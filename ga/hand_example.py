"""Ví dụ tính tay từng bước cho TV3 (yêu cầu 3).

Chạy GA trên một bài toán tí hon (6 món, quần thể 6 cá thể, 2 thế hệ) và in ra
toàn bộ các con số trung gian dưới dạng bảng markdown: fitness, phần bánh xe
roulette, điểm cắt khi lai ghép, gene nào bị đột biến, quần thể mới.

Dùng đúng các hàm toán tử trong ga/algorithm.py, chỉ viết lại vòng lặp cho
tường minh để nhìn thấy từng bước. Nhờ vậy con số trên slide trùng khớp tuyệt
đối với con số do chương trình sinh ra, giảng viên có hỏi cũng chứng minh được.

Cách chạy:
    python -m ga.hand_example            # in ra màn hình và ghi file markdown
"""

from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import List, Sequence

from .algorithm import mutate, population_diversity, select_roulette
from .baselines import brute_force
from .problem import KnapsackInstance, evaluate

ROOT = Path(__file__).resolve().parent.parent
OUT_FILE = ROOT / "docs" / "vi-du-tinh-tay.md"

# Bài toán tí hon, các con số chọn tròn trịa để nhẩm tay được.
TOY = KnapsackInstance(
    name="kp_toy",
    values=(8, 7, 9, 4, 12, 2),
    weights=(3, 4, 5, 2, 6, 1),
    capacity=12,
    kind="uncorrelated",
)

POP_SIZE = 6
GENERATIONS = 2
P_MUTATION = 0.15        # cố ý để cao hơn mức 1/n để trong 2 thế hệ chắc chắn
P_CROSSOVER = 1.0        # thấy được đột biến xảy ra
ELITISM = 1
SEED = 97            # chọn seed này vì ba thế hệ cho thấy rõ fitness cải thiện dần


class Report:
    """Gom các dòng in ra để vừa hiện trên màn hình vừa ghi thành file."""

    def __init__(self) -> None:
        self.lines: List[str] = []

    def __call__(self, text: str = "") -> None:
        print(text)
        self.lines.append(text)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")
        print(f"\nĐã ghi bản markdown vào {path}")


def genes_str(genes: Sequence[int]) -> str:
    return "".join(str(g) for g in genes)


def table(out: Report, header: Sequence[str], rows: Sequence[Sequence[str]]) -> None:
    out("| " + " | ".join(header) + " |")
    out("|" + "|".join("---" for _ in header) + "|")
    for row in rows:
        out("| " + " | ".join(str(c) for c in row) + " |")
    out()


def show_instance(out: Report) -> None:
    out("## Bài toán dùng cho ví dụ")
    out()
    out(f"Sức chứa của túi **W = {TOY.capacity}**, có {TOY.n} món đồ:")
    out()
    table(
        out,
        ["Món i", "Giá trị v_i", "Trọng lượng w_i", "Mật độ v_i/w_i"],
        [
            [i, TOY.values[i], TOY.weights[i], f"{TOY.ratio(i):.2f}"]
            for i in range(TOY.n)
        ],
    )
    bf = brute_force(TOY)
    out(f"Vét cạn toàn bộ 2^{TOY.n} = {2 ** TOY.n} phương án cho biết nghiệm tối ưu "
        f"là **{bf.value}** với tổ hợp `{genes_str(bf.genes or [])}` "
        f"(trọng lượng {bf.weight}/{TOY.capacity}). "
        "Con số này chỉ dùng để đối chiếu, bản thân GA không biết trước.")
    out()
    out("Cách mã hoá: nhiễm sắc thể là chuỗi 6 bit, bit thứ i bằng 1 nghĩa là "
        "mang món i theo. Ví dụ `101001` nghĩa là mang món 0, 2 và 5.")
    out()


def population_table(out: Report, pop: Sequence[Sequence[int]], title: str) -> List[dict]:
    """In bảng quần thể và trả về thông tin đánh giá của từng cá thể."""
    info = []
    rows = []
    for idx, ind in enumerate(pop):
        ev = evaluate(TOY, ind, "repair")
        raw_weight = sum(w for g, w in zip(ind, TOY.weights) if g)
        repaired = ev.genes != list(ind)
        info.append({"genes": ev.genes, "fitness": ev.fitness, "value": ev.value,
                     "weight": ev.weight})
        rows.append([
            f"C{idx + 1}",
            f"`{genes_str(ind)}`",
            raw_weight,
            "có" if repaired else "không",
            f"`{genes_str(ev.genes)}`" if repaired else "-",
            ev.weight,
            int(ev.fitness),
        ])
    out(title)
    out()
    table(
        out,
        ["Cá thể", "Nhiễm sắc thể", "Trọng lượng thô", "Phải sửa chữa",
         "Sau sửa chữa", "Trọng lượng", "Fitness"],
        rows,
    )
    fits = [i["fitness"] for i in info]
    out(f"Fitness tốt nhất {int(max(fits))}, trung bình {sum(fits) / len(fits):.2f}, "
        f"độ đa dạng gene {population_diversity([i['genes'] for i in info]):.3f}.")
    out()
    return info


def roulette_table(out: Report, info: Sequence[dict]) -> None:
    fits = [i["fitness"] for i in info]
    total = sum(fits)
    acc = 0.0
    rows = []
    for idx, f in enumerate(fits):
        share = 100 * f / total
        acc += share
        rows.append([f"C{idx + 1}", int(f), f"{share:.1f}%", f"{acc:.1f}%"])
    out("Bánh xe roulette, phần bánh xe tỉ lệ thuận với fitness:")
    out()
    table(out, ["Cá thể", "Fitness", "Tỉ lệ được chọn", "Luỹ kế"], rows)


