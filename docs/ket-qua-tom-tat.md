# Kết quả thí nghiệm, bảng tóm tắt

File này do `python -m ga.report` sinh ra từ các file CSV trong `results/`. Không sửa tay, muốn đổi số thì chạy lại thí nghiệm.

## 1. Thiết lập thí nghiệm

- Số lần lặp lại mỗi cấu hình: **30** seed khác nhau
- Ngân sách chung cho mọi thuật toán ngẫu nhiên: **9060 lần gọi hàm fitness**
- Cấu hình nền: quần thể 60, 150 thế hệ, chọn lọc tournament k = 3, lai ghép one_point p = 0.9, đột biến 1/n, tinh hoa 2, xử lý ràng buộc bằng repair
- Tổng thời gian chạy toàn bộ thí nghiệm: 906 giây

Bốn bộ dữ liệu:

| Bộ dữ liệu | Mô tả | Nghiệm tối ưu (quy hoạch động) |
|---|---|---|
| kp_small | kp_small [strongly_correlated]: n = 20 món, sức chứa W = 542 (bằng 50% tổng trọng lượng), lấy hết thì được 1285 điểm giá trị | 672 |
| kp_main | kp_main [strongly_correlated]: n = 100 món, sức chứa W = 2725 (bằng 50% tổng trọng lượng), lấy hết thì được 6451 điểm giá trị | 3395 |
| kp_easy | kp_easy [uncorrelated]: n = 100 món, sức chứa W = 2725 (bằng 50% tổng trọng lượng), lấy hết thì được 5686 điểm giá trị | 4328 |
| kp_large | kp_large [strongly_correlated]: n = 500 món, sức chứa W = 13505 (bằng 50% tổng trọng lượng), lấy hết thì được 32011 điểm giá trị | 16915 |

## 2. GA so với các thuật toán khác

Cùng một ngân sách đánh giá fitness. Cột lệch tối ưu càng nhỏ càng tốt, 0% nghĩa là tìm đúng nghiệm tối ưu.

**kp_small** (n = 20, lớp dữ liệu strongly_correlated)

| Thuật toán | Số lần chạy | Giá trị trung bình | Giá trị tốt nhất | Lệch tối ưu trung bình | Độ lệch chuẩn | Tỉ lệ chạm tối ưu | Thời gian |
|---|---|---|---|---|---|---|---|
| GA (di truyền) | 30 | 672.0 | 672 | 0.00% | 0.00 | 100% | 0.079s |
| Tham lam theo mật độ | 1 | 639.0 | 639 | 4.91% | 0.00 | 0% | 0.000s |
| Leo đồi lật bit | 30 | 671.9 | 672 | 0.02% | 0.06 | 90% | 0.042s |
| Tìm kiếm ngẫu nhiên | 30 | 671.2 | 672 | 0.12% | 0.17 | 63% | 0.106s |
| Vét cạn 2^n | 1 | 672.0 | 672 | 0.00% | 0.00 | 100% | 2.141s |
| Quy hoạch động (tối ưu) | 1 | 672.0 | 672 | 0.00% | 0.00 | 100% | 0.000s |

**kp_main** (n = 100, lớp dữ liệu strongly_correlated)

| Thuật toán | Số lần chạy | Giá trị trung bình | Giá trị tốt nhất | Lệch tối ưu trung bình | Độ lệch chuẩn | Tỉ lệ chạm tối ưu | Thời gian |
|---|---|---|---|---|---|---|---|
| GA (di truyền) | 30 | 3387.6 | 3395 | 0.22% | 0.24 | 40% | 0.246s |
| Tham lam theo mật độ | 1 | 3330.0 | 3330 | 1.91% | 0.00 | 0% | 0.000s |
| Leo đồi lật bit | 30 | 3297.5 | 3341 | 2.87% | 0.43 | 0% | 0.114s |
| Tìm kiếm ngẫu nhiên | 30 | 3301.1 | 3323 | 2.76% | 0.28 | 0% | 0.459s |
| Quy hoạch động (tối ưu) | 1 | 3395.0 | 3395 | 0.00% | 0.00 | 100% | 0.001s |

**kp_easy** (n = 100, lớp dữ liệu uncorrelated)

