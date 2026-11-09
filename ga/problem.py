"""Bài toán Cái túi 0/1: dữ liệu, cách mã hoá và hàm thích nghi.

Phát biểu bài toán (yêu cầu 1)
------------------------------
Input     : n món đồ, món i có giá trị v_i > 0 và trọng lượng w_i > 0;
            một chiếc túi chịu được tối đa W đơn vị trọng lượng.
Output    : tập con S các món đồ mang theo.
Ràng buộc : tổng trọng lượng các món trong S không vượt quá W.
Mục tiêu  : cực đại tổng giá trị các món trong S.

Biểu diễn dữ liệu (yêu cầu 4)
-----------------------------
Nhiễm sắc thể là một chuỗi nhị phân dài n: gene[i] = 1 nghĩa là mang món i.
Không gian tìm kiếm có 2^n điểm, với n = 100 đã là 1.27e30 phương án nên
không thể vét cạn, đó là lý do cần tới giải thuật tiến hoá.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import List, Sequence, Tuple

# Ba lớp dữ liệu kinh điển trong các bộ benchmark cái túi.
INSTANCE_KINDS = ("uncorrelated", "weakly_correlated", "strongly_correlated")


@dataclass(frozen=True)
class KnapsackInstance:
    """Một thể hiện (instance) cụ thể của bài toán cái túi."""

    name: str
    values: Tuple[int, ...]
    weights: Tuple[int, ...]
    capacity: int
    kind: str = "uncorrelated"

    @property
    def n(self) -> int:
        return len(self.values)

    @property
    def total_weight(self) -> int:
        return sum(self.weights)

    @property
    def total_value(self) -> int:
        return sum(self.values)

    def ratio(self, i: int) -> float:
        """Mật độ giá trị của món i, dùng cho tham lam và cho thủ tục sửa chữa."""
        return self.values[i] / self.weights[i]

    # ---- đọc và ghi file ----------------------------------------------
    def to_json(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "name": self.name,
                    "kind": self.kind,
                    "capacity": self.capacity,
                    "values": list(self.values),
                    "weights": list(self.weights),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    @staticmethod
    def from_json(path: Path) -> "KnapsackInstance":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        return KnapsackInstance(
            name=raw["name"],
            values=tuple(raw["values"]),
            weights=tuple(raw["weights"]),
            capacity=raw["capacity"],
            kind=raw.get("kind", "uncorrelated"),
        )

    def describe(self) -> str:
        return (
            f"{self.name} [{self.kind}]: n = {self.n} món, sức chứa W = {self.capacity}"
            f" (bằng {100 * self.capacity / self.total_weight:.0f}% tổng trọng lượng),"
            f" lấy hết thì được {self.total_value} điểm giá trị"
        )


def make_instance(
    n: int,
    seed: int,
    kind: str = "strongly_correlated",
    weight_range: Tuple[int, int] = (10, 100),
    capacity_ratio: float = 0.5,
    name: str | None = None,
) -> KnapsackInstance:
    """Sinh một thể hiện theo lớp dữ liệu đã chọn.

    - uncorrelated       : v_i và w_i độc lập nhau. Lớp dễ, tham lam theo tỉ lệ
                           đã gần tối ưu vì các món có mật độ giá trị rất khác nhau.
    - weakly_correlated  : v_i xấp xỉ w_i cộng nhiễu, khó hơn một chút.
    - strongly_correlated: v_i = w_i + 10, mọi món có mật độ gần như nhau nên
                           tham lam mất phương hướng. Đây là lớp khó kinh điển
                           và là lớp nhóm chọn làm bài chính.

    capacity_ratio = W / tổng trọng lượng. Để 0.5 cho bài toán đủ chặt: nếu W
    quá lớn thì lấy gần hết món nào cũng thoả, bài toán mất ý nghĩa.
    """
    if kind not in INSTANCE_KINDS:
        raise ValueError(f"kind không hợp lệ: {kind}")
    rng = random.Random(seed)
    lo, hi = weight_range
    weights = tuple(rng.randint(lo, hi) for _ in range(n))
    if kind == "uncorrelated":
        values = tuple(rng.randint(lo, hi) for _ in range(n))
    elif kind == "weakly_correlated":
        values = tuple(max(1, w + rng.randint(-hi // 10, hi // 10)) for w in weights)
    else:
        values = tuple(w + 10 for w in weights)
    capacity = max(max(weights), int(capacity_ratio * sum(weights)))
    return KnapsackInstance(
        name=name or f"kp_{kind[:4]}_n{n}_s{seed}",
        values=values,
        weights=weights,
        capacity=capacity,
        kind=kind,
    )


# ---------------------------------------------------------------------------
# Hàm thích nghi (fitness)
# ---------------------------------------------------------------------------

class EvalCounter:
    """Đếm số lần gọi hàm fitness.

    Số lần đánh giá fitness là đơn vị chi phí chung để so sánh công bằng giữa
    GA, leo đồi và tìm kiếm ngẫu nhiên: cùng ngân sách thì ai tìm tốt hơn.
    """

    __slots__ = ("count",)

    def __init__(self) -> None:
        self.count = 0

    def tick(self, k: int = 1) -> None:
        self.count += k


@lru_cache(maxsize=16)
def ratio_order_asc(inst: KnapsackInstance) -> Tuple[int, ...]:
    """Chỉ số các món xếp theo mật độ giá trị tăng dần, tính sẵn và nhớ lại."""
    return tuple(sorted(range(inst.n), key=inst.ratio))


@dataclass
class Evaluation:
    fitness: float      # điểm dùng để so sánh các cá thể trong quần thể
    value: int          # tổng giá trị thực sự mang về
    weight: int         # tổng trọng lượng sau khi giải mã
    feasible: bool      # có thoả ràng buộc sức chứa hay không
    genes: List[int]    # nhiễm sắc thể sau khi sửa chữa (nếu dùng chế độ repair)


def evaluate(
    inst: KnapsackInstance,
    genes: Sequence[int],
    mode: str = "repair",
    penalty_coef: float = 2.0,
    counter: EvalCounter | None = None,
) -> Evaluation:
    """Giải mã nhiễm sắc thể thành lời giải rồi chấm điểm.

    Hai cách xử lý cá thể vượt sức chứa:

    - mode="repair" : bỏ dần món có tỉ lệ giá trị trên trọng lượng thấp nhất
                      cho tới khi vừa túi. Mọi cá thể luôn hợp lệ.
    - mode="penalty": giữ nguyên cá thể nhưng trừ điểm phạt
                      fitness = value - penalty_coef * (weight - W).
                      Cách này cho phép đi xuyên qua vùng không hợp lệ.
    """
    if counter is not None:
        counter.tick()

    genes = list(genes)
    weight = sum(w for g, w in zip(genes, inst.weights) if g)
    value = sum(v for g, v in zip(genes, inst.values) if g)

    if weight <= inst.capacity:
        return Evaluation(float(value), value, weight, True, genes)

    if mode == "penalty":
        fitness = value - penalty_coef * (weight - inst.capacity)
        return Evaluation(float(fitness), value, weight, False, genes)

    if mode != "repair":
        raise ValueError(f"mode không hợp lệ: {mode}")

    # Sửa chữa: bỏ món tệ nhất trước, tức món có mật độ giá trị thấp nhất.
    # Thứ tự mật độ của một thể hiện là cố định nên được tính sẵn một lần,
    # nhờ vậy mỗi lần đánh giá chỉ tốn O(n) chứ không phải sắp xếp lại.
    for i in ratio_order_asc(inst):
        if weight <= inst.capacity:
            break
        if genes[i]:
            genes[i] = 0
            weight -= inst.weights[i]
            value -= inst.values[i]
    return Evaluation(float(value), value, weight, True, genes)


def decode(inst: KnapsackInstance, genes: Sequence[int]) -> List[int]:
    """Danh sách chỉ số các món được chọn, để in ra cho dễ đọc."""
    return [i for i, g in enumerate(genes) if g]
