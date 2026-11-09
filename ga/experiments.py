"""Chạy toàn bộ thí nghiệm và xuất dữ liệu thô ra CSV (yêu cầu 5).

Mỗi thí nghiệm lặp lại trên nhiều hạt giống ngẫu nhiên (seed) khác nhau vì GA
là thuật toán ngẫu nhiên: một lần chạy đẹp không chứng minh được điều gì, phải
báo cáo trung bình và độ lệch chuẩn.

Cách chạy:
    python -m ga.experiments              # đầy đủ, khoảng 5 tới 8 phút
    python -m ga.experiments --quick      # bản rút gọn để thử, dưới 1 phút
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from .algorithm import GAConfig, run_ga
from .baselines import (
    brute_force,
    dp_exact,
    gap_percent,
    greedy_ratio,
    hill_climbing,
    random_search,
)
from .problem import KnapsackInstance, make_instance

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"

# Cấu hình nền, mọi thí nghiệm tham số đều đổi đúng một thứ so với cấu hình này.
BASE = GAConfig(
    pop_size=60,
    generations=150,
    selection="tournament",
    tournament_k=3,
    crossover="one_point",
    p_crossover=0.9,
    p_mutation=None,        # tức 1/n
    elitism=2,
    repair_mode="repair",
    label="base",
)
# Ngân sách đánh giá fitness của cấu hình nền, dùng cho mọi đối thủ so sánh.
BUDGET = BASE.pop_size * (BASE.generations + 1)


def build_instances() -> Dict[str, KnapsackInstance]:
    """Bốn bộ dữ liệu dùng xuyên suốt báo cáo."""
    return {
        # n nhỏ để vét cạn kiểm chứng được
        "kp_small": make_instance(20, seed=1, kind="strongly_correlated",
                                  name="kp_small"),
        # bài chính của nhóm
        "kp_main": make_instance(100, seed=7, kind="strongly_correlated",
                                 name="kp_main"),
        # cùng cỡ nhưng dữ liệu không tương quan, để thấy tham lam mạnh hay yếu
        # là do cấu trúc dữ liệu chứ không phải do thuật toán
        "kp_easy": make_instance(100, seed=7, kind="uncorrelated",
                                 name="kp_easy"),
        # bài lớn để nói về khả năng mở rộng
        "kp_large": make_instance(500, seed=13, kind="strongly_correlated",
                                  name="kp_large"),
    }


def _rel(path: Path) -> str:
    """Đường dẫn gọn cho dễ đọc khi in ra màn hình."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def write_csv(path: Path, rows: Sequence[dict], fieldnames: Sequence[str] | None = None) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(fieldnames or rows[0].keys())
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  -> {_rel(path)}  ({len(rows)} dòng)")


def aggregate(
    rows: Sequence[dict],
    group_keys: Sequence[str],
    metrics: Sequence[str],
) -> List[dict]:
    """Gom các lần chạy cùng cấu hình lại thành trung bình, độ lệch chuẩn, min, max.

    Đây chính là bảng mà TV5 dùng để vẽ biểu đồ cột có thanh sai số.
    """
    buckets: Dict[tuple, List[dict]] = {}
    for row in rows:
        key = tuple(row[k] for k in group_keys)
        buckets.setdefault(key, []).append(row)

    out: List[dict] = []
    for key, items in buckets.items():
        rec = dict(zip(group_keys, key))
        rec["runs"] = len(items)
        for m in metrics:
            vals = [float(it[m]) for it in items]
            rec[f"{m}_mean"] = round(statistics.fmean(vals), 4)
            rec[f"{m}_std"] = round(statistics.pstdev(vals), 4) if len(vals) > 1 else 0.0
            rec[f"{m}_min"] = round(min(vals), 4)
            rec[f"{m}_max"] = round(max(vals), 4)
        hits = [it for it in items if int(it.get("hit_optimum", 0)) == 1]
        rec["success_rate"] = round(100.0 * len(hits) / len(items), 2)
        out.append(rec)
    return out


