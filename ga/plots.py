"""Vẽ biểu đồ từ các file CSV do ga.experiments sinh ra.

Chạy sau khi đã có dữ liệu:
    python -m ga.plots

Mỗi hàm vẽ một hình và in ra đúng tên file CSV cùng các cột đã dùng, để phần
báo cáo trích dẫn được nguồn số liệu của từng biểu đồ.

Quy ước trình bày
-----------------
- Một hình chỉ dùng một trục giá trị. Khi cần hai đại lượng khác đơn vị thì
  tách thành hai khung vẽ cạnh nhau, không bao giờ dùng hai trục tung chồng lên
  nhau vì người đọc sẽ hiểu sai tương quan.
- Bảng màu cố định theo thứ tự, mỗi phương pháp giữ nguyên một màu ở mọi hình.
- Lưới mờ, viền mỏng, nhãn trực tiếp ở chỗ cần nhấn.
"""

from __future__ import annotations

import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures"

# Bảng màu phân loại, dùng theo đúng thứ tự slot, không bao giờ xoay vòng.
C_BLUE = "#2a78d6"
C_ORANGE = "#eb6834"
C_AQUA = "#1baf7a"
C_YELLOW = "#eda100"
C_MAGENTA = "#e87ba4"
C_VIOLET = "#4a3aa7"
C_GRAY = "#8a8a85"

INK = "#0b0b0b"
INK_SOFT = "#52514e"
GRID = "#dedcd6"

# Mỗi phương pháp một màu cố định xuyên suốt báo cáo.
METHOD_COLOR = {
    "ga": C_BLUE,
    "greedy": C_ORANGE,
    "hill_climbing": C_AQUA,
    "random": C_MAGENTA,
    "dp_exact": INK_SOFT,
    "brute_force": C_VIOLET,
}
METHOD_LABEL = {
    "ga": "GA (di truyền)",
    "greedy": "Tham lam",
    "hill_climbing": "Leo đồi",
    "random": "Ngẫu nhiên",
    "dp_exact": "Quy hoạch động (tối ưu)",
    "brute_force": "Vét cạn",
}

plt.rcParams.update(
    {
        "figure.dpi": 150,
        "savefig.dpi": 150,
        "figure.facecolor": "#ffffff",
        "axes.facecolor": "#ffffff",
        "axes.edgecolor": GRID,
        "axes.linewidth": 0.8,
        "axes.labelcolor": INK_SOFT,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.titlecolor": INK,
        "axes.grid": True,
        "axes.axisbelow": True,     # lưới nằm dưới cột, không cắt ngang qua cột
        "grid.color": GRID,
        "grid.linewidth": 0.7,
        "grid.alpha": 0.9,
        "xtick.color": INK_SOFT,
        "ytick.color": INK_SOFT,
        "font.size": 9,
        "legend.frameon": False,
        "legend.fontsize": 8.5,
        "lines.linewidth": 2.0,
    }
)


# ---------------------------------------------------------------------------

def read_csv(name: str) -> List[dict]:
    path = RESULTS / name
    if not path.exists():
        raise SystemExit(
            f"Chưa có {path.name}. Hãy chạy `python -m ga.experiments` trước."
        )
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _f(row: dict, key: str) -> float:
    return float(row[key])


def group_mean(
    rows: Sequence[dict], key: str, value: str
) -> Dict[str, List[float]]:
    buckets: Dict[str, List[float]] = defaultdict(list)
    for r in rows:
        buckets[r[key]].append(_f(r, value))
    return buckets


def _finish(fig, path: Path, source: str, columns: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {path.name}")
    print(f"     nguồn: {source} | cột: {columns}")


def _pct(ax) -> None:
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}%"))


def _err(ys: Sequence[float], errs: Sequence[float]) -> List[List[float]]:
    """Thanh sai số bất đối xứng, cụt lại ở mốc 0.

    Khoảng cách tới tối ưu không thể âm, để thanh sai số thò xuống dưới 0 là
    vẽ ra một vùng giá trị không tồn tại.
    """
    return [[min(e, y) for y, e in zip(ys, errs)], list(errs)]


