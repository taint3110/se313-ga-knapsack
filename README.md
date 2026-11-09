# Giải thuật tiến hoá và ứng dụng: bài toán Cái túi 0/1

Mã nguồn seminar môn **SE313 - Một số thuật toán thông minh**, UIT.

Chương trình cài đặt giải thuật di truyền (Genetic Algorithm) để giải bài toán
Cái túi 0/1, chạy thí nghiệm so sánh với bốn thuật toán khác, xuất dữ liệu ra
CSV và vẽ biểu đồ.

## 1. Cài đặt

Cần Python 3.10 trở lên.

```bash
pip install -r requirements.txt
```

Phần lõi thuật toán không phụ thuộc thư viện ngoài. `numpy` chỉ để tăng tốc
bảng quy hoạch động, `matplotlib` chỉ để vẽ biểu đồ.

## 2. Bốn lệnh cần nhớ

```bash
python demo.py                  # demo chạy trên lớp, 5 cảnh nối tiếp nhau
python -m ga.hand_example       # ví dụ tính tay 6 món, 2 thế hệ, in bảng markdown
python -m ga.experiments        # chạy toàn bộ thí nghiệm, xuất CSV vào results/
python -m ga.plots              # vẽ biểu đồ từ CSV vào results/figures/
python -m ga.report             # gom CSV thành bảng tóm tắt docs/ket-qua-tom-tat.md
```

Thứ tự bắt buộc: `experiments` chạy trước, rồi mới tới `plots` và `report`.

Hai lệnh phụ trong `tools/`, đóng gói lại cho người xem:

```bash
python tools/make_charts_deck.py  # 10 biểu đồ thành PDF, ảnh rời và ảnh động
python tools/make_demo_video.py   # ghi phần demo thành MP4, ảnh động và bản chữ
```

Vài tham số hay dùng khi demo trên lớp:

```bash
python demo.py --slow                      # chậm lại, hợp để quay video
python demo.py --instance kp_small         # bài n = 20, chạy được cả vét cạn
python demo.py --pop 10 --mutation-scale 0 # cố ý để tham số kém, cho thấy hội tụ sớm
python demo.py --no-pause                  # chạy một mạch, không chờ Enter
```

## 3. Cấu trúc thư mục

```
demo.py                  demo trình chiếu, phần của TV4
ga/problem.py            dữ liệu bài toán, cách mã hoá, hàm fitness
ga/algorithm.py          GA: khởi tạo, chọn lọc, lai ghép, đột biến, tinh hoa
ga/baselines.py          vét cạn, quy hoạch động, tham lam, leo đồi, ngẫu nhiên
ga/experiments.py        chạy thí nghiệm, xuất CSV
ga/plots.py              vẽ biểu đồ từ CSV
ga/report.py             gom CSV thành bảng markdown
ga/hand_example.py       ví dụ tính tay từng bước, phần của TV3
tools/make_charts_deck.py  đóng biểu đồ thành PDF, ảnh rời và ảnh động
tools/make_demo_video.py   ghi phần demo thành MP4, ảnh động và bản chữ
data/                      bốn bộ dữ liệu dạng JSON
results/                   CSV kết quả thô và bảng tổng hợp
results/figures/           10 biểu đồ PNG
results/slides/            10 trang biểu đồ kèm chú thích, dạng PNG
results/demo.mp4           bản ghi hình phần demo, không tiếng, tua được
docs/                      tài liệu bàn giao cho từng thành viên
```

## 4. Bài toán và cách mã hoá

**Phát biểu.** Cho `n` món đồ, món thứ `i` có giá trị `v_i` và trọng lượng
`w_i`. Túi chịu được tối đa `W`. Chọn tập món có tổng giá trị lớn nhất mà tổng
trọng lượng không vượt `W`.

**Nhiễm sắc thể.** Chuỗi nhị phân dài `n`, `gene[i] = 1` nghĩa là mang món `i`.
Không gian tìm kiếm `2^n`, với `n = 100` là `1.27e30` phương án.

**Fitness.** Bằng tổng giá trị của các món được chọn. Cá thể vượt sức chứa được
xử lý theo một trong hai cách, chọn bằng tham số `repair_mode`:

- `repair`: bỏ dần món có mật độ giá trị `v_i/w_i` thấp nhất cho tới khi vừa
  túi. Mọi cá thể luôn hợp lệ. Đây là mặc định.
- `penalty`: giữ nguyên cá thể, fitness bị trừ `penalty_coef * (weight - W)`.

**Bộ dữ liệu.** Lớp `strongly_correlated` (`v_i = w_i + 10`) là lớp khó kinh
điển: mọi món có mật độ gần như nhau nên tham lam mất phương hướng. Lớp
`uncorrelated` dễ hơn nhiều, dùng để đối chứng.

## 5. Tham số của thuật toán

Tất cả nằm trong `GAConfig` (`ga/algorithm.py`):

| Tham số | Mặc định | Ý nghĩa |
|---|---|---|
| `pop_size` | 60 | số cá thể trong quần thể |
| `generations` | 150 | số thế hệ |
| `selection` | `tournament` | `tournament`, `roulette` hoặc `rank` |
| `tournament_k` | 3 | số cá thể tham gia mỗi vòng đấu |
| `crossover` | `one_point` | `one_point`, `two_point` hoặc `uniform` |
| `p_crossover` | 0.9 | xác suất lai ghép một cặp cha mẹ |
| `p_mutation` | `None` | để `None` là dùng mức chuẩn `1/n` |
| `mutation_scale` | 1.0 | bội số nhân với `1/n` |
| `elitism` | 2 | số cá thể tốt nhất được chép thẳng sang thế hệ sau |
| `repair_mode` | `repair` | cách xử lý cá thể vượt sức chứa |
| `stop_no_improve` | `None` | dừng sớm sau bao nhiêu thế hệ không cải thiện |
| `seed` | 0 | hạt giống ngẫu nhiên, cùng seed cho kết quả giống hệt |

## 6. Cách so sánh cho công bằng

GA, leo đồi và tìm kiếm ngẫu nhiên đều nhận **cùng một ngân sách số lần gọi hàm
fitness** (mặc định `60 x 151 = 9060`). Nếu chỉ so theo thời gian hoặc theo số
vòng lặp thì mỗi thuật toán một đơn vị, không so được.

Quy hoạch động `O(n*W)` cho nghiệm tối ưu tuyệt đối, dùng làm mốc để tính
khoảng cách `gap = (tối ưu - nghiệm tìm được) / tối ưu`. Với `n <= 20` còn chạy
thêm vét cạn `2^n` để chứng minh quy hoạch động đúng.

## 7. Tài liệu đi kèm

| File | Dành cho |
|---|---|
| `docs/ban-giao-cho-tv5.md` | TV5: dữ liệu nào vẽ biểu đồ nào, dàn ý Kết quả và Nhận xét |
| `docs/ket-qua-tom-tat.md` | bảng số liệu tổng hợp, sinh tự động từ CSV |
| `docs/vi-du-tinh-tay.md` | TV3: ví dụ tính tay từng bước, sinh tự động |
| `docs/kich-ban-quay-video.md` | TV4: kịch bản quay video demo dự phòng |
| `docs/cau-hoi-thuong-gap.md` | cả nhóm: câu hỏi giảng viên hay hỏi và cách trả lời |
| `results/bieu-do-tung-hinh.pdf` | 10 trang biểu đồ kèm nguồn dữ liệu và câu kết luận |
| `results/slides/` | từng trang trên dạng PNG rời, chèn thẳng vào slide |
| `results/demo.mp4` | bản ghi hình phần demo, dùng khi máy chiếu trục trặc |
| `results/demo-transcript.txt` | toàn bộ chữ phần demo in ra, để đọc lại hoặc đưa vào phụ lục |

## 8. Tái lập kết quả

Mọi con số trong báo cáo đều tái lập được: cùng `seed` thì cùng kết quả. Thí
nghiệm mặc định lặp lại 30 seed cho mỗi cấu hình và báo cáo trung bình kèm độ
lệch chuẩn, vì một lần chạy đẹp của thuật toán ngẫu nhiên không chứng minh được
điều gì.

```bash
python -m ga.experiments --quick        # 5 seed, khoảng 2 phút, dùng để thử
python -m ga.experiments --seeds 30     # mặc định đầy đủ
```
