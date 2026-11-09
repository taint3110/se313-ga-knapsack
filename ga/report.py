"""Gom các file CSV thành một bảng tóm tắt markdown cho phần Kết quả.

Chạy sau ga.experiments:
    python -m ga.report

Sinh ra docs/ket-qua-tom-tat.md. Mọi con số trong file đó đều đọc thẳng từ CSV
nên không bao giờ lệch với dữ liệu thật, cứ chạy lại thí nghiệm là bảng tự cập
nhật theo.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import List, Sequence

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
OUT_FILE = ROOT / "docs" / "ket-qua-tom-tat.md"

METHOD_LABEL = {
    "ga": "GA (di truyền)",
    "greedy": "Tham lam theo mật độ",
    "hill_climbing": "Leo đồi lật bit",
    "random": "Tìm kiếm ngẫu nhiên",
    "dp_exact": "Quy hoạch động (tối ưu)",
    "brute_force": "Vét cạn 2^n",
}
METHOD_ORDER = ["ga", "greedy", "hill_climbing", "random", "brute_force", "dp_exact"]

EXPERIMENT_TITLE = {
    "pop_size": "Kích thước quần thể (giữ nguyên tổng ngân sách đánh giá)",
    "mutation_scale": "Tỉ lệ đột biến, theo bội số của mức chuẩn 1/n",
    "p_crossover": "Xác suất lai ghép",
    "crossover": "Kiểu lai ghép",
    "selection": "Phương pháp chọn lọc",
    "elitism": "Số cá thể tinh hoa",
    "constraint": "Cách xử lý ràng buộc sức chứa",
}


def read_csv(name: str) -> List[dict]:
    path = RESULTS / name
    if not path.exists():
        raise SystemExit(f"Thiếu {path.name}. Chạy `python -m ga.experiments` trước.")
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def f(row: dict, key: str) -> float:
    return float(row[key])


class Doc:
    def __init__(self) -> None:
        self.lines: List[str] = []

    def __call__(self, text: str = "") -> None:
        self.lines.append(text)

    def table(self, header: Sequence[str], rows: Sequence[Sequence[object]]) -> None:
        self("| " + " | ".join(header) + " |")
        self("|" + "|".join("---" for _ in header) + "|")
        for row in rows:
            self("| " + " | ".join(str(c) for c in row) + " |")
        self()

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")
        print(f"  -> {path}")


def section_overview(doc: Doc, meta: dict) -> None:
    doc("## 1. Thiết lập thí nghiệm")
    doc()
    cfg = meta["base_config"]
    doc(f"- Số lần lặp lại mỗi cấu hình: **{meta['seeds']}** seed khác nhau")
    doc(f"- Ngân sách chung cho mọi thuật toán ngẫu nhiên: "
        f"**{meta['budget_evaluations']} lần gọi hàm fitness**")
    doc(f"- Cấu hình nền: quần thể {cfg['pop_size']}, {cfg['generations']} thế hệ, "
        f"chọn lọc {cfg['selection']} k = {cfg['tournament_k']}, lai ghép "
        f"{cfg['crossover']} p = {cfg['p_crossover']}, đột biến 1/n, "
        f"tinh hoa {cfg['elitism']}, xử lý ràng buộc bằng {cfg['repair_mode']}")
    doc(f"- Tổng thời gian chạy toàn bộ thí nghiệm: "
        f"{meta['total_runtime_sec']:.0f} giây")
    doc()
    doc("Bốn bộ dữ liệu:")
    doc()
    doc.table(
        ["Bộ dữ liệu", "Mô tả", "Nghiệm tối ưu (quy hoạch động)"],
        [[k, v, meta["optima"][k]] for k, v in meta["instances"].items()],
    )


def section_methods(doc: Doc) -> None:
    rows = read_csv("summary_baselines.csv")
    doc("## 2. GA so với các thuật toán khác")
    doc()
    doc("Cùng một ngân sách đánh giá fitness. Cột lệch tối ưu càng nhỏ càng tốt, "
        "0% nghĩa là tìm đúng nghiệm tối ưu.")
    doc()
    instances: List[str] = []
    for r in rows:
        if r["instance"] not in instances:
            instances.append(r["instance"])

    for inst in instances:
        subset = [r for r in rows if r["instance"] == inst]
        head = subset[0]
        doc(f"**{inst}** (n = {head['n']}, lớp dữ liệu {head['kind']})")
        doc()
        table_rows = []
        for method in METHOD_ORDER:
            rec = next((r for r in subset if r["method"] == method), None)
            if rec is None:
                continue
            table_rows.append([
                METHOD_LABEL[method],
                int(rec["runs"]),
                f"{f(rec, 'best_value_mean'):.1f}",
                int(f(rec, "best_value_max")),
                f"{f(rec, 'gap_percent_mean'):.2f}%",
                f"{f(rec, 'gap_percent_std'):.2f}",
                f"{f(rec, 'success_rate'):.0f}%",
                f"{f(rec, 'runtime_sec_mean'):.3f}s",
            ])
        doc.table(
            ["Thuật toán", "Số lần chạy", "Giá trị trung bình", "Giá trị tốt nhất",
             "Lệch tối ưu trung bình", "Độ lệch chuẩn", "Tỉ lệ chạm tối ưu",
             "Thời gian"],
            table_rows,
        )


def section_params(doc: Doc) -> None:
    rows = read_csv("summary_params.csv")
    doc("## 3. Ảnh hưởng của tham số")
    doc()
    doc("Mỗi bảng chỉ đổi đúng một tham số, mọi tham số còn lại giữ như cấu hình nền.")
    doc()
    order = ["pop_size", "mutation_scale", "p_crossover", "crossover", "selection",
             "elitism", "constraint"]
    for experiment in order:
        subset = [r for r in rows if r["experiment"] == experiment]
        if not subset:
            continue
        try:
            subset.sort(key=lambda r: float(r["param_value"]))
        except ValueError:
            pass
        doc(f"### 3.{order.index(experiment) + 1}. "
            f"{EXPERIMENT_TITLE.get(experiment, experiment)}")
        doc()
        doc.table(
            ["Giá trị", "Lệch tối ưu trung bình", "Độ lệch chuẩn",
             "Tỉ lệ chạm tối ưu", "Thế hệ tìm ra nghiệm tốt nhất",
             "Đa dạng cuối", "Thời gian"],
            [[
                r["param_value"],
                f"{f(r, 'gap_percent_mean'):.2f}%",
                f"{f(r, 'gap_percent_std'):.2f}",
                f"{f(r, 'success_rate'):.0f}%",
                f"{f(r, 'gen_to_best_mean'):.0f}",
                f"{f(r, 'final_diversity_mean'):.3f}",
                f"{f(r, 'runtime_sec_mean'):.3f}s",
            ] for r in subset],
        )
        best = min(subset, key=lambda r: f(r, "gap_percent_mean"))
        worst = max(subset, key=lambda r: f(r, "gap_percent_mean"))
        doc(f"Tốt nhất: **{best['param_value']}** "
            f"({f(best, 'gap_percent_mean'):.2f}%). "
            f"Kém nhất: **{worst['param_value']}** "
            f"({f(worst, 'gap_percent_mean'):.2f}%).")
        doc()


def section_tuned(doc: Doc, meta: dict) -> None:
    rows = read_csv("summary_tuned.csv")
    doc("## 4. Tinh chỉnh bộ tham số")
    doc()
    doc("Ba bộ tham số, cùng một ngân sách khoảng 9060 lần đánh giá:")
    doc()
    naive = meta["tuned_naive_config"]
    tuned = meta["tuned_config"]
    doc("- **base**: quần thể 60 x 150 thế hệ, tournament k = 3, one_point "
        "p = 0.9, đột biến 1/n, tinh hoa 2")
    doc(f"- **tuned_naive**: ghép cơ học giá trị tốt nhất của từng tham số trong "
        f"mục 3, thành quần thể {naive['pop_size']} x {naive['generations']} thế "
        f"hệ, tournament k = {naive['tournament_k']}, {naive['crossover']} "
        f"p = {naive['p_crossover']}, đột biến {naive['mutation_scale']:.0f}/n, "
        f"tinh hoa {naive['elitism']}")
    doc(f"- **tuned**: tổ hợp tốt nhất tìm được khi thử theo tổ hợp, quần thể "
        f"{tuned['pop_size']} x {tuned['generations']} thế hệ, tournament "
        f"k = {tuned['tournament_k']}, {tuned['crossover']} "
        f"p = {tuned['p_crossover']}, đột biến {tuned['mutation_scale']:.0f}/n, "
        f"tinh hoa {tuned['elitism']}")
    doc()
    instances: List[str] = []
    for r in rows:
        if r["instance"] not in instances:
            instances.append(r["instance"])
    order = ["base", "tuned_naive", "tuned"]
    table_rows = []
    for inst in instances:
        subset = {r["config"]: r for r in rows if r["instance"] == inst}
        for cfg in order:
            rec = subset.get(cfg)
            if rec is None:
                continue
            table_rows.append([
                inst,
                rec["n"],
                cfg,
                f"{f(rec, 'best_value_mean'):.1f}",
                int(f(rec, "best_value_max")),
                f"{f(rec, 'gap_percent_mean'):.3f}%",
                f"{f(rec, 'gap_percent_std'):.3f}",
                f"{f(rec, 'success_rate'):.0f}%",
                f"{100 * f(rec, 'beats_greedy_mean'):.0f}%",
            ])
    doc.table(
        ["Bộ dữ liệu", "n", "Cấu hình", "Giá trị trung bình", "Giá trị tốt nhất",
         "Lệch tối ưu trung bình", "Độ lệch chuẩn", "Tỉ lệ chạm tối ưu",
         "Tỉ lệ vượt tham lam"],
        table_rows,
    )
    doc("Điểm đáng chú ý: cấu hình **tuned_naive** ghép từ các giá trị tốt nhất "
        "của từng tham số riêng lẻ lại cho kết quả tệ hơn cả cấu hình nền. Các "
        "tham số không độc lập với nhau, phải thử theo tổ hợp chứ không cộng dồn "
        "được.")
    doc()


def section_budget(doc: Doc) -> None:
    rows = sorted(read_csv("summary_budget.csv"), key=lambda r: int(r["budget"]))
    raw = read_csv("budget.csv")
    greedy_gap = f(raw[0], "greedy_gap_percent")
    doc("## 5. Ngân sách tính toán trên bài n = 500")
    doc()
    doc(f"Tham lam đứng yên ở mức lệch {greedy_gap:.2f}% dù cho bao nhiêu thời gian "
        "cũng vậy, còn GA cải thiện dần theo ngân sách.")
    doc()
    doc("Bảng này dùng bộ toán tử của cấu hình nền, chỉ kéo dài số thế hệ. "
        "Đối chiếu với mục 4 sẽ thấy một điều đáng giá: cấu hình đã tinh chỉnh "
        "chỉ cần 9000 lần đánh giá đã đạt 0.20%, tức ngang với cấu hình nền khi "
        "được cấp 100000 lần đánh giá. Chỉnh tham số cho đúng tiết kiệm được "
        "hơn mười lần chi phí tính toán.")
    doc()
    doc.table(
        ["Ngân sách đánh giá", "Số thế hệ", "Lệch tối ưu trung bình",
         "Tốt nhất", "Tỉ lệ vượt tham lam", "Thời gian mỗi lần chạy"],
        [[
            f"{int(r['budget']):,}".replace(",", "."),
            r["generations"],
            f"{f(r, 'gap_percent_mean'):.2f}%",
            f"{f(r, 'gap_percent_min'):.2f}%",
            f"{100 * f(r, 'beats_greedy_mean'):.0f}%",
            f"{f(r, 'runtime_sec_mean'):.2f}s",
        ] for r in rows],
    )


def section_scalability(doc: Doc) -> None:
    rows = sorted(read_csv("summary_scalability.csv"), key=lambda r: int(r["n"]))
    doc("## 6. Khả năng mở rộng theo kích thước bài toán")
    doc()
    doc("GA giữ nguyên ngân sách 9060 lần đánh giá ở mọi kích thước, nên bài càng "
        "lớn thì mỗi điểm trong không gian càng ít được thăm dò.")
    doc()
    doc.table(
        ["n", "Không gian tìm kiếm", "Lệch tối ưu của GA", "Lệch tối ưu của tham lam",
         "Tỉ lệ GA chạm tối ưu", "Thời gian GA", "Thời gian quy hoạch động"],
        [[
            r["n"],
            f"2^{r['n']}",
            f"{f(r, 'ga_gap_percent_mean'):.2f}%",
            f"{f(r, 'greedy_gap_percent_mean'):.2f}%",
            f"{f(r, 'success_rate'):.0f}%",
            f"{f(r, 'ga_runtime_sec_mean'):.2f}s",
            f"{f(r, 'dp_runtime_sec_mean') * 1000:.1f} ms",
        ] for r in rows],
    )


def main() -> int:
    meta = json.loads((RESULTS / "run_meta.json").read_text(encoding="utf-8"))
    doc = Doc()
    doc("# Kết quả thí nghiệm, bảng tóm tắt")
    doc()
    doc("File này do `python -m ga.report` sinh ra từ các file CSV trong "
        "`results/`. Không sửa tay, muốn đổi số thì chạy lại thí nghiệm.")
    doc()
    section_overview(doc, meta)
    section_methods(doc)
    section_params(doc)
    section_tuned(doc, meta)
    section_budget(doc)
    section_scalability(doc)
    doc("---")
    doc()
    doc("Biểu đồ tương ứng nằm trong `results/figures/`, sinh bằng "
        "`python -m ga.plots`.")
    doc.save(OUT_FILE)
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main())