def build_report(seed: int = SEED) -> tuple[Report, List[int], int]:
    """Chạy toàn bộ ví dụ, trả về báo cáo, fitness tốt nhất mỗi thế hệ và nghiệm cuối."""
    out = Report()
    out("# Ví dụ tính tay từng bước của giải thuật di truyền")
    out()
    out("File này do `python -m ga.hand_example` sinh ra, mọi con số trong đây "
        "đều lấy thẳng từ mã nguồn chứ không nhập tay.")
    out()
    out(f"Tham số: quần thể {POP_SIZE} cá thể, {GENERATIONS} thế hệ, chọn lọc "
        f"bánh xe roulette, lai ghép một điểm với xác suất {P_CROSSOVER:.0%}, "
        f"đột biến mỗi gene với xác suất {P_MUTATION:.0%}, giữ lại {ELITISM} "
        f"cá thể tinh hoa, seed = {seed}.")
    out()

    show_instance(out)

    rng = random.Random(seed)
    gen_best: List[int] = []
    pop: List[List[int]] = [[rng.randint(0, 1) for _ in range(TOY.n)]
                            for _ in range(POP_SIZE)]

    best_genes: List[int] = []
    best_value = -1

    for gen in range(GENERATIONS + 1):
        out(f"## Thế hệ {gen}")
        out()
        info = population_table(
            out, pop,
            "Bước 1: giải mã và chấm điểm từng cá thể "
            "(cá thể nào quá nặng thì bỏ bớt món có mật độ thấp nhất)",
        )
        gen_best.append(int(max(i["fitness"] for i in info)))
        for item in info:
            if item["value"] > best_value:
                best_value = item["value"]
                best_genes = list(item["genes"])
        pop = [list(i["genes"]) for i in info]
        fits = [i["fitness"] for i in info]

        if gen == GENERATIONS:
            out(f"Hết {GENERATIONS} thế hệ. Nghiệm tốt nhất tìm được là "
                f"`{genes_str(best_genes)}` với giá trị **{best_value}**.")
            out()
            break

        ranked = sorted(range(len(pop)), key=lambda i: fits[i], reverse=True)
        elite = [list(pop[i]) for i in ranked[:ELITISM]]
        out(f"Bước 2: giữ lại {ELITISM} cá thể tinh hoa: "
            + ", ".join(f"C{i + 1} (`{genes_str(pop[i])}`, fitness {int(fits[i])})"
                        for i in ranked[:ELITISM]))
        out()

        out("Bước 3: chọn lọc cha mẹ")
        out()
        roulette_table(out, info)

        children = list(elite)
        pair_rows = []
        pair_no = 0
        while len(children) < POP_SIZE:
            pair_no += 1
            p1 = select_roulette(pop, fits, rng)
            p2 = select_roulette(pop, fits, rng)
            before = (genes_str(p1), genes_str(p2))
            point = rng.randrange(1, TOY.n)
            # Lai ghép một điểm, tự cắt tại `point` để in được vị trí cắt ra bảng.
            c1 = list(p1[:point]) + list(p2[point:])
            c2 = list(p2[:point]) + list(p1[point:])
            flips1 = mutate(c1, P_MUTATION, rng)
            flips2 = mutate(c2, P_MUTATION, rng)
            pair_rows.append([
                pair_no,
                f"`{before[0]}`", f"`{before[1]}`",
                f"sau bit {point}",
                f"`{genes_str(c1)}`", flips1,
                f"`{genes_str(c2)}`", flips2,
            ])
            children.append(c1)
            if len(children) < POP_SIZE:
                children.append(c2)

        out("Bước 4 và 5: lai ghép rồi đột biến")
        out()
        table(
            out,
            ["Cặp", "Cha", "Mẹ", "Điểm cắt", "Con 1", "Số gene đột biến ở con 1",
             "Con 2", "Số gene đột biến ở con 2"],
            pair_rows,
        )
        out(f"Bước 6: quần thể thế hệ {gen + 1} gồm "
            + ", ".join(f"`{genes_str(c)}`" for c in children))
        out()
        pop = children

    bf = brute_force(TOY)
    out("## Kết luận của ví dụ")
    out()
    out(f"- Nghiệm tối ưu thật sự (vét cạn): **{bf.value}**")
    out(f"- Nghiệm GA tìm được sau {GENERATIONS} thế hệ: **{best_value}** "
        f"(`{genes_str(best_genes)}`)")
    if best_value >= bf.value:
        out("- Với bài tí hon này, chỉ 2 thế hệ là đã chạm đúng nghiệm tối ưu.")
    else:
        out(f"- Còn kém tối ưu {bf.value - best_value} điểm. Bài thật dùng quần thể "
            "60 cá thể và 150 thế hệ nên sai lệch nhỏ hơn hẳn.")
    out()
    out("Điểm cần nhấn khi thuyết trình: fitness tốt nhất của quần thể không bao "
        "giờ đi xuống, vì cơ chế tinh hoa luôn chép thẳng cá thể khoẻ nhất sang "
        "thế hệ sau. Lai ghép lo việc khai thác những mảnh gene tốt đã có, đột "
        "biến lo việc khám phá những mảnh gene chưa từng xuất hiện.")

    return out, gen_best, best_value


def main() -> int:
    out, _, _ = build_report()
    out.save(OUT_FILE)
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main())