| Thuật toán | Số lần chạy | Giá trị trung bình | Giá trị tốt nhất | Lệch tối ưu trung bình | Độ lệch chuẩn | Tỉ lệ chạm tối ưu | Thời gian |
|---|---|---|---|---|---|---|---|
| GA (di truyền) | 30 | 4324.2 | 4328 | 0.09% | 0.10 | 37% | 0.248s |
| Tham lam theo mật độ | 1 | 4324.0 | 4324 | 0.09% | 0.00 | 0% | 0.000s |
| Leo đồi lật bit | 30 | 4327.4 | 4328 | 0.01% | 0.03 | 67% | 0.127s |
| Tìm kiếm ngẫu nhiên | 30 | 3726.0 | 3832 | 13.91% | 1.27 | 0% | 0.465s |
| Quy hoạch động (tối ưu) | 1 | 4328.0 | 4328 | 0.00% | 0.00 | 100% | 0.001s |

**kp_large** (n = 500, lớp dữ liệu strongly_correlated)

| Thuật toán | Số lần chạy | Giá trị trung bình | Giá trị tốt nhất | Lệch tối ưu trung bình | Độ lệch chuẩn | Tỉ lệ chạm tối ưu | Thời gian |
|---|---|---|---|---|---|---|---|
| GA (di truyền) | 30 | 16668.8 | 16733 | 1.46% | 0.18 | 0% | 1.077s |
| Tham lam theo mật độ | 1 | 16879.0 | 16879 | 0.21% | 0.00 | 0% | 0.000s |
| Leo đồi lật bit | 30 | 16125.4 | 16183 | 4.67% | 0.16 | 0% | 0.462s |
| Tìm kiếm ngẫu nhiên | 30 | 16195.3 | 16231 | 4.25% | 0.10 | 0% | 2.252s |
| Quy hoạch động (tối ưu) | 1 | 16915.0 | 16915 | 0.00% | 0.00 | 100% | 0.012s |

## 3. Ảnh hưởng của tham số

Mỗi bảng chỉ đổi đúng một tham số, mọi tham số còn lại giữ như cấu hình nền.

### 3.1. Kích thước quần thể (giữ nguyên tổng ngân sách đánh giá)

| Giá trị | Lệch tối ưu trung bình | Độ lệch chuẩn | Tỉ lệ chạm tối ưu | Thế hệ tìm ra nghiệm tốt nhất | Đa dạng cuối | Thời gian |
|---|---|---|---|---|---|---|
| 10 | 0.74% | 0.30 | 0% | 677 | 0.031 | 0.271s |
| 20 | 0.46% | 0.28 | 7% | 315 | 0.046 | 0.247s |
| 40 | 0.23% | 0.22 | 33% | 133 | 0.050 | 0.252s |
| 60 | 0.22% | 0.24 | 40% | 86 | 0.063 | 0.249s |
| 100 | 0.05% | 0.10 | 70% | 55 | 0.062 | 0.240s |
| 200 | 0.00% | 0.01 | 83% | 33 | 0.136 | 0.246s |

Tốt nhất: **200** (0.00%). Kém nhất: **10** (0.74%).

### 3.2. Tỉ lệ đột biến, theo bội số của mức chuẩn 1/n

| Giá trị | Lệch tối ưu trung bình | Độ lệch chuẩn | Tỉ lệ chạm tối ưu | Thế hệ tìm ra nghiệm tốt nhất | Đa dạng cuối | Thời gian |
|---|---|---|---|---|---|---|
| 0.0 | 2.28% | 0.50 | 0% | 10 | 0.000 | 0.236s |
| 0.5 | 1.09% | 0.48 | 3% | 106 | 0.027 | 0.248s |
| 1.0 | 0.22% | 0.24 | 40% | 86 | 0.063 | 0.239s |
| 2.0 | 0.02% | 0.06 | 73% | 87 | 0.196 | 0.241s |
| 5.0 | 0.48% | 0.20 | 0% | 106 | 0.486 | 0.249s |
| 10.0 | 1.27% | 0.29 | 0% | 104 | 0.736 | 0.255s |
| 30.0 | 2.47% | 0.20 | 0% | 92 | 0.945 | 0.259s |

Tốt nhất: **2.0** (0.02%). Kém nhất: **30.0** (2.47%).

### 3.3. Xác suất lai ghép