def _bar_labels(ax, bars, fmt="{:.2f}", errs: Sequence[float] | None = None) -> None:
    """Dán nhãn số ngay trên đầu cột, vì cột thấp rất khó đọc theo trục.

    Có thanh sai số thì nhãn phải nhảy lên cao hơn đầu thanh, nếu không hai thứ
    chồng lên nhau.
    """
    for i, b in enumerate(bars):
        h = b.get_height()
        top = h + (errs[i] if errs else 0.0)
        ax.annotate(
            fmt.format(h),
            (b.get_x() + b.get_width() / 2, top),
            textcoords="offset points",
            xytext=(0, 3),
            ha="center",
            fontsize=8,
            color=INK_SOFT,
        )


# ---------------------------------------------------------------------------
# Hình 1: đường hội tụ
# ---------------------------------------------------------------------------

def fig_convergence() -> None:
    rows = read_csv("convergence.csv")
    base = read_csv("summary_baselines.csv")
    inst = rows[0]["instance"]
    optimum = _f(rows[0], "optimum")
    greedy = next(
        (_f(r, "best_value_mean") for r in base
         if r["instance"] == inst and r["method"] == "greedy"),
        None,
    )

    gens = sorted({int(r["generation"]) for r in rows})
    by_gen_best: Dict[int, List[float]] = defaultdict(list)
    by_gen_mean: Dict[int, List[float]] = defaultdict(list)
    by_gen_gap: Dict[int, List[float]] = defaultdict(list)
    for r in rows:
        g = int(r["generation"])
        by_gen_best[g].append(_f(r, "best_value"))
        by_gen_mean[g].append(_f(r, "mean_fitness"))
        by_gen_gap[g].append(_f(r, "gap_percent"))

    best_mean = [statistics.fmean(by_gen_best[g]) for g in gens]
    best_lo = [min(by_gen_best[g]) for g in gens]
    best_hi = [max(by_gen_best[g]) for g in gens]
    pop_mean = [statistics.fmean(by_gen_mean[g]) for g in gens]
    gap_mean = [statistics.fmean(by_gen_gap[g]) for g in gens]
    gap_hi = [max(by_gen_gap[g]) for g in gens]
    gap_lo = [min(by_gen_gap[g]) for g in gens]
    runs = len(by_gen_best[gens[0]])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))

    ax1.axhline(optimum, color=INK_SOFT, linestyle="--", linewidth=1.2)
    ax1.annotate(f"Tối ưu (quy hoạch động) = {optimum:.0f}",
                 (gens[-1], optimum), xytext=(-4, 5), textcoords="offset points",
                 ha="right", fontsize=8, color=INK_SOFT)
    if greedy:
        ax1.axhline(greedy, color=C_ORANGE, linestyle=":", linewidth=1.4)
        ax1.annotate(f"Tham lam = {greedy:.0f}", (gens[-1], greedy),
                     xytext=(-4, -12), textcoords="offset points", ha="right",
                     fontsize=8, color=C_ORANGE)
    ax1.fill_between(gens, best_lo, best_hi, color=C_BLUE, alpha=0.15, linewidth=0)
    ax1.plot(gens, best_mean, color=C_BLUE, label="Cá thể tốt nhất (trung bình)")
    ax1.plot(gens, pop_mean, color=C_AQUA, linewidth=1.6,
             label="Trung bình cả quần thể")
    ax1.set_xlabel("Thế hệ")
    ax1.set_ylabel("Tổng giá trị")
    ax1.set_title(f"Hội tụ của GA trên {inst} ({runs} lần chạy)")
    ax1.legend(loc="lower right")

    ax2.fill_between(gens, gap_lo, gap_hi, color=C_BLUE, alpha=0.15, linewidth=0)
    ax2.plot(gens, gap_mean, color=C_BLUE)
    ax2.set_xlabel("Thế hệ")
    ax2.set_ylabel("Khoảng cách tới tối ưu")
    ax2.set_title("Sai lệch so với nghiệm tối ưu giảm dần")
    _pct(ax2)
    ax2.annotate(f"{gap_mean[-1]:.2f}% ở thế hệ {gens[-1]}",
                 (gens[-1], gap_mean[-1]), xytext=(-6, 10),
                 textcoords="offset points", ha="right", fontsize=8.5, color=C_BLUE)

    _finish(fig, FIGURES / "fig1_hoi_tu.png", "convergence.csv",
            "generation, best_value, mean_fitness, gap_percent, optimum")


# ---------------------------------------------------------------------------
# Hình 2: mất đa dạng và hội tụ sớm
# ---------------------------------------------------------------------------

