# Ví dụ tính tay từng bước của giải thuật di truyền

File này do `python -m ga.hand_example` sinh ra, mọi con số trong đây đều lấy thẳng từ mã nguồn chứ không nhập tay.

Tham số: quần thể 6 cá thể, 2 thế hệ, chọn lọc bánh xe roulette, lai ghép một điểm với xác suất 100%, đột biến mỗi gene với xác suất 15%, giữ lại 1 cá thể tinh hoa, seed = 97.

## Bài toán dùng cho ví dụ

Sức chứa của túi **W = 12**, có 6 món đồ:

| Món i | Giá trị v_i | Trọng lượng w_i | Mật độ v_i/w_i |
|---|---|---|---|
| 0 | 8 | 3 | 2.67 |
| 1 | 7 | 4 | 1.75 |
| 2 | 9 | 5 | 1.80 |
| 3 | 4 | 2 | 2.00 |
| 4 | 12 | 6 | 2.00 |
| 5 | 2 | 1 | 2.00 |

Vét cạn toàn bộ 2^6 = 64 phương án cho biết nghiệm tối ưu là **26** với tổ hợp `100111` (trọng lượng 12/12). Con số này chỉ dùng để đối chiếu, bản thân GA không biết trước.

Cách mã hoá: nhiễm sắc thể là chuỗi 6 bit, bit thứ i bằng 1 nghĩa là mang món i theo. Ví dụ `101001` nghĩa là mang món 0, 2 và 5.

## Thế hệ 0

Bước 1: giải mã và chấm điểm từng cá thể (cá thể nào quá nặng thì bỏ bớt món có mật độ thấp nhất)

| Cá thể | Nhiễm sắc thể | Trọng lượng thô | Phải sửa chữa | Sau sửa chữa | Trọng lượng | Fitness |
|---|---|---|---|---|---|---|
| C1 | `011000` | 9 | không | - | 9 | 16 |
| C2 | `011001` | 10 | không | - | 10 | 18 |
| C3 | `101010` | 14 | có | `100010` | 9 | 20 |
| C4 | `110000` | 7 | không | - | 7 | 15 |
| C5 | `000001` | 1 | không | - | 1 | 2 |
| C6 | `001000` | 5 | không | - | 5 | 9 |

Fitness tốt nhất 20, trung bình 13.33, độ đa dạng gene 0.722.

Bước 2: giữ lại 1 cá thể tinh hoa: C3 (`100010`, fitness 20)

Bước 3: chọn lọc cha mẹ

Bánh xe roulette, phần bánh xe tỉ lệ thuận với fitness:

| Cá thể | Fitness | Tỉ lệ được chọn | Luỹ kế |
|---|---|---|---|
| C1 | 16 | 20.0% | 20.0% |
| C2 | 18 | 22.5% | 42.5% |
| C3 | 20 | 25.0% | 67.5% |
| C4 | 15 | 18.8% | 86.2% |
| C5 | 2 | 2.5% | 88.8% |
| C6 | 9 | 11.2% | 100.0% |

Bước 4 và 5: lai ghép rồi đột biến

| Cặp | Cha | Mẹ | Điểm cắt | Con 1 | Số gene đột biến ở con 1 | Con 2 | Số gene đột biến ở con 2 |
|---|---|---|---|---|---|---|---|
| 1 | `011000` | `100010` | sau bit 5 | `011010` | 1 | `000011` | 2 |
| 2 | `110000` | `100010` | sau bit 4 | `111011` | 2 | `100000` | 0 |
| 3 | `011001` | `100010` | sau bit 3 | `011010` | 0 | `100001` | 0 |

Bước 6: quần thể thế hệ 1 gồm `100010`, `011010`, `000011`, `111011`, `100000`, `011010`

## Thế hệ 1

Bước 1: giải mã và chấm điểm từng cá thể (cá thể nào quá nặng thì bỏ bớt món có mật độ thấp nhất)

| Cá thể | Nhiễm sắc thể | Trọng lượng thô | Phải sửa chữa | Sau sửa chữa | Trọng lượng | Fitness |
|---|---|---|---|---|---|---|
| C1 | `100010` | 9 | không | - | 9 | 20 |
| C2 | `011010` | 15 | có | `001010` | 11 | 21 |
| C3 | `000011` | 7 | không | - | 7 | 14 |
| C4 | `111011` | 19 | có | `100011` | 10 | 22 |
| C5 | `100000` | 3 | không | - | 3 | 8 |
| C6 | `011010` | 15 | có | `001010` | 11 | 21 |

Fitness tốt nhất 22, trung bình 17.67, độ đa dạng gene 0.556.

Bước 2: giữ lại 1 cá thể tinh hoa: C4 (`100011`, fitness 22)

Bước 3: chọn lọc cha mẹ

Bánh xe roulette, phần bánh xe tỉ lệ thuận với fitness:

| Cá thể | Fitness | Tỉ lệ được chọn | Luỹ kế |
|---|---|---|---|
| C1 | 20 | 18.9% | 18.9% |
| C2 | 21 | 19.8% | 38.7% |
| C3 | 14 | 13.2% | 51.9% |
| C4 | 22 | 20.8% | 72.6% |
| C5 | 8 | 7.5% | 80.2% |
| C6 | 21 | 19.8% | 100.0% |

Bước 4 và 5: lai ghép rồi đột biến

| Cặp | Cha | Mẹ | Điểm cắt | Con 1 | Số gene đột biến ở con 1 | Con 2 | Số gene đột biến ở con 2 |
|---|---|---|---|---|---|---|---|
| 1 | `001010` | `000011` | sau bit 1 | `010111` | 2 | `011010` | 1 |
| 2 | `100011` | `000011` | sau bit 2 | `110010` | 2 | `100111` | 2 |
| 3 | `100011` | `100010` | sau bit 1 | `110010` | 1 | `101111` | 2 |

Bước 6: quần thể thế hệ 2 gồm `100011`, `010111`, `011010`, `110010`, `100111`, `110010`

## Thế hệ 2

Bước 1: giải mã và chấm điểm từng cá thể (cá thể nào quá nặng thì bỏ bớt món có mật độ thấp nhất)

| Cá thể | Nhiễm sắc thể | Trọng lượng thô | Phải sửa chữa | Sau sửa chữa | Trọng lượng | Fitness |
|---|---|---|---|---|---|---|
| C1 | `100011` | 10 | không | - | 10 | 22 |
| C2 | `010111` | 13 | có | `000111` | 9 | 18 |
| C3 | `011010` | 15 | có | `001010` | 11 | 21 |
| C4 | `110010` | 13 | có | `100010` | 9 | 20 |
| C5 | `100111` | 12 | không | - | 12 | 26 |
| C6 | `110010` | 13 | có | `100010` | 9 | 20 |

Fitness tốt nhất 26, trung bình 21.17, độ đa dạng gene 0.556.

Hết 2 thế hệ. Nghiệm tốt nhất tìm được là `100111` với giá trị **26**.

## Kết luận của ví dụ

- Nghiệm tối ưu thật sự (vét cạn): **26**
- Nghiệm GA tìm được sau 2 thế hệ: **26** (`100111`)
- Với bài tí hon này, chỉ 2 thế hệ là đã chạm đúng nghiệm tối ưu.

Điểm cần nhấn khi thuyết trình: fitness tốt nhất của quần thể không bao giờ đi xuống, vì cơ chế tinh hoa luôn chép thẳng cá thể khoẻ nhất sang thế hệ sau. Lai ghép lo việc khai thác những mảnh gene tốt đã có, đột biến lo việc khám phá những mảnh gene chưa từng xuất hiện.
