# Kịch bản quay video demo

Hai video, quay riêng, tổng cộng khoảng 7 phút.

- **Video 1 (3 phút)**: demo chương trình chạy. Dùng làm bản dự phòng nếu hôm
  thuyết trình máy lỗi, và để cả nhóm xem trước cho quen luồng.
- **Video 2 (4 phút)**: đi qua dữ liệu và biểu đồ, quay riêng cho TV5 nắm số
  liệu nào quan trọng.

Trong thư mục này đã có sẵn `results/demo.gif`, bản ghi hình tự động của Video 1
không có tiếng. Dùng tạm được ngay, nhưng nên quay lại có giọng nói vì giảng
viên đánh giá cả phần diễn giải. Toàn bộ chữ mà phần demo in ra cũng được lưu
ở `results/demo-transcript.txt`, tiện đọc lại khi soạn lời dẫn.

Riêng Video 2, nếu không kịp quay thì gửi thẳng `results/bieu-do-tung-hinh.pdf`
cũng đủ: 10 trang, mỗi trang một biểu đồ kèm nguồn dữ liệu và câu kết luận,
người nhận tự lật theo nhịp của họ.

## 0. Chuẩn bị trước khi bấm ghi

1. Mở Windows Terminal, phóng chữ lên cỡ 16 tới 18 (Ctrl và dấu cộng), nền tối.
2. Cửa sổ rộng tối thiểu 90 cột để bảng không bị xuống dòng.
3. Tắt thông báo: Win + A rồi bật Focus assist, tắt Zalo và Messenger.
4. Vào đúng thư mục dự án và chạy thử một lượt trước khi ghi.
5. Phần mềm ghi hình: bấm **Win + Alt + R** là Xbox Game Bar ghi luôn cửa sổ
   đang mở, file ra nằm ở `Videos/Captures`. Muốn chỉn chu hơn thì dùng OBS,
   chọn nguồn Window Capture rồi trỏ vào Windows Terminal.
6. Nói chậm, mỗi cảnh dừng một nhịp để người xem kịp đọc số trên màn hình.

## Video 1: demo chương trình

### Cảnh mở đầu, khoảng 15 giây

Màn hình: thư mục dự án, gõ lệnh nhưng chưa Enter.

> Chào thầy và các bạn, em là [tên], phụ trách phần cài đặt. Nhóm em giải bài
> toán Cái túi 0/1 bằng giải thuật di truyền. Toàn bộ chương trình viết bằng
> Python thuần, phần lõi thuật toán không dùng thư viện ngoài nào.

Lệnh chạy:

```bash
python demo.py --slow
```

Chương trình có năm cảnh, mỗi cảnh dừng chờ Enter nên cứ thong thả nói rồi mới
bấm.

### Cảnh 1, bài toán, khoảng 30 giây

Chỉ vào ba con số: 100 món, sức chứa 2725, và `2^100 = 1.27e30`.

> Bài có 100 món, túi chỉ chịu được một nửa tổng trọng lượng. Nếu vét cạn thì
> phải xét hơn một triệu tỉ tỉ tỉ phương án, máy xét một tỉ phương án mỗi giây
> vẫn cần bốn chục nghìn tỉ năm. Đó là lý do phải dùng thuật toán xấp xỉ.

Nói thêm về cột Mật độ: dữ liệu thuộc lớp strongly correlated, giá trị bằng
trọng lượng cộng 10, nên mật độ của mọi món xấp xỉ bằng nhau. Chính chỗ này làm
thuật toán tham lam mất phương hướng.

### Cảnh 2, mã hoá, khoảng 25 giây

Chỉ vào chuỗi bit màu xanh.

> Mỗi lời giải là một chuỗi 100 bit, bit thứ i bằng 1 nghĩa là mang món i. Chuỗi
> ngẫu nhiên này nặng hơn sức chứa, chương trình sửa chữa bằng cách bỏ dần món
> có mật độ giá trị thấp nhất cho tới khi vừa túi. Nhờ vậy mọi cá thể trong quần
> thể luôn là lời giải hợp lệ.

### Cảnh 3, tiến hoá, khoảng 60 giây

Đây là cảnh quan trọng nhất, để `--slow` cho các dòng hiện ra từ từ.

Cần chỉ rõ ba cột:

- **Tốt nhất**: tăng dần, không bao giờ tụt, vì có cơ chế tinh hoa.
- **TB quần thể**: tăng theo nhưng luôn thấp hơn, khoảng cách giữa hai cột là
  phần quần thể còn đang thử nghiệm.
- **Đa dạng**: từ 0.97 rơi xuống dưới 0.1. Đây là hiện tượng hội tụ: ban đầu
  quần thể rải khắp nơi, về sau cả quần thể xúm lại quanh một nghiệm.

