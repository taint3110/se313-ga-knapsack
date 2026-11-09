"""Ghi hình phần demo thành video MP4, không cần phần mềm quay màn hình.

Chạy `demo.py`, bắt toàn bộ những gì nó in ra, rồi vẽ lại từng dòng lên ảnh
theo kiểu gõ dần.

    python tools/make_demo_video.py

Xuất ra ba thứ:

    results/demo.mp4             bản chính, dừng và tua được
    results/demo.gif             bản chạy tự động, để chèn vào chat cho nhanh
    results/demo-transcript.txt  toàn bộ chữ, để đọc lại hoặc đưa vào phụ lục

Dùng làm bản dự phòng khi máy chiếu trục trặc, và để gửi cho cả nhóm xem
trước. Bản ghi này không có tiếng, muốn có lời dẫn thì quay lại theo
docs/kich-ban-quay-video.md.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT_FILE = ROOT / "results" / "demo.gif"

# Giao diện ảnh
BG = (18, 18, 20)
FG = (222, 222, 216)
DIM_FG = (124, 124, 118)
PALETTE_256 = {33: (58, 135, 229), 208: (235, 104, 52), 35: (27, 175, 122)}
MARGIN = 22
LINE_H = 22
FONT_SIZE = 16
COLS = 92
VIEWPORT = 32

ANSI = re.compile(r"\033\[([0-9;]*)m")


def find_mono_font() -> ImageFont.FreeTypeFont:
    """Lấy font chữ đều có đủ dấu tiếng Việt.

    Consolas và Cascadia Mono của Windows có đủ bộ chữ Latinh mở rộng, còn
    DejaVu Sans Mono đi kèm matplotlib thì thiếu một số chữ có dấu như ế, ộ, ạ
    nên chỉ dùng làm phương án cuối.
    """
    candidates = [
        Path("C:/Windows/Fonts/consola.ttf"),
        Path("C:/Windows/Fonts/CascadiaMono.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
    ]
    try:
        import matplotlib

        candidates.append(
            Path(matplotlib.get_data_path()) / "fonts" / "ttf" / "DejaVuSansMono.ttf"
        )
    except ImportError:
        pass
    for path in candidates:
        if path.exists():
            font = ImageFont.truetype(str(path), FONT_SIZE)
            if font.getmask("ế").getbbox() is not None:
                return font
    raise SystemExit("Không tìm thấy font chữ đều nào có đủ dấu tiếng Việt")


def parse_ansi(line: str) -> List[Tuple[str, Tuple[int, int, int]]]:
    """Tách một dòng có mã màu ANSI thành các đoạn (chữ, màu)."""
    spans: List[Tuple[str, Tuple[int, int, int]]] = []
    colour = FG
    pos = 0
    for m in ANSI.finditer(line):
        if m.start() > pos:
            spans.append((line[pos:m.start()], colour))
        codes = [c for c in m.group(1).split(";") if c]
        if not codes or codes[0] == "0":
            colour = FG
        elif codes[0] == "2":
            colour = DIM_FG
        elif codes[0] == "1":
            colour = (255, 255, 255)
        elif codes[0] == "38" and len(codes) >= 3 and codes[1] == "5":
            colour = PALETTE_256.get(int(codes[2]), FG)
        pos = m.end()
    if pos < len(line):
        spans.append((line[pos:], colour))
    return spans


def capture_demo(extra_args: List[str]) -> List[str]:
    """Chạy demo.py và lấy về từng dòng nó in ra."""
    cmd = [sys.executable, str(ROOT / "demo.py"), "--no-pause", *extra_args]
    proc = subprocess.run(
        cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        raise SystemExit(f"demo.py lỗi, mã thoát {proc.returncode}")
    return proc.stdout.splitlines()


def render(lines: List[str], font: ImageFont.FreeTypeFont, cols: int) -> Image.Image:
    char_w = font.getlength("M")
    width = int(MARGIN * 2 + char_w * cols)
    height = MARGIN * 2 + LINE_H * VIEWPORT
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)
    for row, line in enumerate(lines[-VIEWPORT:]):
        x = MARGIN
        y = MARGIN + row * LINE_H
        for text, colour in parse_ansi(line):
            draw.text((x, y), text, font=font, fill=colour)
            x += font.getlength(text)
    return img


def write_mp4(frames: List[Image.Image], durations: List[int], out: Path,
              fps: int = 10) -> None:
    """Xuất video MP4, mỗi khung hình giữ đúng số giây như bản ảnh động.

    Người xem dừng lại, tua tới tua lui được, và gửi qua Zalo hay Drive cũng
    nhẹ hơn ảnh động nhiều.
    """
    import imageio.v2 as imageio
    import numpy as np

    writer = imageio.get_writer(
        out, fps=fps, codec="libx264", quality=8, macro_block_size=1,
        ffmpeg_params=["-pix_fmt", "yuv420p"],   # để Windows và điện thoại mở được
    )
    try:
        for frame, duration in zip(frames, durations):
            repeat = max(1, round(duration / 1000 * fps))
            data = np.asarray(frame)
            for _ in range(repeat):
                writer.append_data(data)
    finally:
        writer.close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Ghi phần demo thành video MP4, ảnh động và bản chữ"
    )
    parser.add_argument("--out", default=str(OUT_FILE))
    parser.add_argument("--no-gif", action="store_true",
                        help="chỉ xuất MP4 và bản chữ")
    parser.add_argument("--demo-args", nargs=argparse.REMAINDER, default=[],
                        help="tham số truyền thẳng cho demo.py")
    args = parser.parse_args(argv)

    print("Đang chạy demo.py để lấy nội dung ...")
    raw_lines = capture_demo(args.demo_args)

    # Bản chữ để đọc theo nhịp của mình, không phải xem lại cả đoạn phim.
    transcript = Path(args.out).with_name("demo-transcript.txt")
    transcript.parent.mkdir(parents=True, exist_ok=True)
    transcript.write_text(
        "\n".join(ANSI.sub("", line) for line in raw_lines) + "\n", encoding="utf-8"
    )
    print(f"Đã ghi {transcript.name}")

    font = find_mono_font()
    # Khung hình phải đủ rộng cho dòng dài nhất, nếu không bảng sẽ bị cắt mất đuôi.
    cols = max(COLS, max(len(ANSI.sub("", line)) for line in raw_lines) + 2)

    frames: List[Image.Image] = []
    durations: List[int] = []
    shown: List[str] = []
    for line in raw_lines:
        shown.append(line)
        frames.append(render(shown, font, cols))
        plain = ANSI.sub("", line)
        if plain.startswith("  CẢNH"):
            durations.append(1400)      # dừng lâu ở tiêu đề mỗi cảnh
        elif not plain.strip():
            durations.append(120)
        else:
            durations.append(260)
    durations[-1] = 4000                # giữ khung cuối để kịp đọc bảng so sánh

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    total = sum(durations) / 1000

    mp4 = out.with_suffix(".mp4")
    write_mp4(frames, durations, mp4)
    print(f"Đã ghi {mp4.name} ({total:.0f} giây, "
          f"{mp4.stat().st_size / 1e6:.1f} MB)")

    if not args.no_gif:
        frames[0].save(
            out,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            optimize=True,
        )
        print(f"Đã ghi {out.name} ({len(frames)} khung hình, {total:.0f} giây, "
              f"{out.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main())
