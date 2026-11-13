"""Giải thuật di truyền (Genetic Algorithm) cho bài toán Cái túi 0/1.

Khung thuật toán (yêu cầu 2)
----------------------------
    1. Khởi tạo quần thể ngẫu nhiên gồm pop_size cá thể
    2. Lặp qua từng thế hệ:
         a. Đánh giá fitness toàn quần thể
         b. Giữ lại `elitism` cá thể tốt nhất (tinh hoa)
         c. Chọn lọc cha mẹ: tournament / roulette / rank
         d. Lai ghép với xác suất p_crossover
         e. Đột biến từng gene với xác suất p_mutation
         f. Thay thế quần thể cũ bằng quần thể con
    3. Dừng khi hết số thế hệ hoặc không cải thiện sau `stop_no_improve` thế hệ

Mỗi bước tách thành một hàm riêng để slide của TV2 và ví dụ tính tay của TV3
trỏ thẳng vào đúng một hàm trong mã nguồn.
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import asdict, dataclass, field
from typing import Callable, List, Optional, Sequence, Tuple

from .problem import EvalCounter, Evaluation, KnapsackInstance, evaluate

SELECTION_METHODS = ("tournament", "roulette", "rank")
CROSSOVER_METHODS = ("one_point", "two_point", "uniform")


@dataclass
class GAConfig:
    """Toàn bộ tham số của thuật toán, gom về một chỗ để dễ thí nghiệm."""

    pop_size: int = 60
    generations: int = 150
    selection: str = "tournament"
    tournament_k: int = 3
    crossover: str = "one_point"
    p_crossover: float = 0.9
    # p_mutation = None nghĩa là dùng mặc định 1/n, tức trung bình 1 gene bị lật
    # trên mỗi cá thể. Đây là mức khuyến nghị kinh điển cho mã hoá nhị phân.
    p_mutation: Optional[float] = None
    mutation_scale: float = 1.0       # hệ số nhân với 1/n khi p_mutation = None
    elitism: int = 2
    repair_mode: str = "repair"       # "repair" hoặc "penalty"
    penalty_coef: float = 2.0
    stop_no_improve: Optional[int] = None   # dừng sớm nếu không cải thiện
    seed: int = 0
    label: str = "default"

    def mutation_rate(self, n: int) -> float:
        if self.p_mutation is not None:
            return self.p_mutation
        return self.mutation_scale / n

    def as_row(self) -> dict:
        return asdict(self)


@dataclass
class GenStats:
    """Thống kê của một thế hệ, chính là dữ liệu để vẽ biểu đồ hội tụ."""

    generation: int
    best_fitness: float
    mean_fitness: float
    worst_fitness: float
    std_fitness: float
    best_value: int
    best_weight: int
    diversity: float        # độ đa dạng gene, 0 = cả quần thể giống hệt nhau
    unique: int             # số cá thể khác nhau trong quần thể
    evaluations: int        # tổng số lần gọi fitness tính tới thế hệ này
    elapsed: float          # giây kể từ lúc bắt đầu chạy


@dataclass
class GAResult:
    best_genes: List[int]
    best_value: int
    best_weight: int
    history: List[GenStats] = field(default_factory=list)
    generations_run: int = 0
    gen_to_best: int = 0          # thế hệ đầu tiên tìm ra nghiệm tốt nhất
    evaluations: int = 0
    runtime: float = 0.0
    config: Optional[GAConfig] = None

    @property
    def items(self) -> List[int]:
        return [i for i, g in enumerate(self.best_genes) if g]


# ---------------------------------------------------------------------------
# Các toán tử
# ---------------------------------------------------------------------------

def init_population(n: int, pop_size: int, rng: random.Random) -> List[List[int]]:
    """Khởi tạo ngẫu nhiên: mỗi gene nhận 0 hoặc 1 với xác suất bằng nhau.

    Với cái túi, khởi tạo 50/50 cho ra cá thể nặng khoảng gấp đôi sức chứa,
    nhưng thủ tục sửa chữa trong `evaluate` kéo chúng về vùng hợp lệ ngay ở
    thế hệ đầu tiên.
    """
    return [[rng.randint(0, 1) for _ in range(n)] for _ in range(pop_size)]


def select_tournament(
    pop: Sequence[Sequence[int]],
    fits: Sequence[float],
    k: int,
    rng: random.Random,
) -> List[int]:
    """Chọn k cá thể ngẫu nhiên rồi lấy cá thể khoẻ nhất trong nhóm đó.

    k càng lớn thì áp lực chọn lọc càng mạnh: hội tụ nhanh hơn nhưng dễ mất
    đa dạng và kẹt ở cực trị địa phương.
    """
    best = rng.randrange(len(pop))
    for _ in range(k - 1):
        challenger = rng.randrange(len(pop))
        if fits[challenger] > fits[best]:
            best = challenger
    return list(pop[best])


def select_roulette(
    pop: Sequence[Sequence[int]],
    fits: Sequence[float],
    rng: random.Random,
) -> List[int]:
    """Bánh xe roulette: xác suất được chọn tỉ lệ thuận với fitness.

    Fitness có thể âm khi dùng hình phạt nên phải dịch toàn bộ về không âm
    trước khi chia phần bánh xe.
    """
    shift = min(fits)
    adjusted = [f - shift + 1e-9 for f in fits]
    total = sum(adjusted)
    pick = rng.random() * total
    acc = 0.0
    for ind, w in zip(pop, adjusted):
        acc += w
        if acc >= pick:
            return list(ind)
    return list(pop[-1])


def select_rank(
    pop: Sequence[Sequence[int]],
    fits: Sequence[float],
    rng: random.Random,
) -> List[int]:
    """Chọn theo thứ hạng: xác suất tỉ lệ với hạng, không tỉ lệ với fitness.

    Nhờ vậy một siêu cá thể không chiếm gần hết bánh xe roulette, áp lực chọn
    lọc được giữ ổn định qua các thế hệ.
    """
    order = sorted(range(len(pop)), key=lambda i: fits[i])   # kém nhất mang hạng 1
    total = len(pop) * (len(pop) + 1) / 2
    pick = rng.random() * total
    acc = 0.0
    for rank, idx in enumerate(order, start=1):
        acc += rank
        if acc >= pick:
            return list(pop[idx])
    return list(pop[order[-1]])


def crossover_one_point(
    p1: Sequence[int], p2: Sequence[int], rng: random.Random
) -> Tuple[List[int], List[int]]:
    """Cắt tại một điểm rồi tráo đuôi của hai cha mẹ."""
    point = rng.randrange(1, len(p1))
    return list(p1[:point]) + list(p2[point:]), list(p2[:point]) + list(p1[point:])


def crossover_two_point(
    p1: Sequence[int], p2: Sequence[int], rng: random.Random
) -> Tuple[List[int], List[int]]:
    """Cắt tại hai điểm rồi tráo đoạn ở giữa."""
    a, b = sorted(rng.sample(range(1, len(p1)), 2))
    c1 = list(p1[:a]) + list(p2[a:b]) + list(p1[b:])
    c2 = list(p2[:a]) + list(p1[a:b]) + list(p2[b:])
    return c1, c2


def crossover_uniform(
    p1: Sequence[int], p2: Sequence[int], rng: random.Random
) -> Tuple[List[int], List[int]]:
    """Mỗi vị trí gene tung một đồng xu để lấy gene của cha hay của mẹ."""
    c1: List[int] = []
    c2: List[int] = []
    for g1, g2 in zip(p1, p2):
        if rng.random() < 0.5:
            c1.append(g1)
            c2.append(g2)
        else:
            c1.append(g2)
            c2.append(g1)
    return c1, c2


def mutate(genes: List[int], p_mutation: float, rng: random.Random) -> int:
    """Đột biến lật bit ngay trên cá thể. Trả về số gene đã bị lật."""
    flips = 0
    for i in range(len(genes)):
        if rng.random() < p_mutation:
            genes[i] ^= 1
            flips += 1
    return flips


# ---------------------------------------------------------------------------
# Vòng lặp chính
# ---------------------------------------------------------------------------

def population_diversity(pop: Sequence[Sequence[int]]) -> float:
    """Độ đa dạng = trung bình của 4 * p * (1 - p) trên từng vị trí gene.

    p là tỉ lệ cá thể mang bit 1 tại vị trí đó. Giá trị 1.0 là đa dạng tối đa
    (nửa quần thể mang 0, nửa mang 1), 0.0 là cả quần thể trùng nhau hoàn toàn.
    Đây là chỉ số dùng để chứng minh hiện tượng hội tụ sớm.
    """
    if not pop:
        return 0.0
    m = len(pop)
    n = len(pop[0])
    acc = 0.0
    for i in range(n):
        p = sum(ind[i] for ind in pop) / m
        acc += 4.0 * p * (1.0 - p)
    return acc / n


def _std(values: Sequence[float], mean: float) -> float:
    if len(values) < 2:
        return 0.0
    return math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))


def run_ga(
    inst: KnapsackInstance,
    config: GAConfig,
    on_generation: Optional[Callable[[GenStats, List[int]], None]] = None,
) -> GAResult:
    """Chạy GA trên một thể hiện, trả về nghiệm tốt nhất kèm toàn bộ lịch sử.

    `on_generation` là hook để phần demo in ra màn hình theo từng thế hệ.
    """
    if config.selection not in SELECTION_METHODS:
        raise ValueError(f"selection không hợp lệ: {config.selection}")
    if config.crossover not in CROSSOVER_METHODS:
        raise ValueError(f"crossover không hợp lệ: {config.crossover}")
    if config.elitism >= config.pop_size:
        raise ValueError("elitism phải nhỏ hơn pop_size")

    rng = random.Random(config.seed)
    counter = EvalCounter()
    n = inst.n
    p_mut = config.mutation_rate(n)
    t0 = time.perf_counter()
    # Thời gian nằm trong hook hiển thị không phải là thời gian của thuật toán.
    # Phần demo cố ý in chậm lại cho người xem kịp đọc, nếu tính luôn vào đây
    # thì con số thời gian chạy báo cáo ra sẽ sai hoàn toàn.
    hook_time = 0.0

    pop = init_population(n, config.pop_size, rng)
    history: List[GenStats] = []

    best_genes: List[int] = [0] * n
    best_value = -1
    best_weight = 0
    gen_to_best = 0
    no_improve = 0

    for gen in range(config.generations + 1):
        # (a) Đánh giá cả quần thể. Với chế độ repair, cá thể được thay bằng
        #     bản đã sửa chữa để quần thể luôn nằm trong vùng hợp lệ.
        evals: List[Evaluation] = []
        for idx, ind in enumerate(pop):
            ev = evaluate(inst, ind, config.repair_mode, config.penalty_coef, counter)
            if config.repair_mode == "repair":
                pop[idx] = ev.genes
            evals.append(ev)

        fits = [e.fitness for e in evals]
        mean_fit = sum(fits) / len(fits)
        champion = max(range(len(pop)), key=lambda i: fits[i])

        # Nghiệm trả về phải là cá thể hợp lệ tốt nhất từng gặp, không phải cá
        # thể có fitness cao nhất. Hai thứ này khác nhau ở chế độ phạt điểm:
        # một cá thể vượt sức chứa vẫn có thể có fitness cao hơn mọi cá thể hợp
        # lệ, nhưng nó không phải lời giải dùng được.
        improved = False
        for idx, ev in enumerate(evals):
            if ev.feasible and ev.value > best_value:
                best_value = ev.value
                best_weight = ev.weight
                best_genes = list(pop[idx])
                gen_to_best = gen
                improved = True

        stats = GenStats(
            generation=gen,
            best_fitness=fits[champion],
            mean_fitness=mean_fit,
            worst_fitness=min(fits),
            std_fitness=_std(fits, mean_fit),
            best_value=best_value,
            best_weight=best_weight,
            diversity=population_diversity(pop),
            unique=len({tuple(ind) for ind in pop}),
            evaluations=counter.count,
            elapsed=time.perf_counter() - t0 - hook_time,
        )
        history.append(stats)
        if on_generation is not None:
            t_hook = time.perf_counter()
            on_generation(stats, best_genes)
            hook_time += time.perf_counter() - t_hook

        no_improve = 0 if improved else no_improve + 1
        if config.stop_no_improve is not None and no_improve >= config.stop_no_improve:
            break
        if gen == config.generations:
            break

        # (b) Tinh hoa: sao chép nguyên vẹn các cá thể tốt nhất sang thế hệ sau.
        ranked = sorted(range(len(pop)), key=lambda i: fits[i], reverse=True)
        children: List[List[int]] = [list(pop[i]) for i in ranked[: config.elitism]]

        # (c, d, e) Sinh phần còn lại bằng chọn lọc, lai ghép rồi đột biến.
        while len(children) < config.pop_size:
            if config.selection == "tournament":
                p1 = select_tournament(pop, fits, config.tournament_k, rng)
                p2 = select_tournament(pop, fits, config.tournament_k, rng)
            elif config.selection == "roulette":
                p1 = select_roulette(pop, fits, rng)
                p2 = select_roulette(pop, fits, rng)
            else:
                p1 = select_rank(pop, fits, rng)
                p2 = select_rank(pop, fits, rng)

            if rng.random() < config.p_crossover:
                if config.crossover == "one_point":
                    c1, c2 = crossover_one_point(p1, p2, rng)
                elif config.crossover == "two_point":
                    c1, c2 = crossover_two_point(p1, p2, rng)
                else:
                    c1, c2 = crossover_uniform(p1, p2, rng)
            else:
                c1, c2 = list(p1), list(p2)

            mutate(c1, p_mut, rng)
            mutate(c2, p_mut, rng)
            children.append(c1)
            if len(children) < config.pop_size:
                children.append(c2)

        pop = children

    return GAResult(
        best_genes=best_genes,
        best_value=best_value,
        best_weight=best_weight,
        history=history,
        generations_run=history[-1].generation,
        gen_to_best=gen_to_best,
        evaluations=counter.count,
        runtime=time.perf_counter() - t0 - hook_time,
        config=config,
    )
