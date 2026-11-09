"""Các thuật toán đối chứng để so sánh với GA (yêu cầu 5 và 6).

    - brute_force   : vét cạn 2^n, chỉ chạy nổi khi n nhỏ, dùng để chứng minh
                      quy hoạch động cho ra đúng nghiệm tối ưu.
    - dp_exact      : quy hoạch động O(n*W), cho nghiệm tối ưu tuyệt đối.
                      Đây là mốc chuẩn để tính khoảng cách (gap) của GA.
    - greedy_ratio  : tham lam theo tỉ lệ giá trị trên trọng lượng, O(n log n).
    - random_search : lấy mẫu ngẫu nhiên với cùng ngân sách đánh giá như GA.
    - hill_climbing : leo đồi lật bit, có khởi động lại ngẫu nhiên.

Ba thuật toán cuối nhận cùng một `budget` là số lần gọi hàm fitness, nhờ vậy
so sánh với GA mới công bằng: cùng chi phí tính toán thì ai tìm được nghiệm
tốt hơn.
"""

from __future__ import annotations

import itertools
import random
import time
from dataclasses import dataclass
from typing import List, Optional

from .problem import EvalCounter, KnapsackInstance, evaluate

try:                                    # numpy chỉ dùng để tăng tốc quy hoạch động
    import numpy as _np
except ImportError:                     # vẫn chạy được khi máy không có numpy
    _np = None


@dataclass
class BaselineResult:
    method: str
    value: int
    weight: int
    runtime: float
    evaluations: int
    genes: Optional[List[int]] = None
    exact: bool = False                 # có bảo đảm là nghiệm tối ưu hay không


# ---------------------------------------------------------------------------

def brute_force(inst: KnapsackInstance, max_n: int = 22) -> BaselineResult:
    """Duyệt toàn bộ 2^n tổ hợp. Chỉ dùng cho n nhỏ để kiểm chứng."""
    if inst.n > max_n:
        raise ValueError(f"vét cạn chỉ chạy với n <= {max_n}, instance có n = {inst.n}")
    t0 = time.perf_counter()
    best_value = -1
    best_genes: List[int] = []
    best_weight = 0
    count = 0
    for combo in itertools.product((0, 1), repeat=inst.n):
        count += 1
        weight = sum(w for g, w in zip(combo, inst.weights) if g)
        if weight > inst.capacity:
            continue
        value = sum(v for g, v in zip(combo, inst.values) if g)
        if value > best_value:
            best_value, best_weight, best_genes = value, weight, list(combo)
    return BaselineResult(
        "brute_force", best_value, best_weight,
        time.perf_counter() - t0, count, best_genes, exact=True,
    )


def dp_exact(inst: KnapsackInstance) -> BaselineResult:
    """Quy hoạch động theo sức chứa, trả về nghiệm tối ưu tuyệt đối.

    dp[w] = giá trị lớn nhất đạt được với sức chứa w sau khi xét i món đầu.
    Duyệt w giảm dần nên mỗi món chỉ được lấy một lần (bài toán 0/1).
    Bảng `keep` lưu lại quyết định để truy vết ra danh sách món đã chọn.
    """
    t0 = time.perf_counter()
    n, cap = inst.n, inst.capacity

    if _np is not None:
        dp = _np.zeros(cap + 1, dtype=_np.int64)
        keep = _np.zeros((n, cap + 1), dtype=bool)
        for i in range(n):
            w, v = inst.weights[i], inst.values[i]
            if w > cap:
                continue
            candidate = dp[: cap + 1 - w] + v
            better = candidate > dp[w:]
            keep[i, w:] = better
            dp[w:] = _np.where(better, candidate, dp[w:])
        best_value = int(dp[cap])
        genes = [0] * n
        w = cap
        for i in range(n - 1, -1, -1):
            if keep[i, w]:
                genes[i] = 1
                w -= inst.weights[i]
    else:
        dp = [0] * (cap + 1)
        keep = [bytearray(cap + 1) for _ in range(n)]
        for i in range(n):
            wi, vi = inst.weights[i], inst.values[i]
            row = keep[i]
            for w in range(cap, wi - 1, -1):
                cand = dp[w - wi] + vi
                if cand > dp[w]:
                    dp[w] = cand
                    row[w] = 1
        best_value = dp[cap]
        genes = [0] * n
        w = cap
        for i in range(n - 1, -1, -1):
            if keep[i][w]:
                genes[i] = 1
                w -= inst.weights[i]

    weight = sum(wi for g, wi in zip(genes, inst.weights) if g)
    return BaselineResult(
        "dp_exact", best_value, weight,
        time.perf_counter() - t0, n * (cap + 1), genes, exact=True,
    )