# ---------------------------------------------------------------------------
# Thí nghiệm 1: đường hội tụ
# ---------------------------------------------------------------------------

def exp_convergence(inst: KnapsackInstance, optimum: int, seeds: Iterable[int]) -> List[dict]:
    """Ghi lại từng thế hệ của từng lần chạy, phục vụ biểu đồ hội tụ."""
    rows: List[dict] = []
    for seed in seeds:
        cfg = GAConfig(**{**BASE.as_row(), "seed": seed, "label": "base"})
        res = run_ga(inst, cfg)
        for h in res.history:
            rows.append(
                {
                    "instance": inst.name,
                    "config": cfg.label,
                    "seed": seed,
                    "generation": h.generation,
                    "best_value": h.best_value,
                    "best_fitness": round(h.best_fitness, 2),
                    "mean_fitness": round(h.mean_fitness, 2),
                    "worst_fitness": round(h.worst_fitness, 2),
                    "std_fitness": round(h.std_fitness, 2),
                    "best_weight": h.best_weight,
                    "diversity": round(h.diversity, 4),
                    "unique": h.unique,
                    "evaluations": h.evaluations,
                    "elapsed": round(h.elapsed, 4),
                    "optimum": optimum,
                    "gap_percent": round(gap_percent(h.best_value, optimum), 4),
                }
            )
    return rows


# ---------------------------------------------------------------------------
# Thí nghiệm 2: GA so với các thuật toán khác
# ---------------------------------------------------------------------------

def exp_baselines(
    instances: Dict[str, KnapsackInstance],
    optima: Dict[str, int],
    seeds: Sequence[int],
) -> List[dict]:
    """So sánh GA với tham lam, leo đồi, ngẫu nhiên và quy hoạch động.

    GA, leo đồi và ngẫu nhiên dùng chung ngân sách BUDGET lần gọi fitness.
    """
    rows: List[dict] = []
    for key, inst in instances.items():
        opt = optima[key]

        dp = dp_exact(inst)
        rows.append(_row(inst, "dp_exact", dp.value, dp.weight, dp.runtime,
                         dp.evaluations, opt, deterministic=True))

        gr = greedy_ratio(inst)
        rows.append(_row(inst, "greedy", gr.value, gr.weight, gr.runtime,
                         gr.evaluations, opt, deterministic=True))

        if inst.n <= 20:
            bf = brute_force(inst)
            rows.append(_row(inst, "brute_force", bf.value, bf.weight, bf.runtime,
                             bf.evaluations, opt, deterministic=True))

        for seed in seeds:
            cfg = GAConfig(**{**BASE.as_row(), "seed": seed})
            ga = run_ga(inst, cfg)
            rows.append(_row(inst, "ga", ga.best_value, ga.best_weight, ga.runtime,
                             ga.evaluations, opt, seed=seed,
                             gen_to_best=ga.gen_to_best))

            hc = hill_climbing(inst, BUDGET, seed)
            rows.append(_row(inst, "hill_climbing", hc.value, hc.weight, hc.runtime,
                             hc.evaluations, opt, seed=seed))

            rs = random_search(inst, BUDGET, seed)
            rows.append(_row(inst, "random", rs.value, rs.weight, rs.runtime,
                             rs.evaluations, opt, seed=seed))
    return rows


def _row(
    inst: KnapsackInstance,
    method: str,
    value: int,
    weight: int,
    runtime: float,
    evaluations: int,
    optimum: int,
    seed: int | str = "-",
    deterministic: bool = False,
    gen_to_best: int | str = "-",
) -> dict:
    return {
        "instance": inst.name,
        "kind": inst.kind,
        "n": inst.n,
        "capacity": inst.capacity,
        "method": method,
        "seed": "det" if deterministic else seed,
        "best_value": value,
        "weight": weight,
        "optimum": optimum,
        "gap_percent": round(gap_percent(value, optimum), 4),
        "hit_optimum": int(value >= optimum),
        "evaluations": evaluations,
        "runtime_sec": round(runtime, 5),
        "gen_to_best": gen_to_best,
    }


