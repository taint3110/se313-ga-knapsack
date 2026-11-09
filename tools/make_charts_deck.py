"""Đóng 10 biểu đồ thành một tập trang để đi qua số liệu, phần dành cho TV5.

Mỗi trang gồm một biểu đồ kèm dải chú thích ghi rõ ba thứ: hình này nói điều
gì, lấy số liệu từ file CSV nào, và câu kết luận nên viết trong báo cáo.

    python tools/make_charts_deck.py

Xuất ra ba dạng, dùng cho ba nhu cầu khác nhau:

    results/bieu-do-tung-hinh.pdf    lật từng trang, phóng to, in ra được
    results/slides/trang-01..10.png  từng trang rời, chèn thẳng vào slide
    results/bieu-do-tung-hinh.gif    chạy tự động, chỉ để xem lướt

Bản PDF là bản chính. Ảnh động không dừng và không tua được nên chỉ hợp để
xem qua một lượt cho biết có những gì.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FIGURES = ROOT / "results" / "figures"
RESULTS = ROOT / "results"

CANVAS_W = 1180
CANVAS_H = 900
MARGIN = 26
SECONDS_PER_SLIDE = 9

BG = (255, 255, 255)
INK = (11, 11, 11)
INK_SOFT = (82, 81, 78)
BLUE = (42, 120, 214)
RULE = (222, 220, 214)

# (tên file, tiêu đề, nguồn dữ liệu, câu kết luận)
SLIDES: List[Tuple[str, str, str, str]] = [
    (
        "fig1_hoi_tu.png",
        "Hình 1. Đường hội tụ qua 150 thế hệ",
        "convergence.csv, cột generation, best_value, mean_fitness, gap_percent",
        "GA vượt mốc tham lam ngay trong khoảng 10 thế hệ đầu rồi cải thiện chậm "
        "dần. Đường tốt nhất không bao giờ đi xuống nhờ cơ chế tinh hoa.",
    ),
    (
        "fig2_da_dang.png",
        "Hình 2. Quần thể mất dần đa dạng",
        "convergence.csv, cột diversity, unique",
        "Độ đa dạng gene rơi từ 0.97 xuống dưới 0.10 chỉ sau khoảng 30 thế hệ. "
        "Đây là bằng chứng định lượng cho hiện tượng hội tụ sớm.",
    ),
    (
        "fig3_so_sanh_thuat_toan.png",
        "Hình 3. GA so với tham lam, leo đồi và ngẫu nhiên",
        "summary_baselines.csv, cột gap_percent_mean và gap_percent_std",
        "Hình quan trọng nhất của phần kết quả. Cùng ngân sách đánh giá, GA thắng "
        "rõ ở lớp dữ liệu khó nhưng thua tham lam ở bài n = 500.",
    ),
    (
        "fig4_kich_thuoc_quan_the.png",
        "Hình 4. Kích thước quần thể",
        "summary_params.csv lọc experiment = pop_size",
        "Tổng ngân sách đánh giá được giữ nguyên nên quần thể lớn phải chạy ít thế "
        "hệ hơn. Dù vậy quần thể lớn vẫn cho kết quả tốt hơn hẳn.",
    ),
    (
        "fig5_dot_bien.png",
        "Hình 5. Tỉ lệ đột biến",
        "summary_params.csv lọc experiment = mutation_scale",
        "Đường cong hình chữ U. Tắt đột biến thì quần thể cạn đa dạng, đột biến "
        "quá mạnh thì GA thoái hoá thành tìm kiếm ngẫu nhiên.",
    ),
    (
        "fig6_toan_tu.png",
        "Hình 6. Bốn toán tử của thuật toán",
        "summary_params.csv lọc crossover, p_crossover, selection, elitism",
        "Lai ghép đều tốt nhất vì mã hoá nhị phân của bài cái túi không có liên kết "
        "vị trí. Áp lực chọn lọc quá mạnh làm mất đa dạng sớm.",
    ),
    (
        "fig7_rang_buoc.png",
        "Hình 7. Cách xử lý ràng buộc sức chứa",
        "summary_params.csv lọc experiment = constraint",
        "Sửa chữa cá thể tốt hơn phạt điểm. Hệ số phạt quá nhẹ còn kéo cả quần thể "
        "trôi ra ngoài vùng hợp lệ.",
    ),
    (
        "fig8_tinh_chinh_tham_so.png",
        "Hình 8. Ba bộ tham số, cùng một ngân sách",
        "summary_tuned.csv, cột gap_percent_mean, gap_percent_std, success_rate",
        "Ghép cơ học các giá trị tốt nhất của từng tham số lại cho kết quả tệ hơn "
        "cả cấu hình nền. Tham số của GA tương tác với nhau, không cộng dồn được.",
    ),
    (
        "fig9_ngan_sach.png",
        "Hình 9. Tăng ngân sách tính toán trên bài n = 500",
        "summary_budget.csv và budget.csv",
        "Tham lam đứng yên mãi ở một con số, còn GA cho thêm thời gian là cho "
        "nghiệm tốt hơn. Đây là điểm mạnh cốt lõi của thuật toán xấp xỉ.",
    ),
    (
        "fig10_mo_rong.png",
        "Hình 10. Khả năng mở rộng theo kích thước bài toán",
        "summary_scalability.csv",
        "Với ngân sách cố định, sai lệch của GA tăng dần theo n. Thời gian chạy "
        "tăng tuyến tính theo n.",
    ),
]


def load_fonts():
    """Ưu tiên font có đủ dấu tiếng Việt."""
    families = [
        ("C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/segoeui.ttf"),
        ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"),
    ]
    for bold, regular in families:
        if Path(bold).exists() and Path(regular).exists():
            return (ImageFont.truetype(bold, 26),
                    ImageFont.truetype(regular, 18),
                    ImageFont.truetype(regular, 17))
    try:
        import matplotlib

        base = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
        return (ImageFont.truetype(str(base / "DejaVuSans-Bold.ttf"), 26),
                ImageFont.truetype(str(base / "DejaVuSans.ttf"), 18),
                ImageFont.truetype(str(base / "DejaVuSans.ttf"), 17))
    except ImportError:
        raise SystemExit("Không tìm thấy font nào để vẽ chú thích")


def wrap(draw, text: str, font, width: int) -> List[str]:
    """Ngắt dòng theo bề rộng thật của chữ chứ không theo số ký tự."""
    words = text.split()
    lines: List[str] = []
    current = ""
    for word in words:
        probe = f"{current} {word}".strip()
        if draw.textlength(probe, font=font) <= width:
            current = probe
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def build_slide(path: Path, title: str, source: str, takeaway: str, fonts) -> Image.Image:
    """Dựng một khung hình: tiêu đề, nguồn dữ liệu, biểu đồ, câu kết luận.

    Mọi khung hình cùng một kích thước cố định, biểu đồ được thu phóng vừa
    khoảng trống còn lại rồi căn giữa, để khi chuyển hình không bị giật.
    """
    font_title, font_body, font_source = fonts
    chart = Image.open(path).convert("RGB")
    inner = CANVAS_W - 2 * MARGIN

    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    source_lines = wrap(probe, f"Nguồn: {source}", font_source, inner)
    takeaway_lines = wrap(probe, takeaway, font_body, inner)

    header = MARGIN + 38 + len(source_lines) * 24 + 16
    footer = 14 + 12 + len(takeaway_lines) * 26 + MARGIN
    available = CANVAS_H - header - footer
    scale = min(inner / chart.width, available / chart.height)
    chart = chart.resize((round(chart.width * scale), round(chart.height * scale)),
                         Image.LANCZOS)

    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
    draw = ImageDraw.Draw(canvas)

    y = MARGIN
    draw.text((MARGIN, y), title, font=font_title, fill=INK)
    y += 38
    for line in source_lines:
        draw.text((MARGIN, y), line, font=font_source, fill=BLUE)
        y += 24

    chart_y = header + (available - chart.height) // 2
    canvas.paste(chart, ((CANVAS_W - chart.width) // 2, chart_y))

    y = CANVAS_H - footer + 14
    draw.line([(MARGIN, y), (CANVAS_W - MARGIN, y)], fill=RULE, width=1)
    y += 12
    for line in takeaway_lines:
        draw.text((MARGIN, y), line, font=font_body, fill=INK_SOFT)
        y += 26
    return canvas


def size_mb(path: Path) -> str:
    return f"{path.stat().st_size / 1e6:.1f} MB"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Đóng biểu đồ thành PDF, ảnh rời và ảnh động"
    )
    parser.add_argument("--out-dir", default=str(RESULTS))
    parser.add_argument("--seconds", type=float, default=SECONDS_PER_SLIDE,
                        help="số giây mỗi trang trong bản ảnh động")
    parser.add_argument("--no-gif", action="store_true",
                        help="chỉ xuất PDF và ảnh rời")
    args = parser.parse_args(argv)

    fonts = load_fonts()
    pages: List[Image.Image] = []
    for name, title, source, takeaway in SLIDES:
        path = FIGURES / name
        if not path.exists():
            raise SystemExit(f"Thiếu {path}. Chạy `python -m ga.plots` trước.")
        pages.append(build_slide(path, title, source, takeaway, fonts))
        print(f"  + {name}")

    out_dir = Path(args.out_dir)
    slides_dir = out_dir / "slides"
    slides_dir.mkdir(parents=True, exist_ok=True)

    # Bản chính: PDF nhiều trang, lật tới lui và phóng to thoải mái.
    pdf = out_dir / "bieu-do-tung-hinh.pdf"
    pages[0].save(pdf, save_all=True, append_images=pages[1:], resolution=150.0)
    print(f"Đã ghi {pdf.name} ({len(pages)} trang, {size_mb(pdf)})")

    # Từng trang rời để chèn vào slide báo cáo.
    for i, page in enumerate(pages, start=1):
        page.save(slides_dir / f"trang-{i:02d}.png", optimize=True)
    print(f"Đã ghi {len(pages)} ảnh rời vào {slides_dir.name}/")

    if not args.no_gif:
        gif = out_dir / "bieu-do-tung-hinh.gif"
        pages[0].save(
            gif,
            save_all=True,
            append_images=pages[1:],
            duration=int(args.seconds * 1000),
            loop=0,
            optimize=True,
        )
        print(f"Đã ghi {gif.name} ({len(pages) * args.seconds:.0f} giây, "
              f"{size_mb(gif)})")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main())