def greedy_ratio(inst: KnapsackInstance) -> BaselineResult:
    """Tham lam: xếp món theo tỉ lệ giá trị/trọng lượng giảm dần rồi nhét dần.

    Rất nhanh nhưng không bảo đảm tối ưu, vì một món cồng kềnh bị bỏ qua sớm
    có thể là món phải có trong nghiệm tốt nhất.
    """
    t0 = time.perf_counter()
    order = sorted(range(inst.n), key=inst.ratio, reverse=True)
    genes = [0] * inst.n
    weight = value = 0
    for i in order:
        if weight + inst.weights[i] <= inst.capacity:
            genes[i] = 1
            weight += inst.weights[i]
            value += inst.values[i]
    return BaselineResult(
        "greedy", value, weight, time.perf_counter() - t0, inst.n, genes,
    )


def random_search(inst: KnapsackInstance, budget: int, seed: int = 0) -> BaselineResult:
    """Lấy mẫu ngẫu nhiên `budget` lần, giữ lại cá thể tốt nhất.

    Đây là mốc thấp nhất: nếu GA không hơn hẳn cách này thì GA vô nghĩa.
    """
    t0 = time.perf_counter()
    rng = random.Random(seed)
    counter = EvalCounter()
    best_value, best_weight = -1, 0
    best_genes: List[int] = []
    for _ in range(budget):
        genes = [rng.randint(0, 1) for _ in range(inst.n)]
        ev = evaluate(inst, genes, "repair", counter=counter)
        if ev.value > best_value:
            best_value, best_weight, best_genes = ev.value, ev.weight, ev.genes
    return BaselineResult(
        "random", best_value, best_weight,
        time.perf_counter() - t0, counter.count, best_genes,
    )


def hill_climbing(inst: KnapsackInstance, budget: int, seed: int = 0) -> BaselineResult:
    """Leo đồi lật bit, hết ngân sách thì thôi, kẹt thì khởi động lại.

    Lân cận của một lời giải là tập các lời giải khác nó đúng một bit. Thuật
    toán nhận ngay cải thiện đầu tiên tìm được (first improvement). Khi không
    còn hàng xóm nào tốt hơn thì đang ở cực trị địa phương, phải nhảy sang
    điểm xuất phát ngẫu nhiên khác. So sánh với GA ở đây cho thấy đúng chỗ
    mạnh của GA: quần thể và lai ghép giúp thoát bẫy cực trị địa phương.
    """
    t0 = time.perf_counter()
    rng = random.Random(seed)
    counter = EvalCounter()
    best_value, best_weight = -1, 0
    best_genes: List[int] = []
    restarts = 0

    while counter.count < budget:
        restarts += 1
        current = [rng.randint(0, 1) for _ in range(inst.n)]
        cur = evaluate(inst, current, "repair", counter=counter)
        current, cur_value = cur.genes, cur.value
        improved = True
        while improved and counter.count < budget:
            improved = False
            for i in rng.sample(range(inst.n), inst.n):
                if counter.count >= budget:
                    break
                neighbour = list(current)
                neighbour[i] ^= 1
                ev = evaluate(inst, neighbour, "repair", counter=counter)
                if ev.value > cur_value:
                    current, cur_value = ev.genes, ev.value
                    improved = True
                    break
        if cur_value > best_value:
            best_value = cur_value
            best_genes = list(current)
            best_weight = sum(w for g, w in zip(best_genes, inst.weights) if g)

    return BaselineResult(
        "hill_climbing", best_value, best_weight,
        time.perf_counter() - t0, counter.count, best_genes,
    )


def gap_percent(value: float, optimum: float) -> float:
    """Khoảng cách tới nghiệm tối ưu, tính theo phần trăm. 0% là trùng tối ưu."""
    if optimum <= 0:
        return 0.0
    return 100.0 * (optimum - value) / optimum