> Thế hệ 0 quần thể ngẫu nhiên cho 3249 điểm. Sau 100 thế hệ lên 3395. Cột đa
> dạng tụt từ 0.97 xuống dưới 0.1, nghĩa là quần thể đã co cụm lại. Nếu co cụm
> quá sớm thì thuật toán kẹt luôn, đó gọi là hội tụ sớm, phần nhận xét của nhóm
> em có số liệu cho chuyện này.

### Cảnh 4, nghiệm, khoảng 20 giây

> Nghiệm cuối mang 67 trên 100 món, trọng lượng đúng 2725 trên 2725, dùng hết
> sạch sức chứa, tổng giá trị 3395.

### Cảnh 5, đối chứng, khoảng 40 giây

Bảng so sánh là chỗ ăn điểm, nhấn vào cột Lệch tối ưu.

> Bốn thuật toán xấp xỉ dùng chung đúng 9060 lần gọi hàm fitness nên so sánh
> mới công bằng. GA đạt 3395, bằng đúng nghiệm tối ưu của quy hoạch động, lệch
> 0%. Tham lam lệch 1.91%, leo đồi 2.83%, ngẫu nhiên 2.74%. Quy hoạch động cho
> nghiệm tối ưu nhưng cần bảng 100 nhân 2726 ô nhớ và chỉ chạy được khi trọng
> lượng là số nguyên nhỏ, còn GA không cần hai điều kiện đó.

### Cảnh kết, khoảng 20 giây

Chạy thêm một lệnh nữa để cho thấy tham số đổi được và kết quả xấu đi thật:

```bash
python demo.py --pop 10 --gens 40 --mutation-scale 0 --no-pause
```

> Khi để quần thể 10 cá thể, tắt hẳn đột biến, quần thể cạn đa dạng chỉ sau vài
> thế hệ và kết quả kém hẳn. Chuyện này nhóm em đo trên 30 lần chạy, có trong
> phần kết quả.

## Video 2: dữ liệu và biểu đồ, quay cho TV5

Mở sẵn thư mục `results/` và `results/figures/`.

### Phần 1, chạy thí nghiệm, 30 giây

```bash
python -m ga.experiments
```

Không cần quay hết 10 phút chạy, chỉ quay đoạn đầu rồi cắt sang lúc đã xong.

> Lệnh này chạy năm nhóm thí nghiệm, mỗi cấu hình lặp lại 30 lần với 30 seed
> khác nhau rồi ghi ra CSV. Lặp nhiều lần là bắt buộc vì GA là thuật toán ngẫu
> nhiên, một lần chạy đẹp không chứng minh được gì.

### Phần 2, đi qua từng file CSV, 2 phút

Mở từng file, nói đúng một câu về nó. Thứ tự và nội dung lấy theo bảng trong
`docs/ban-giao-cho-tv5.md`, phần "Bảng tra nhanh".

Nhấn mạnh ba điểm cho TV5:

1. File có tiền tố `summary_` là bản đã gộp sẵn trung bình, độ lệch chuẩn, min,
   max và tỉ lệ thành công. Vẽ biểu đồ thì dùng mấy file này, nhanh hơn nhiều.
2. File không có tiền tố là dữ liệu thô từng lần chạy, chỉ cần khi muốn vẽ
   boxplot hoặc khi thầy hỏi dữ liệu gốc.
3. Cột quan trọng nhất của cả báo cáo là `gap_percent`, tức phần trăm lệch so
   với nghiệm tối ưu. Nhỏ hơn là tốt hơn, 0% là chạm đúng tối ưu.

### Phần 3, đi qua biểu đồ, 1 phút 30

```bash
python -m ga.plots
```

Mở lần lượt 9 file PNG trong `results/figures/`, mỗi hình nói một câu kết luận.
Câu kết luận có sẵn trong `docs/ban-giao-cho-tv5.md`.

### Phần 4, bảng tóm tắt, 30 giây

```bash
python -m ga.report
```

> Lệnh này gộp toàn bộ CSV thành một file markdown `docs/ket-qua-tom-tat.md`.
> Chị copy thẳng bảng trong đó vào báo cáo, số liệu luôn khớp với dữ liệu thật
> vì không ai gõ tay vào đó cả.

## Danh sách kiểm tra trước khi nộp video

- [ ] Nghe lại, tiếng rõ, không ồn nền
- [ ] Chữ trên terminal đọc được khi xem ở điện thoại
- [ ] Có nói đủ ba con số chính: 0% lệch tối ưu của GA, 1.91% của tham lam,
      9060 lần đánh giá dùng chung
- [ ] Có giải thích vì sao phải lặp 30 lần
- [ ] Độ dài mỗi video không quá 4 phút