def fig_diversity() -> None:
    rows = read_csv("convergence.csv")
    gens = sorted({int(r["generation"]) for r in rows})
    div: Dict[int, List[float]] = defaultdict(list)
    uni: Dict[int, List[float]] = defaultdict(list)
    for r in rows:
        g = int(r["generation"])
        div[g].append(_f(r, "diversity"))
        uni[g].append(_f(r, "unique"))

    d_mean = [statistics.fmean(div[g]) for g in gens]
    u_mean = [statistics.fmean(uni[g]) for g in gens]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))

    ax1.fill_between(gens, [min(div[g]) for g in gens], [max(div[g]) for g in gens],
                     color=C_ORANGE, alpha=0.15, linewidth=0)
    ax1.plot(gens, d_mean, color=C_ORANGE)
    ax1.set_xlabel("Thế hệ")
    ax1.set_ylabel("Độ đa dạng gene")
    ax1.set_title("Quần thể mất dần đa dạng")
    ax1.set_ylim(0, 1)
    ax1.annotate(f"{d_mean[0]:.2f}", (gens[0], d_mean[0]), xytext=(6, -4),
                 textcoords="offset points", fontsize=8.5, color=C_ORANGE)
    ax1.annotate(f"{d_mean[-1]:.2f}", (gens[-1], d_mean[-1]), xytext=(-6, 8),
                 textcoords="offset points", ha="right", fontsize=8.5, color=C_ORANGE)

    ax2.plot(gens, u_mean, color=C_AQUA)
    ax2.set_xlabel("Thế hệ")
    ax2.set_ylabel("Số cá thể khác nhau")
    ax2.set_title("Số cá thể phân biệt được trong quần thể")

    _finish(fig, FIGURES / "fig2_da_dang.png", "convergence.csv",
            "generation, diversity, unique")


# ---------------------------------------------------------------------------
# Hình 3: GA so với các thuật toán khác
# ---------------------------------------------------------------------------

def fig_methods() -> None:
    """Bốn khung nhỏ, mỗi bộ dữ liệu một trục riêng.

    Không gộp chung một trục được: trên kp_easy thì tìm kiếm ngẫu nhiên lệch tới
    13.9%, nếu để chung thì ba bộ còn lại bị ép bẹp xuống đáy, mất hết chỗ chênh
    lệch đáng quan tâm giữa 0.2% và 1.9%.
    """
    rows = read_csv("summary_baselines.csv")
    order = ["ga", "greedy", "hill_climbing", "random"]
    instances = []
    for r in rows:
        if r["instance"] not in instances:
            instances.append(r["instance"])

    fig, axes = plt.subplots(1, len(instances), figsize=(12, 4.2))
    for ax, inst in zip(axes, instances):
        subset = {r["method"]: r for r in rows if r["instance"] == inst}
        names = [m for m in order if m in subset]
        ys = [_f(subset[m], "gap_percent_mean") for m in names]
        errs = [_f(subset[m], "gap_percent_std") for m in names]
        bars = ax.bar(range(len(names)), ys, 0.64,
                      color=[METHOD_COLOR[m] for m in names],
                      yerr=_err(ys, errs), capsize=3,
                      error_kw={"elinewidth": 0.9, "ecolor": INK_SOFT})
        _bar_labels(ax, bars, errs=errs)
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels([METHOD_LABEL[m].split(" (")[0] for m in names],
                           rotation=20, ha="right")
        head = subset[names[0]]
        ax.set_title(f"{inst}\nn = {head['n']}, {head['kind']}", fontsize=10)
        ax.set_ylim(0, max(y + e for y, e in zip(ys, errs)) * 1.28)
        _pct(ax)
    axes[0].set_ylabel("Khoảng cách tới tối ưu (càng thấp càng tốt)")

    fig.suptitle("GA so với tham lam, leo đồi và ngẫu nhiên, "
                 "cùng ngân sách 9060 lần đánh giá",
                 fontsize=12, fontweight="bold", color=INK)
    _finish(fig, FIGURES / "fig3_so_sanh_thuat_toan.png", "summary_baselines.csv",
            "instance, method, gap_percent_mean, gap_percent_std")


# ---------------------------------------------------------------------------
# Hình 4, 5, 6, 7: các tham số
# ---------------------------------------------------------------------------

def _param_rows(experiment: str) -> List[dict]:
    rows = [r for r in read_csv("summary_params.csv") if r["experiment"] == experiment]
    if not rows:
        raise SystemExit(f"Không tìm thấy thí nghiệm {experiment} trong summary_params.csv")
    return rows