| Giá trị | Lệch tối ưu trung bình | Độ lệch chuẩn | Tỉ lệ chạm tối ưu | Thế hệ tìm ra nghiệm tốt nhất | Đa dạng cuối | Thời gian |
|---|---|---|---|---|---|---|
| 0.0 | 0.52% | 0.17 | 0% | 127 | 0.059 | 0.243s |
| 0.3 | 0.45% | 0.21 | 3% | 112 | 0.057 | 0.232s |
| 0.6 | 0.24% | 0.20 | 30% | 107 | 0.056 | 0.230s |
| 0.9 | 0.22% | 0.24 | 40% | 86 | 0.063 | 0.245s |
| 1.0 | 0.11% | 0.14 | 60% | 86 | 0.049 | 0.234s |

Tốt nhất: **1.0** (0.11%). Kém nhất: **0.0** (0.52%).

### 3.4. Kiểu lai ghép

| Giá trị | Lệch tối ưu trung bình | Độ lệch chuẩn | Tỉ lệ chạm tối ưu | Thế hệ tìm ra nghiệm tốt nhất | Đa dạng cuối | Thời gian |
|---|---|---|---|---|---|---|
| one_point | 0.22% | 0.24 | 40% | 86 | 0.063 | 0.246s |
| two_point | 0.13% | 0.18 | 63% | 76 | 0.055 | 0.266s |
| uniform | 0.02% | 0.07 | 90% | 41 | 0.053 | 0.309s |

Tốt nhất: **uniform** (0.02%). Kém nhất: **one_point** (0.22%).

### 3.5. Phương pháp chọn lọc

| Giá trị | Lệch tối ưu trung bình | Độ lệch chuẩn | Tỉ lệ chạm tối ưu | Thế hệ tìm ra nghiệm tốt nhất | Đa dạng cuối | Thời gian |
|---|---|---|---|---|---|---|
| tournament_k2 | 0.03% | 0.08 | 80% | 89 | 0.107 | 0.232s |
| tournament_k3 | 0.22% | 0.24 | 40% | 86 | 0.063 | 0.247s |
| tournament_k5 | 0.54% | 0.25 | 0% | 105 | 0.048 | 0.246s |
| tournament_k10 | 0.82% | 0.35 | 0% | 114 | 0.042 | 0.271s |
| roulette | 0.13% | 0.13 | 33% | 113 | 0.199 | 0.294s |
| rank | 0.06% | 0.11 | 77% | 91 | 0.117 | 0.308s |

Tốt nhất: **tournament_k2** (0.03%). Kém nhất: **tournament_k10** (0.82%).

### 3.6. Số cá thể tinh hoa

| Giá trị | Lệch tối ưu trung bình | Độ lệch chuẩn | Tỉ lệ chạm tối ưu | Thế hệ tìm ra nghiệm tốt nhất | Đa dạng cuối | Thời gian |
|---|---|---|---|---|---|---|
| 0 | 0.05% | 0.10 | 70% | 76 | 0.057 | 0.256s |
| 1 | 0.08% | 0.12 | 67% | 90 | 0.058 | 0.259s |
| 2 | 0.22% | 0.24 | 40% | 86 | 0.063 | 0.247s |
| 5 | 0.35% | 0.27 | 13% | 96 | 0.050 | 0.228s |
| 10 | 0.50% | 0.26 | 3% | 111 | 0.046 | 0.229s |

Tốt nhất: **0** (0.05%). Kém nhất: **10** (0.50%).

### 3.7. Cách xử lý ràng buộc sức chứa

| Giá trị | Lệch tối ưu trung bình | Độ lệch chuẩn | Tỉ lệ chạm tối ưu | Thế hệ tìm ra nghiệm tốt nhất | Đa dạng cuối | Thời gian |
|---|---|---|---|---|---|---|
| repair | 0.22% | 0.24 | 40% | 86 | 0.063 | 0.241s |
| penalty_0.5 | 4.71% | 0.47 | 0% | 0 | 0.058 | 0.253s |
| penalty_2 | 0.71% | 0.21 | 0% | 113 | 0.114 | 0.250s |
| penalty_10 | 1.27% | 0.30 | 0% | 128 | 0.119 | 0.243s |

Tốt nhất: **repair** (0.22%). Kém nhất: **penalty_0.5** (4.71%).

## 4. Tinh chỉnh bộ tham số

Ba bộ tham số, cùng một ngân sách khoảng 9060 lần đánh giá:

- **base**: quần thể 60 x 150 thế hệ, tournament k = 3, one_point p = 0.9, đột biến 1/n, tinh hoa 2
- **tuned_naive**: ghép cơ học giá trị tốt nhất của từng tham số trong mục 3, thành quần thể 200 x 44 thế hệ, tournament k = 2, uniform p = 1.0, đột biến 2/n, tinh hoa 1
- **tuned**: tổ hợp tốt nhất tìm được khi thử theo tổ hợp, quần thể 100 x 89 thế hệ, tournament k = 2, uniform p = 1.0, đột biến 1/n, tinh hoa 1

| Bộ dữ liệu | n | Cấu hình | Giá trị trung bình | Giá trị tốt nhất | Lệch tối ưu trung bình | Độ lệch chuẩn | Tỉ lệ chạm tối ưu | Tỉ lệ vượt tham lam |
|---|---|---|---|---|---|---|---|---|
| kp_main | 100 | base | 3387.6 | 3395 | 0.218% | 0.238 | 40% | 100% |
| kp_main | 100 | tuned_naive | 3384.2 | 3395 | 0.317% | 0.168 | 3% | 100% |
| kp_main | 100 | tuned | 3395.0 | 3395 | 0.000% | 0.000 | 100% | 100% |
| kp_large | 500 | base | 16668.8 | 16733 | 1.456% | 0.185 | 0% | 0% |
| kp_large | 500 | tuned_naive | 16705.6 | 16747 | 1.238% | 0.118 | 0% | 0% |
| kp_large | 500 | tuned | 16880.4 | 16905 | 0.204% | 0.067 | 0% | 50% |

Điểm đáng chú ý: cấu hình **tuned_naive** ghép từ các giá trị tốt nhất của từng tham số riêng lẻ lại cho kết quả tệ hơn cả cấu hình nền. Các tham số không độc lập với nhau, phải thử theo tổ hợp chứ không cộng dồn được.

## 5. Ngân sách tính toán trên bài n = 500

Tham lam đứng yên ở mức lệch 0.21% dù cho bao nhiêu thời gian cũng vậy, còn GA cải thiện dần theo ngân sách.

Bảng này dùng bộ toán tử của cấu hình nền, chỉ kéo dài số thế hệ. Đối chiếu với mục 4 sẽ thấy một điều đáng giá: cấu hình đã tinh chỉnh chỉ cần 9000 lần đánh giá đã đạt 0.20%, tức ngang với cấu hình nền khi được cấp 100000 lần đánh giá. Chỉnh tham số cho đúng tiết kiệm được hơn mười lần chi phí tính toán.

| Ngân sách đánh giá | Số thế hệ | Lệch tối ưu trung bình | Tốt nhất | Tỉ lệ vượt tham lam | Thời gian mỗi lần chạy |
|---|---|---|---|---|---|
| 9.000 | 89 | 1.53% | 1.41% | 0% | 1.10s |
| 30.000 | 299 | 0.38% | 0.30% | 0% | 3.69s |
| 100.000 | 999 | 0.14% | 0.12% | 100% | 11.78s |
| 300.000 | 2999 | 0.12% | 0.12% | 100% | 36.63s |

## 6. Khả năng mở rộng theo kích thước bài toán

GA giữ nguyên ngân sách 9060 lần đánh giá ở mọi kích thước, nên bài càng lớn thì mỗi điểm trong không gian càng ít được thăm dò.

| n | Không gian tìm kiếm | Lệch tối ưu của GA | Lệch tối ưu của tham lam | Tỉ lệ GA chạm tối ưu | Thời gian GA | Thời gian quy hoạch động |
|---|---|---|---|---|---|---|
| 20 | 2^20 | 0.00% | 6.32% | 100% | 0.09s | 0.3 ms |
| 50 | 2^50 | 0.30% | 0.96% | 50% | 0.15s | 0.4 ms |
| 100 | 2^100 | 0.42% | 0.06% | 0% | 0.24s | 1.1 ms |
| 200 | 2^200 | 0.62% | 0.39% | 0% | 0.45s | 2.9 ms |
| 500 | 2^500 | 1.45% | 0.33% | 0% | 1.10s | 12.7 ms |
| 1000 | 2^1000 | 2.38% | 0.12% | 0% | 2.23s | 56.0 ms |

---

Biểu đồ tương ứng nằm trong `results/figures/`, sinh bằng `python -m ga.plots`.
