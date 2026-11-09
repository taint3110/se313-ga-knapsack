"""Demo chạy trực tiếp trên sân khấu (phần của TV4).

Năm cảnh nối tiếp nhau:
    1. Bài toán  : dữ liệu đầu vào và độ lớn của không gian tìm kiếm
    2. Mã hoá    : một nhiễm sắc thể trông như thế nào, giải mã ra sao
    3. Tiến hoá  : chạy GA, in từng mốc thế hệ kèm thanh tiến trình
    4. Nghiệm    : lời giải tốt nhất tìm được
    5. Đối chứng : so với quy hoạch động, tham lam, leo đồi và ngẫu nhiên

Cách chạy:
    python demo.py                      # mặc định, bài n = 100
    python demo.py --slow               # chậm lại, hợp để quay video
    python demo.py --instance kp_small  # bài n = 20, có cả vét cạn
    python demo.py --pop 20 --gens 40   # cố ý để tham số kém, cho thấy hội tụ sớm
    python demo.py --no-pause           # không chờ Enter, chạy một mạch
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ga.algorithm import GAConfig, GenStats, run_ga                    # noqa: E402
from ga.baselines import (                                             # noqa: E402
    brute_force,
    dp_exact,
    gap_percent,
    greedy_ratio,
    hill_climbing,
    random_search,
)
from ga.problem import KnapsackInstance, evaluate, make_instance       # noqa: E402

INSTANCES = {
    "kp_small": dict(n=20, seed=1, kind="strongly_correlated"),
    "kp_main": dict(n=100, seed=7, kind="strongly_correlated"),
    "kp_easy": dict(n=100, seed=7, kind="uncorrelated"),
    "kp_large": dict(n=500, seed=13, kind="strongly_correlated"),
}

WIDTH = 74

# Mã màu ANSI. Trên Windows cần gọi os.system("") một lần để bật chế độ này.
if os.name == "nt":
    os.system("")
BOLD = "\033[1m"
DIM = "\033[2m"
BLUE = "\033[38;5;33m"
ORANGE = "\033[38;5;208m"
GREEN = "\033[38;5;35m"
RESET = "\033[0m"


def rule(char: str = "─") -> None:
    print(DIM + char * WIDTH + RESET)


def scene(no: int, title: str) -> None:
    print()
    rule("━")
    print(f"{BOLD}  CẢNH {no}. {title}{RESET}")
    rule("━")


def pause(enabled: bool, note: str = "Nhấn Enter để sang cảnh tiếp theo") -> None:
    if not enabled:
        return
    try:
        input(f"\n{DIM}   {note}{RESET}")
    except EOFError:
        pass


def bar(fraction: float, width: int = 32) -> str:
    filled = max(0, min(width, round(fraction * width)))
    return "█" * filled + DIM + "·" * (width - filled) + RESET


# ---------------------------------------------------------------------------

def scene_problem(inst: KnapsackInstance, pause_on: bool) -> None:
    scene(1, "BÀI TOÁN CÁI TÚI 0/1")
    print(f"  Có {inst.n} món đồ, mỗi món có giá trị và trọng lượng riêng.")
    print(f"  Chiếc túi chịu được tối đa {BOLD}{inst.capacity}{RESET} đơn vị trọng lượng,")
    print(f"  trong khi tổng trọng lượng tất cả các món là {inst.total_weight}.")
    print("  Mục tiêu: chọn tập món có tổng giá trị lớn nhất mà vẫn vừa túi.")
    print()
    print(f"  {DIM}Lớp dữ liệu: {inst.kind}{RESET}")
    if inst.kind == "strongly_correlated":
        print(f"  {DIM}(giá trị = trọng lượng + 10, nên mọi món đáng giá gần như nhau,")
        print(f"   đây là lớp dữ liệu khó nhất với các thuật toán tham lam){RESET}")
    print()
    print(f"  {BOLD}10 món đầu tiên{RESET}")
    print(f"  {'Món':>5} {'Giá trị':>9} {'Trọng lượng':>12} {'Mật độ':>9}")
    for i in range(min(10, inst.n)):
        print(f"  {i:>5} {inst.values[i]:>9} {inst.weights[i]:>12} "
              f"{inst.ratio(i):>9.2f}")
    if inst.n > 10:
        print(f"  {DIM}... còn {inst.n - 10} món nữa{RESET}")
    print()
    space = f"2^{inst.n}"
    print(f"  Số phương án phải xét nếu vét cạn: {BOLD}{space} "
          f"= {2 ** inst.n:.3e}{RESET}")
    if inst.n >= 60:
        years = 2 ** inst.n / 1e9 / 3.15e7
        print(f"  Máy xét được một tỉ phương án mỗi giây thì vẫn cần "
              f"{BOLD}{years:.1e} năm{RESET}.")
    pause(pause_on)


def scene_encoding(inst: KnapsackInstance, pause_on: bool) -> None:
    import random

    scene(2, "MÃ HOÁ MỘT LỜI GIẢI THÀNH NHIỄM SẮC THỂ")
    rng = random.Random(42)
    genes = [rng.randint(0, 1) for _ in range(inst.n)]
    shown = "".join(str(g) for g in genes[:40])
    print(f"  Mỗi lời giải là một chuỗi {inst.n} bit, bit thứ i bằng 1 nghĩa là mang món i.")
    print()
    print(f"  {BLUE}{shown}{'...' if inst.n > 40 else ''}{RESET}")
    print()
    ev_raw_weight = sum(w for g, w in zip(genes, inst.weights) if g)
    ev = evaluate(inst, genes, "repair")
    print(f"  Giải mã: chọn {sum(genes)} món, tổng trọng lượng {ev_raw_weight} "
          f"so với sức chứa {inst.capacity}.")
    if ev_raw_weight > inst.capacity:
        print(f"  {ORANGE}Quá tải, phải sửa chữa: bỏ dần món có mật độ giá trị thấp nhất"
              f"{RESET}")
        print(f"  Sau sửa chữa còn {sum(ev.genes)} món, trọng lượng {ev.weight}, "
              f"giá trị {BOLD}{ev.value}{RESET}.")
    else:
        print(f"  Vừa túi, giá trị {BOLD}{ev.value}{RESET}.")
    print()
    print(f"  {DIM}Fitness của một cá thể chính là tổng giá trị sau khi giải mã.{RESET}")
    pause(pause_on)


def scene_evolution(
    inst: KnapsackInstance, cfg: GAConfig, optimum: int, slow: float, pause_on: bool
):
    scene(3, "CHO QUẦN THỂ TIẾN HOÁ")
    print(f"  Quần thể {cfg.pop_size} cá thể, {cfg.generations} thế hệ, "
          f"chọn lọc {cfg.selection} (k = {cfg.tournament_k}),")
    print(f"  lai ghép {cfg.crossover} với xác suất {cfg.p_crossover:.0%}, "
          f"đột biến {cfg.mutation_rate(inst.n):.4f} mỗi gene,")
    print(f"  giữ {cfg.elitism} cá thể tinh hoa, seed = {cfg.seed}.")
    print()
    print(f"  {'Thế hệ':>7} {'Tốt nhất':>10} {'TB quần thể':>12} {'Đa dạng':>8}  "
          f"{'Tiến trình tới nghiệm tối ưu':<32}")
    rule()

    step = max(1, cfg.generations // 15)
    lo = {"v": None}

    def on_gen(stats: GenStats, _best) -> None:
        if lo["v"] is None:
            lo["v"] = stats.best_value
        if stats.generation % step and stats.generation != cfg.generations:
            return
        frac = (stats.best_value - lo["v"]) / max(1, optimum - lo["v"])
        print(f"  {stats.generation:>7} {stats.best_value:>10} "
              f"{stats.mean_fitness:>12.1f} {stats.diversity:>8.3f}  "
              f"{bar(frac)}")
        if slow:
            time.sleep(slow)

    res = run_ga(inst, cfg, on_generation=on_gen)
    rule()
    print(f"  Chạy xong {res.generations_run} thế hệ trong "
          f"{BOLD}{res.runtime:.2f} giây{RESET}, "
          f"gọi hàm fitness {res.evaluations} lần.")
    print(f"  Lần cải thiện cuối cùng rơi vào thế hệ {res.gen_to_best}.")
    pause(pause_on)
    return res


def scene_solution(inst: KnapsackInstance, res, pause_on: bool) -> None:
    scene(4, "LỜI GIẢI TỐT NHẤT TÌM ĐƯỢC")
    items = res.items
    print(f"  Mang theo {BOLD}{len(items)}/{inst.n} món{RESET}, "
          f"tổng trọng lượng {BOLD}{res.best_weight}/{inst.capacity}{RESET} "
          f"({100 * res.best_weight / inst.capacity:.1f}% sức chứa),")
    print(f"  tổng giá trị {BOLD}{GREEN}{res.best_value}{RESET}.")
    print()
    preview = ", ".join(str(i) for i in items[:25])
    print(f"  Các món được chọn: {preview}" + (" ..." if len(items) > 25 else ""))
    print()
    print(f"  {DIM}Nhiễm sắc thể tương ứng (40 bit đầu):{RESET}")
    print(f"  {BLUE}{''.join(str(g) for g in res.best_genes[:40])}"
          f"{'...' if inst.n > 40 else ''}{RESET}")
    pause(pause_on)


def scene_compare(
    inst: KnapsackInstance, res, dp, budget: int, seed: int, pause_on: bool
) -> None:
    scene(5, "ĐỐI CHỨNG VỚI CÁC THUẬT TOÁN KHÁC")
    optimum = dp.value
    print(f"  Mọi thuật toán ngẫu nhiên dưới đây dùng chung ngân sách "
          f"{budget} lần gọi fitness.")
    print()
    rows = [("GA (di truyền)", res.best_value, res.runtime, True)]

    gr = greedy_ratio(inst)
    rows.append(("Tham lam theo mật độ", gr.value, gr.runtime, False))

    hc = hill_climbing(inst, budget, seed)
    rows.append(("Leo đồi lật bit", hc.value, hc.runtime, False))

    rs = random_search(inst, budget, seed)
    rows.append(("Tìm kiếm ngẫu nhiên", rs.value, rs.runtime, False))

    if inst.n <= 20:
        bf = brute_force(inst)
        rows.append(("Vét cạn 2^n", bf.value, bf.runtime, False))

    print(f"  {'Thuật toán':<24}{'Giá trị':>9}{'Lệch tối ưu':>13}{'Thời gian':>12}")
    rule()
    for name, value, runtime, is_ga in rows:
        gap = gap_percent(value, optimum)
        colour = BLUE if is_ga else ""
        reset = RESET if is_ga else ""
        print(f"  {colour}{name:<24}{value:>9}{gap:>12.2f}%{runtime:>11.3f}s{reset}")
    rule()
    print(f"  {'Quy hoạch động (tối ưu)':<24}{optimum:>9}{0.0:>12.2f}%"
          f"{dp.runtime:>11.3f}s")
    print()

    best_other = max(v for name, v, _, is_ga in rows if not is_ga)
    if res.best_value > best_other:
        print(f"  {GREEN}GA cho nghiệm tốt nhất trong nhóm các thuật toán xấp xỉ."
              f"{RESET}")
    elif res.best_value == best_other:
        print("  GA ngang bằng thuật toán xấp xỉ tốt nhất còn lại.")
    else:
        print(f"  {ORANGE}Ở cấu hình này GA chưa vượt được đối thủ tốt nhất, "
              f"cần thêm ngân sách thế hệ.{RESET}")
    print(f"  Quy hoạch động cho nghiệm tối ưu tuyệt đối nhưng cần bảng "
          f"{inst.n} x {inst.capacity + 1} ô nhớ")
    print("  và chỉ dùng được khi trọng lượng là số nguyên nhỏ. GA không cần "
          "hai điều kiện đó.")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Demo GA cho bài toán cái túi 0/1")
    parser.add_argument("--instance", default="kp_main", choices=sorted(INSTANCES))
    parser.add_argument("--pop", type=int, default=60)
    parser.add_argument("--gens", type=int, default=150)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--mutation-scale", type=float, default=1.0,
                        help="bội số của tỉ lệ đột biến chuẩn 1/n")
    parser.add_argument("--elitism", type=int, default=2)
    parser.add_argument("--selection", default="tournament",
                        choices=("tournament", "roulette", "rank"))
    parser.add_argument("--crossover", default="one_point",
                        choices=("one_point", "two_point", "uniform"))
    parser.add_argument("--slow", action="store_true",
                        help="chậm lại 0.18 giây mỗi mốc, hợp để quay video")
    parser.add_argument("--no-pause", action="store_true",
                        help="không dừng chờ Enter giữa các cảnh")
    args = parser.parse_args(argv)

    spec = INSTANCES[args.instance]
    inst = make_instance(spec["n"], seed=spec["seed"], kind=spec["kind"],
                         name=args.instance)
    cfg = GAConfig(
        pop_size=args.pop,
        generations=args.gens,
        selection=args.selection,
        crossover=args.crossover,
        mutation_scale=args.mutation_scale,
        elitism=args.elitism,
        seed=args.seed,
        label="demo",
    )
    dp = dp_exact(inst)
    optimum = dp.value
    budget = cfg.pop_size * (cfg.generations + 1)
    pause_on = not args.no_pause
    slow = 0.18 if args.slow else 0.0

    print()
    print(f"{BOLD}  GIẢI THUẬT TIẾN HOÁ VÀ ỨNG DỤNG{RESET}")
    print("  Demo: giải bài toán Cái túi 0/1 bằng giải thuật di truyền")
    print(f"  {DIM}Môn SE313 - Một số thuật toán thông minh{RESET}")

    scene_problem(inst, pause_on)
    scene_encoding(inst, pause_on)
    res = scene_evolution(inst, cfg, optimum, slow, pause_on)
    scene_solution(inst, res, pause_on)
    scene_compare(inst, res, dp, budget, cfg.seed, pause_on)
    print()
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main())