def _numeric_sort(rows: List[dict]) -> List[dict]:
    try:
        return sorted(rows, key=lambda r: float(r["param_value"]))
    except ValueError:
        return rows


def fig_pop_size() -> None:
    rows = _numeric_sort(_param_rows("pop_size"))
    labels = [r["param_value"] for r in rows]
    gaps = [_f(r, "gap_percent_mean") for r in rows]
    errs = [_f(r, "gap_percent_std") for r in rows]
    succ = [_f(r, "success_rate") for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    bars = ax1.bar(labels, gaps, 0.6, color=C_BLUE, yerr=_err(gaps, errs), capsize=3,
                   error_kw={"elinewidth": 0.9, "ecolor": INK_SOFT})
    _bar_labels(ax1, bars, errs=errs)
    ax1.set_xlabel("Kích thước quần thể (giữ nguyên tổng ngân sách 9060 lần đánh giá)")
    ax1.set_ylabel("Khoảng cách tới tối ưu")
    ax1.set_title("Quần thể quá nhỏ hay quá lớn đều kém")
    _pct(ax1)

    bars2 = ax2.bar(labels, succ, 0.6, color=C_AQUA)
    _bar_labels(ax2, bars2, "{:.0f}")
    ax2.set_xlabel("Kích thước quần thể")
    ax2.set_ylabel("Tỉ lệ lần chạy chạm đúng tối ưu")
    ax2.set_title("Tỉ lệ thành công theo kích thước quần thể")
    ax2.set_ylim(0, 105)
    _pct(ax2)

    _finish(fig, FIGURES / "fig4_kich_thuoc_quan_the.png", "summary_params.csv",
            "experiment=pop_size: param_value, gap_percent_mean/std, success_rate")


def fig_mutation() -> None:
    rows = _numeric_sort(_param_rows("mutation_scale"))
    labels = [f"{r['param_value']}x" for r in rows]
    gaps = [_f(r, "gap_percent_mean") for r in rows]
    errs = [_f(r, "gap_percent_std") for r in rows]
    divs = [_f(r, "final_diversity_mean") for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    bars = ax1.bar(labels, gaps, 0.6, color=C_BLUE, yerr=_err(gaps, errs), capsize=3,
                   error_kw={"elinewidth": 0.9, "ecolor": INK_SOFT})
    _bar_labels(ax1, bars, errs=errs)
    ax1.set_xlabel("Tỉ lệ đột biến, tính theo bội số của mức chuẩn 1/n")
    ax1.set_ylabel("Khoảng cách tới tối ưu")
    ax1.set_title("Đột biến quá ít thì kẹt, quá nhiều thì hoá ngẫu nhiên")
    _pct(ax1)

    bars2 = ax2.bar(labels, divs, 0.6, color=C_ORANGE)
    _bar_labels(ax2, bars2)
    ax2.set_xlabel("Tỉ lệ đột biến")
    ax2.set_ylabel("Độ đa dạng ở thế hệ cuối")
    ax2.set_title("Đột biến là nguồn giữ đa dạng cho quần thể")

    _finish(fig, FIGURES / "fig5_dot_bien.png", "summary_params.csv",
            "experiment=mutation_scale: param_value, gap_percent_mean/std, final_diversity_mean")


def fig_operators() -> None:
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.6))
    panels = [
        ("crossover", "Kiểu lai ghép", C_BLUE, axes[0][0]),
        ("p_crossover", "Xác suất lai ghép", C_AQUA, axes[0][1]),
        ("selection", "Phương pháp chọn lọc", C_ORANGE, axes[1][0]),
        ("elitism", "Số cá thể tinh hoa giữ lại", C_MAGENTA, axes[1][1]),
    ]
    for experiment, title, color, ax in panels:
        rows = _numeric_sort(_param_rows(experiment))
        labels = [r["param_value"] for r in rows]
        gaps = [_f(r, "gap_percent_mean") for r in rows]
        errs = [_f(r, "gap_percent_std") for r in rows]
        bars = ax.bar(labels, gaps, 0.6, color=color, yerr=_err(gaps, errs), capsize=3,
                      error_kw={"elinewidth": 0.9, "ecolor": INK_SOFT})
        _bar_labels(ax, bars, errs=errs)
        ax.set_title(title)
        ax.set_ylabel("Khoảng cách tới tối ưu")
        _pct(ax)
        if experiment == "selection":
            ax.tick_params(axis="x", labelrotation=20)

    fig.suptitle("Ảnh hưởng của từng toán tử, mỗi lần chỉ đổi một thứ",
                 fontsize=12, fontweight="bold", color=INK)
    _finish(fig, FIGURES / "fig6_toan_tu.png", "summary_params.csv",
            "experiment in {crossover, p_crossover, selection, elitism}: "
            "param_value, gap_percent_mean/std")


