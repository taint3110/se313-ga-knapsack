# Kịch bản nói phần demo, 2 phút

Dành cho người trình bày phần cài đặt. Nói vừa đủ, không đi sâu vào thuật toán
vì phần đó đã có người khác trình bày.

Hai cách chạy, chọn một:

- **Chạy trực tiếp**: `python demo.py`. Chương trình dừng lại chờ Enter sau mỗi
  cảnh, nên nhịp hoàn toàn do mình quyết định. Nói xong đoạn của cảnh nào thì
  bấm Enter sang cảnh đó. Đây là cách nên dùng vì nhìn thật hơn.
- **Mở video**: `results/demo.mp4`, dài 34 giây. Mốc thời gian từng cảnh ghi ở
  cuối file này, tới mốc nào thì bấm tạm dừng, nói xong mới cho chạy tiếp.

Tổng lời nói khoảng 270 chữ, nói thong thả là đúng 2 phút.

---

## Mở đầu, 10 giây

Màn hình: terminal đã mở sẵn ở thư mục dự án, lệnh đã gõ nhưng chưa Enter.

> Phần của em là cài đặt. Nhóm em giải bài toán Cái túi 0/1 bằng giải thuật di
> truyền, viết bằng Python, phần lõi thuật toán không dùng thư viện ngoài nào.
> Em chạy thử luôn ạ.

Bấm Enter.

## Cảnh 1, bài toán, 25 giây

Chỉ vào con số `2^100` ở cuối màn hình.

> Bài toán có 100 món đồ, chiếc túi chỉ chịu được một nửa tổng trọng lượng.
> Nếu vét cạn thì phải xét 2 mũ 100 phương án, tức hơn một tỉ tỉ tỉ cách chọn.
> Máy xét một tỉ phương án mỗi giây thì vẫn cần bốn chục nghìn tỉ năm. Đó là lý
> do phải dùng thuật toán tiến hoá.

Bấm Enter.

## Cảnh 2, mã hoá, 20 giây

Chỉ vào chuỗi bit màu xanh.

> Mỗi lời giải được mã hoá thành một chuỗi 100 bit, bit thứ i bằng 1 nghĩa là
> mang món thứ i theo. Giải mã ra được 44 món, nặng 2546 trên sức chứa 2725
> nên vừa túi, giá trị 2986. Cá thể nào quá nặng thì chương trình bỏ bớt món
> kém giá trị nhất cho tới khi vừa.

Bấm Enter.

## Cảnh 3, tiến hoá, 35 giây

Đây là phần đáng xem nhất, để màn hình chạy hết rồi mới nói.

> Đây là 150 thế hệ. Cột tốt nhất đi từ 3249 lên 3395 và không bao giờ tụt
> xuống, vì mỗi thế hệ đều giữ lại cá thể khoẻ nhất. Cột đa dạng thì ngược
> lại, từ 0.97 rơi xuống dưới 0.1, nghĩa là cả quần thể dần xúm lại quanh một
> nghiệm. Toàn bộ 150 thế hệ chạy hết 0.2 giây.

Bấm Enter.

## Cảnh 4, nghiệm, 15 giây

> Nghiệm cuối mang 67 trên 100 món, trọng lượng đúng 2725 trên 2725, dùng hết
> sạch sức chứa, tổng giá trị 3395.

Bấm Enter.

## Cảnh 5, đối chứng, 35 giây

Bảng này là chỗ ăn điểm, chỉ vào cột Lệch tối ưu.

> Em cho bốn thuật toán chạy cùng một ngân sách là 9060 lần gọi hàm fitness
> cho công bằng. Giải thuật di truyền được 3395, đúng bằng nghiệm tối ưu của
> quy hoạch động, lệch 0%. Tham lam lệch 1.91%, leo đồi 2.83%, ngẫu nhiên
> 2.74%. Quy hoạch động cũng cho nghiệm tối ưu và còn nhanh hơn, nhưng nó cần
> bảng 100 nhân 2726 ô nhớ và chỉ chạy được khi trọng lượng là số nguyên, còn
> giải thuật di truyền thì không cần hai điều kiện đó. Phần kết quả chi tiết
> xin mời bạn tiếp theo.

Hết.

---

## Nếu bị hỏi ngay tại chỗ

**Chạy lại có ra kết quả khác không?** Có, vì đây là thuật toán ngẫu nhiên. Nên
trong báo cáo nhóm em chạy lại 30 lần cho mỗi cấu hình và lấy trung bình, trung
bình là lệch 0.22%.

**Sao không dùng quy hoạch động luôn?** Nó cần bộ nhớ tỉ lệ với sức chứa và đòi
trọng lượng nguyên. Thêm một ràng buộc mới là phải thiết kế lại từ đầu, còn ở
đây chỉ cần sửa hàm fitness.

**Có dùng thư viện GA có sẵn không?** Không, chọn lọc, lai ghép, đột biến đều
tự viết, trong `ga/algorithm.py`.

---

## Mốc thời gian nếu mở video thay vì chạy trực tiếp

File `results/demo.mp4`, tổng 34 giây. Tới mốc nào thì bấm tạm dừng, nói đoạn
tương ứng ở trên, xong mới cho chạy tiếp.

| Mốc | Cảnh | Tạm dừng ở đâu |
|---|---|---|
| 00:00 | mở đầu | để chạy luôn |
| 00:01 | Cảnh 1, bài toán | dừng ở giây 09, khi bảng 10 món và dòng `2^100` đã hiện đủ |
| 00:09 | Cảnh 2, mã hoá | dừng ở giây 13, khi đã hiện dòng giá trị 2986 |
| 00:13 | Cảnh 3, tiến hoá | dừng ở giây 21, khi bảng chạy xong tới thế hệ 150 |
| 00:21 | Cảnh 4, nghiệm | dừng ở giây 25 |
| 00:25 | Cảnh 5, đối chứng | để chạy hết, dừng ở giây 30 khi bảng so sánh đã đủ |

Nhắc: mở video thì chữ nhỏ hơn chạy trực tiếp, nhớ bật toàn màn hình và kiểm
tra xem hàng cuối của bảng so sánh có đọc được từ cuối lớp không.