# ---------------------------------------------------------------------------
# Thí nghiệm 3: ảnh hưởng của từng tham số
# ---------------------------------------------------------------------------

def _param_run(
    inst: KnapsackInstance,
    optimum: int,
    experiment: str,
    param_value,
    overrides: dict,
    seed: int,
) -> dict:
    cfg = GAConfig(**{**BASE.as_row(), **overrides, "seed": seed})
    res = run_ga(inst, cfg)
    return {
        "experiment": experiment,
        "param_value": param_value,
        "instance": inst.name,
        "seed": seed,
        "best_value": res.best_value,
        "optimum": optimum,
        "gap_percent": round(gap_percent(res.best_value, optimum), 4),
        "hit_optimum": int(res.best_value >= optimum),
        "gen_to_best": res.gen_to_best,
        "generations_run": res.generations_run,
        "evaluations": res.evaluations,
        "runtime_sec": round(res.runtime, 5),
        "final_diversity": round(res.history[-1].diversity, 4),
        "pop_size": cfg.pop_size,
        "generations": cfg.generations,
        "p_mutation": round(cfg.mutation_rate(inst.n), 5),
        "p_crossover": cfg.p_crossover,
        "selection": cfg.selection,
        "tournament_k": cfg.tournament_k,
        "crossover": cfg.crossover,
        "elitism": cfg.elitism,
        "repair_mode": cfg.repair_mode,
        "penalty_coef": cfg.penalty_coef,
    }