def fig_constraint() -> None:
    rows = _param_rows("constraint")
    labels = [r["param_value"] for r in rows]
    gaps = [_f(r, "gap_percent_mean") for r in rows]
    errs = [_f(r, "gap_percent_std") for r in rows]
    succ = [_f(r, "success_rate") for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    bars = ax1.bar(labels, gaps, 0.55, color=C_BLUE, yerr=_err(gaps, errs), capsize=3,
                   error_kw={"elinewidth": 0.9, "ecolor": INK_SOFT})
    _bar_labels(ax1, bars, errs=errs)
    ax1.set_xlabel("Cách xử lý ràng buộc sức chứa")
    ax1.set_ylabel("Khoảng cách tới tối ưu")
    ax1.set_title("Sửa chữa cá thể so với phạt điểm")
    _pct(ax1)

    bars2 = ax2.bar(labels, succ, 0.55, color=C_AQUA)
    _bar_labels(ax2, bars2, "{:.0f}")
    ax2.set_xlabel("Cách xử lý ràng buộc")
    ax2.set_ylabel("Tỉ lệ chạm đúng tối ưu")
    ax2.set_title("Tỉ lệ thành công theo cách xử lý ràng buộc")
    ax2.set_ylim(0, 105)
    _pct(ax2)

    _finish(fig, FIGURES / "fig7_rang_buoc.png", "summary_params.csv",
            "experiment=constraint: param_value, gap_percent_mean/std, success_rate")


# ---------------------------------------------------------------------------
# Hình 8: ba cấu hình tham số
# ---------------------------------------------------------------------------

def fig_tuned() -> None:
    rows = read_csv("summary_tuned.csv")
    order = ["base", "tuned_naive", "tuned"]
    label = {
        "base": "Cấu hình nền",
        "tuned_naive": "Ghép cơ học\ncác giá trị tốt nhất",
        "tuned": "Tổ hợp tìm được\nbằng thử nghiệm",
    }
    colors = {"base": C_GRAY, "tuned_naive": C_ORANGE, "tuned": C_BLUE}
    instances = []
    for r in rows:
        if r["instance"] not in instances:
            instances.append(r["instance"])

    fig, axes = plt.subplots(1, len(instances), figsize=(11, 4.4), sharey=False)
    if len(instances) == 1:
        axes = [axes]
    for ax, inst in zip(axes, instances):
        subset = {r["config"]: r for r in rows if r["instance"] == inst}
        names = [c for c in order if c in subset]
        gaps = [_f(subset[c], "gap_percent_mean") for c in names]
        errs = [_f(subset[c], "gap_percent_std") for c in names]
        # Tỉ lệ chạm tối ưu để ngay dưới nhãn trục, không để trong lòng cột, vì
        # cột 0.00% không có chỗ chứa chữ.
        ticks = [f"{label[c]}\nchạm tối ưu {_f(subset[c], 'success_rate'):.0f}%"
                 for c in names]
        bars = ax.bar(ticks, gaps, 0.6,
                      color=[colors[c] for c in names], yerr=_err(gaps, errs), capsize=3,
                      error_kw={"elinewidth": 0.9, "ecolor": INK_SOFT})
        _bar_labels(ax, bars, errs=errs)
        n = subset[names[0]]["n"]
        ax.set_title(f"{inst} (n = {n})")
        ax.set_ylabel("Khoảng cách tới tối ưu")
        ax.set_ylim(0, max(y + e for y, e in zip(gaps, errs)) * 1.25)
        _pct(ax)

    fig.suptitle("Cùng ngân sách 9060 lần đánh giá, chỉ khác bộ tham số",
                 fontsize=12, fontweight="bold", color=INK)
    _finish(fig, FIGURES / "fig8_tinh_chinh_tham_so.png", "summary_tuned.csv",
            "instance, config, gap_percent_mean/std, success_rate")


# ---------------------------------------------------------------------------
# Hình 9: ngân sách tính toán
# ---------------------------------------------------------------------------

def fig_budget() -> None:
    rows = sorted(read_csv("summary_budget.csv"), key=lambda r: int(r["budget"]))
    raw = read_csv("budget.csv")
    greedy_gap = _f(raw[0], "greedy_gap_percent")
    budgets = [int(r["budget"]) for r in rows]
    gaps = [_f(r, "gap_percent_mean") for r in rows]
    lo = [_f(r, "gap_percent_min") for r in rows]
    hi = [_f(r, "gap_percent_max") for r in rows]

    fig, ax = plt.subplots(figsize=(7.8, 4.4))
    ax.fill_between(budgets, lo, hi, color=C_BLUE, alpha=0.15, linewidth=0)
    ax.plot(budgets, gaps, color=C_BLUE, marker="o", markersize=6,
            label="GA")
    ax.axhline(greedy_gap, color=C_ORANGE, linestyle=":", linewidth=1.6,
               label=f"Tham lam ({greedy_gap:.2f}%, không đổi)")
    for b, g in zip(budgets, gaps):
        ax.annotate(f"{g:.2f}%", (b, g), xytext=(0, 9),
                    textcoords="offset points", ha="center", fontsize=8.5,
                    color=C_BLUE)
    ax.set_xscale("log")
    ax.set_xticks(budgets)
    ax.set_xticklabels([f"{b // 1000}k" for b in budgets])
    ax.set_xlabel("Ngân sách (số lần gọi hàm fitness)")
    ax.set_ylabel("Khoảng cách tới tối ưu")
    ax.set_title("Trên bài n = 500, GA cần đủ ngân sách mới vượt được tham lam")
    _pct(ax)
    ax.legend(loc="upper right")

    _finish(fig, FIGURES / "fig9_ngan_sach.png", "summary_budget.csv + budget.csv",
            "budget, gap_percent_mean/min/max, greedy_gap_percent")


# ---------------------------------------------------------------------------
# Hình 10: khả năng mở rộng
# ---------------------------------------------------------------------------

def fig_scalability() -> None:
    rows = sorted(read_csv("summary_scalability.csv"), key=lambda r: int(r["n"]))
    ns = [int(r["n"]) for r in rows]
    ga_gap = [_f(r, "ga_gap_percent_mean") for r in rows]
    ga_err = [_f(r, "ga_gap_percent_std") for r in rows]
    gr_gap = [_f(r, "greedy_gap_percent_mean") for r in rows]
    ga_time = [_f(r, "ga_runtime_sec_mean") for r in rows]
    dp_time = [_f(r, "dp_runtime_sec_mean") for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))

    ax1.errorbar(ns, ga_gap, yerr=_err(ga_gap, ga_err), color=C_BLUE, marker="o", markersize=6,
                 capsize=3, elinewidth=0.9, label="GA (ngân sách cố định 9060)")
    ax1.plot(ns, gr_gap, color=C_ORANGE, marker="s", markersize=5, label="Tham lam")
    ax1.set_xlabel("Số món đồ n")
    ax1.set_ylabel("Khoảng cách tới tối ưu")
    ax1.set_title("Bài càng lớn, ngân sách cố định càng đuối")
    _pct(ax1)
    ax1.legend(loc="upper left")

    ax2.plot(ns, ga_time, color=C_BLUE, marker="o", markersize=6, label="GA")
    ax2.plot(ns, dp_time, color=C_AQUA, marker="s", markersize=5,
             label="Quy hoạch động")
    ax2.set_yscale("log")
    ax2.set_xlabel("Số món đồ n")
    ax2.set_ylabel("Thời gian chạy (giây, thang log)")
    ax2.set_title("Thời gian chạy theo kích thước bài toán")
    ax2.legend(loc="upper left")

    _finish(fig, FIGURES / "fig10_mo_rong.png", "summary_scalability.csv",
            "n, ga_gap_percent_mean/std, greedy_gap_percent_mean, "
            "ga_runtime_sec_mean, dp_runtime_sec_mean")


def main() -> int:
    print(f"Vẽ biểu đồ vào {FIGURES.name}/")
    for fn in (
        fig_convergence,
        fig_diversity,
        fig_methods,
        fig_pop_size,
        fig_mutation,
        fig_operators,
        fig_constraint,
        fig_tuned,
        fig_budget,
        fig_scalability,
    ):
        fn()
    print("Xong.")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main())