def exp_parameters(
    inst: KnapsackInstance, optimum: int, seeds: Sequence[int]
) -> List[dict]:
    """Quét từng tham số một, giữ nguyên mọi tham số còn lại."""
    rows: List[dict] = []

    # 3a. Kích thước quần thể, giữ nguyên tổng ngân sách đánh giá để so sánh
    #     công bằng: quần thể lớn thì số thế hệ phải giảm tương ứng.
    for pop in (10, 20, 40, 60, 100, 200):
        gens = max(1, BUDGET // pop - 1)
        for seed in seeds:
            rows.append(_param_run(inst, optimum, "pop_size", pop,
                                   {"pop_size": pop, "generations": gens,
                                    "label": f"pop{pop}"}, seed))

    # 3b. Tỉ lệ đột biến, tính theo bội số của mức chuẩn 1/n
    for scale in (0.0, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0):
        for seed in seeds:
            rows.append(_param_run(inst, optimum, "mutation_scale", scale,
                                   {"mutation_scale": scale,
                                    "label": f"mut{scale}x"}, seed))

    # 3c. Xác suất lai ghép
    for pc in (0.0, 0.3, 0.6, 0.9, 1.0):
        for seed in seeds:
            rows.append(_param_run(inst, optimum, "p_crossover", pc,
                                   {"p_crossover": pc, "label": f"pc{pc}"}, seed))

    # 3d. Kiểu lai ghép
    for kind in ("one_point", "two_point", "uniform"):
        for seed in seeds:
            rows.append(_param_run(inst, optimum, "crossover", kind,
                                   {"crossover": kind, "label": kind}, seed))

    # 3e. Phương pháp chọn lọc
    for name, over in (
        ("tournament_k2", {"selection": "tournament", "tournament_k": 2}),
        ("tournament_k3", {"selection": "tournament", "tournament_k": 3}),
        ("tournament_k5", {"selection": "tournament", "tournament_k": 5}),
        ("tournament_k10", {"selection": "tournament", "tournament_k": 10}),
        ("roulette", {"selection": "roulette"}),
        ("rank", {"selection": "rank"}),
    ):
        for seed in seeds:
            rows.append(_param_run(inst, optimum, "selection", name,
                                   {**over, "label": name}, seed))

    # 3f. Số cá thể tinh hoa
    for e in (0, 1, 2, 5, 10):
        for seed in seeds:
            rows.append(_param_run(inst, optimum, "elitism", e,
                                   {"elitism": e, "label": f"elite{e}"}, seed))

    # 3g. Cách xử lý ràng buộc: sửa chữa hay phạt điểm
    for name, over in (
        ("repair", {"repair_mode": "repair"}),
        ("penalty_0.5", {"repair_mode": "penalty", "penalty_coef": 0.5}),
        ("penalty_2", {"repair_mode": "penalty", "penalty_coef": 2.0}),
        ("penalty_10", {"repair_mode": "penalty", "penalty_coef": 10.0}),
    ):
        for seed in seeds:
            rows.append(_param_run(inst, optimum, "constraint", name,
                                   {**over, "label": name}, seed))

    return rows


# ---------------------------------------------------------------------------
# Thí nghiệm 4: cấu hình nền so với cấu hình đã tinh chỉnh
# ---------------------------------------------------------------------------

# Cách tinh chỉnh thứ nhất: lấy giá trị tốt nhất của từng tham số trong bảng
# quét rồi ghép cơ học lại với nhau. Nghe hợp lý nhưng kết quả lại tệ đi, vì
# các tham số tương tác với nhau: quần thể 200 chỉ còn 44 thế hệ, mà tỉ lệ đột
# biến gấp đôi lại cần nhiều thế hệ hơn mới kịp khai thác.
TUNED_NAIVE = GAConfig(
    pop_size=200,
    generations=44,
    selection="tournament",
    tournament_k=2,
    crossover="uniform",
    p_crossover=1.0,
    mutation_scale=2.0,
    elitism=1,
    repair_mode="repair",
    label="tuned_naive",
)

# Cách thứ hai: thử theo tổ hợp thay vì cộng dồn từng tham số. Đây là tổ hợp
# tốt nhất tìm được, vẫn giữ nguyên ngân sách khoảng 9060 lần đánh giá.
TUNED = GAConfig(
    pop_size=100,
    generations=89,
    selection="tournament",
    tournament_k=2,
    crossover="uniform",
    p_crossover=1.0,
    mutation_scale=1.0,
    elitism=1,
    repair_mode="repair",
    label="tuned",
)


def exp_tuned(
    instances: Dict[str, KnapsackInstance],
    optima: Dict[str, int],
    keys: Sequence[str],
    seeds: Sequence[int],
) -> List[dict]:
    """So sánh ba cấu hình: nền, ghép cơ học, và tổ hợp tìm được.

    Cả ba dùng cùng một ngân sách đánh giá nên chênh lệch kết quả đúng là do
    tham số chứ không do cấu hình nào được chạy nhiều hơn.
    """
    rows: List[dict] = []
    for key in keys:
        inst = instances[key]
        opt = optima[key]
        greedy_value = greedy_ratio(inst).value
        for label, cfg_base in (("base", BASE), ("tuned_naive", TUNED_NAIVE),
                                ("tuned", TUNED)):
            for seed in seeds:
                cfg = GAConfig(**{**cfg_base.as_row(), "seed": seed})
                res = run_ga(inst, cfg)
                rows.append(
                    {
                        "instance": inst.name,
                        "n": inst.n,
                        "config": label,
                        "seed": seed,
                        "pop_size": cfg.pop_size,
                        "generations": cfg.generations,
                        "selection": f"{cfg.selection}_k{cfg.tournament_k}",
                        "crossover": cfg.crossover,
                        "p_crossover": cfg.p_crossover,
                        "mutation_scale": cfg.mutation_scale,
                        "elitism": cfg.elitism,
                        "best_value": res.best_value,
                        "optimum": opt,
                        "gap_percent": round(gap_percent(res.best_value, opt), 4),
                        "hit_optimum": int(res.best_value >= opt),
                        "beats_greedy": int(res.best_value > greedy_value),
                        "gen_to_best": res.gen_to_best,
                        "evaluations": res.evaluations,
                        "runtime_sec": round(res.runtime, 4),
                    }
                )
    return rows


# ---------------------------------------------------------------------------
# Thí nghiệm 5: tăng ngân sách tính toán trên bài lớn
# ---------------------------------------------------------------------------

def exp_budget(
    inst: KnapsackInstance,
    optimum: int,
    budgets: Sequence[int],
    seeds: Sequence[int],
) -> List[dict]:
    """Trên bài n = 500, GA cần bao nhiêu lần đánh giá mới vượt được tham lam.

    Giữ nguyên quần thể 100 cá thể, chỉ kéo dài số thế hệ. Thí nghiệm này trả
    lời thẳng câu hỏi khó nhất của phần kết quả: với ngân sách nhỏ thì tham lam
    thắng GA ở bài lớn, nhưng GA cải thiện dần khi được chạy lâu hơn còn tham
    lam thì mãi mãi đứng yên ở một con số.
    """
    greedy_value = greedy_ratio(inst).value
    pop = 100
    rows: List[dict] = []
    for budget in budgets:
        gens = max(1, budget // pop - 1)
        for seed in seeds:
            cfg = GAConfig(**{**BASE.as_row(), "pop_size": pop, "generations": gens,
                              "seed": seed, "label": f"budget{budget}"})
            res = run_ga(inst, cfg)
            rows.append(
                {
                    "instance": inst.name,
                    "n": inst.n,
                    "budget": budget,
                    "generations": gens,
                    "pop_size": pop,
                    "seed": seed,
                    "best_value": res.best_value,
                    "optimum": optimum,
                    "gap_percent": round(gap_percent(res.best_value, optimum), 4),
                    "hit_optimum": int(res.best_value >= optimum),
                    "greedy_value": greedy_value,
                    "greedy_gap_percent": round(gap_percent(greedy_value, optimum), 4),
                    "beats_greedy": int(res.best_value > greedy_value),
                    "runtime_sec": round(res.runtime, 4),
                    "evaluations": res.evaluations,
                }
            )
    return rows


# ---------------------------------------------------------------------------
# Thí nghiệm 6: khả năng mở rộng theo kích thước bài toán
# ---------------------------------------------------------------------------

def exp_scalability(sizes: Sequence[int], seeds: Sequence[int]) -> List[dict]:
    """Tăng dần n rồi đo chất lượng và thời gian của GA so với quy hoạch động."""
    rows: List[dict] = []
    for n in sizes:
        inst = make_instance(n, seed=100 + n, kind="strongly_correlated",
                             name=f"kp_scale_n{n}")
        dp = dp_exact(inst)
        gr = greedy_ratio(inst)
        for seed in seeds:
            cfg = GAConfig(**{**BASE.as_row(), "seed": seed})
            res = run_ga(inst, cfg)
            rows.append(
                {
                    "n": n,
                    "instance": inst.name,
                    "capacity": inst.capacity,
                    "seed": seed,
                    "search_space_log10": round(n * 0.30103, 2),
                    "ga_value": res.best_value,
                    "ga_gap_percent": round(gap_percent(res.best_value, dp.value), 4),
                    "hit_optimum": int(res.best_value >= dp.value),
                    "ga_runtime_sec": round(res.runtime, 5),
                    "ga_evaluations": res.evaluations,
                    "dp_value": dp.value,
                    "dp_runtime_sec": round(dp.runtime, 5),
                    "dp_states": dp.evaluations,
                    "greedy_value": gr.value,
                    "greedy_gap_percent": round(gap_percent(gr.value, dp.value), 4),
                    "greedy_runtime_sec": round(gr.runtime, 6),
                }
            )
    return rows


# ---------------------------------------------------------------------------

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chạy thí nghiệm GA cho bài cái túi")
    parser.add_argument("--quick", action="store_true",
                        help="chỉ 5 seed, dùng để thử nhanh")
    parser.add_argument("--seeds", type=int, default=30,
                        help="số lần lặp lại mỗi cấu hình (mặc định 30)")
    parser.add_argument("--out", default=str(RESULTS_DIR), help="thư mục xuất CSV")
    args = parser.parse_args(argv)

    n_seeds = 5 if args.quick else args.seeds
    seeds = list(range(1, n_seeds + 1))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    t_start = time.perf_counter()
    instances = build_instances()
    for key, inst in instances.items():
        inst.to_json(DATA_DIR / f"{key}.json")
    print(f"Đã ghi {len(instances)} bộ dữ liệu vào {_rel(DATA_DIR)}/")

    print("\nTìm nghiệm tối ưu bằng quy hoạch động để làm mốc so sánh")
    optima: Dict[str, int] = {}
    for key, inst in instances.items():
        dp = dp_exact(inst)
        optima[key] = dp.value
        print(f"  {inst.describe()}")
        print(f"    tối ưu = {dp.value} (quy hoạch động, {dp.runtime * 1000:.1f} ms)")

    main_inst = instances["kp_main"]
    main_opt = optima["kp_main"]

    print(f"\n[1/6] Đường hội tụ trên {main_inst.name}, {n_seeds} lần chạy")
    write_csv(out / "convergence.csv", exp_convergence(main_inst, main_opt, seeds))

    print(f"\n[2/6] So sánh GA với các thuật toán khác (ngân sách {BUDGET} lần đánh giá)")
    base_rows = exp_baselines(instances, optima, seeds)
    write_csv(out / "baselines.csv", base_rows)
    write_csv(
        out / "summary_baselines.csv",
        aggregate(base_rows, ["instance", "kind", "n", "method"],
                  ["best_value", "gap_percent", "runtime_sec", "evaluations"]),
    )

    print(f"\n[3/6] Quét tham số trên {main_inst.name}")
    param_rows = exp_parameters(main_inst, main_opt, seeds)
    write_csv(out / "params.csv", param_rows)
    write_csv(
        out / "summary_params.csv",
        aggregate(param_rows, ["experiment", "param_value"],
                  ["best_value", "gap_percent", "gen_to_best", "runtime_sec",
                   "final_diversity"]),
    )

    print("\n[4/6] Cấu hình nền so với cấu hình tinh chỉnh")
    tuned_rows = exp_tuned(instances, optima, ("kp_main", "kp_large"), seeds)
    write_csv(out / "tuned.csv", tuned_rows)
    write_csv(
        out / "summary_tuned.csv",
        aggregate(tuned_rows, ["instance", "n", "config"],
                  ["best_value", "gap_percent", "gen_to_best", "runtime_sec",
                   "beats_greedy"]),
    )

    print("\n[5/6] Tăng ngân sách tính toán trên kp_large")
    budgets = (9000, 30000, 100000) if args.quick else (9000, 30000, 100000, 300000)
    budget_rows = exp_budget(instances["kp_large"], optima["kp_large"], budgets,
                             seeds[: min(len(seeds), 5)])
    write_csv(out / "budget.csv", budget_rows)
    write_csv(
        out / "summary_budget.csv",
        aggregate(budget_rows, ["n", "budget", "generations"],
                  ["best_value", "gap_percent", "runtime_sec", "beats_greedy"]),
    )

    print("\n[6/6] Khả năng mở rộng theo n")
    sizes = (20, 50, 100, 200, 500) if args.quick else (20, 50, 100, 200, 500, 1000)
    scale_rows = exp_scalability(sizes, seeds[: min(len(seeds), 10)])
    write_csv(out / "scalability.csv", scale_rows)
    write_csv(
        out / "summary_scalability.csv",
        aggregate(scale_rows, ["n"],
                  ["ga_value", "ga_gap_percent", "ga_runtime_sec", "dp_value",
                   "dp_runtime_sec", "greedy_gap_percent"]),
    )

    meta = {
        "seeds": n_seeds,
        "budget_evaluations": BUDGET,
        "base_config": BASE.as_row(),
        "tuned_naive_config": TUNED_NAIVE.as_row(),
        "tuned_config": TUNED.as_row(),
        "optima": optima,
        "instances": {k: v.describe() for k, v in instances.items()},
        "total_runtime_sec": round(time.perf_counter() - t_start, 2),
    }
    (out / "run_meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nXong sau {meta['total_runtime_sec']:.1f} giây. "
          f"Dữ liệu nằm trong {_rel(out)}/")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main())
