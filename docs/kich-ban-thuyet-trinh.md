# Kịch bản nói phần demo

Dành cho người trình bày phần cài đặt. Bản đầy đủ dài khoảng **3 phút rưỡi**.
Những đoạn đánh dấu *(cắt được)* có thể bỏ khi thiếu giờ, bỏ hết thì còn khoảng
**2 phút 15**.

Cách chạy: `python demo.py`. Chương trình dừng lại chờ Enter sau mỗi cảnh nên
nhịp hoàn toàn do mình quyết định, nói xong đoạn nào mới bấm Enter sang cảnh
đó. Nếu mở `results/demo.mp4` thay vì chạy trực tiếp thì xem bảng mốc thời gian
ở cuối file.

Chữ in nghiêng trong ngoặc là ghi chú cho mình, không đọc lên.

---

## Mở đầu, 20 giây

*(Terminal đã mở sẵn ở thư mục dự án, lệnh đã gõ nhưng chưa bấm Enter.)*

> Em xin phép trình bày phần cài đặt. Như các bạn vừa nghe, giải thuật di
> truyền làm việc trên một quần thể lời giải, qua mỗi thế hệ thì chọn lọc, lai
> ghép và đột biến để quần thể tốt dần lên. Bây giờ em cho chạy thật trên bài
> toán Cái túi 0 1 để thấy quá trình đó diễn ra như thế nào. Chương trình em
> viết bằng Python, phần thuật toán tự cài chứ không dùng thư viện có sẵn.

*(Bấm Enter.)*

## Cảnh 1, bài toán, 40 giây

> Màn hình đang hiện dữ liệu đầu vào. Có 100 món đồ, mỗi món có một giá trị và
> một trọng lượng, ở đây em in ra 10 món đầu cho dễ nhìn. Chiếc túi chịu được
> tối đa 2725 đơn vị trọng lượng, trong khi tổng trọng lượng của cả 100 món là
> 5451. Nghĩa là chỉ mang được khoảng một nửa, và việc cần làm là chọn đúng cái
> nửa đáng giá nhất.

> Các bạn để ý cột cuối cùng, cột mật độ, tức là giá trị chia cho trọng lượng.
> Mật độ của mọi món đều xấp xỉ nhau, chỉ dao động quanh 1.1 tới 1.6. Đây là bộ
> dữ liệu nhóm em cố ý chọn cho khó. Vì khi món nào cũng đáng giá gần như nhau
> thì cách làm tham lam, tức là cứ nhặt món có mật độ cao nhất trước, sẽ không
> còn căn cứ rõ ràng để xếp thứ tự nữa. *(cắt được)*

> Còn nếu muốn thử hết mọi cách chọn thì có 2 mũ 100 phương án, tức là 1.27
> nhân 10 mũ 30. Máy tính xét được một tỉ phương án mỗi giây thì vẫn cần bốn
> chục nghìn tỉ năm mới xong. Nên vét cạn là không khả thi, bắt buộc phải đi
> tìm nghiệm gần đúng.

*(Bấm Enter.)*

## Cảnh 2, mã hoá, 35 giây

> Để giải thuật di truyền làm việc được thì trước hết phải mã hoá lời giải
> thành nhiễm sắc thể. Ở đây mỗi lời giải là một chuỗi 100 bit, em in ra 40 bit
> đầu. Bit thứ i bằng 1 nghĩa là mang món thứ i theo, bằng 0 là để lại.

> Chuỗi màu xanh trên màn hình là một cá thể sinh ngẫu nhiên. Giải mã ra thì nó
> chọn 44 món, tổng nặng 2546, vẫn nhỏ hơn sức chứa 2725 nên đây là lời giải
> hợp lệ, và tổng giá trị là 2986. Con số 2986 đó chính là fitness, tức là điểm
> số của cá thể này.

> Trường hợp cá thể nào nặng quá sức chứa thì chương trình sửa chữa nó, bằng
> cách bỏ dần món có mật độ thấp nhất cho tới khi vừa túi. Nhờ vậy mọi cá thể
> trong quần thể luôn là một lời giải dùng được, không có cá thể nào vô nghĩa.
> *(cắt được)*

*(Bấm Enter.)*

## Cảnh 3, tiến hoá, 55 giây

*(Đây là phần đáng xem nhất. Để bảng chạy hết rồi hãy nói, đừng nói chen vào
lúc các dòng đang hiện ra.)*

> Đây là phần chính. Quần thể gồm 60 cá thể, chạy 150 thế hệ. Chọn lọc theo
> kiểu thi đấu, mỗi lần bốc ngẫu nhiên 3 cá thể rồi lấy con khoẻ nhất làm cha
> mẹ. Lai ghép một điểm với xác suất 90 phần trăm, đột biến mỗi gene với xác
> suất 1 phần 100, và mỗi thế hệ giữ lại nguyên vẹn 2 cá thể tốt nhất.

> Bảng này có bốn cột. Cột Tốt nhất là giá trị của cá thể khoẻ nhất tìm được
> tính tới thế hệ đó. Cột TB quần thể là điểm trung bình của cả 60 cá thể. Cột
> Đa dạng đo mức độ khác nhau giữa các cá thể, bằng 1 là mỗi con một kiểu, bằng
> 0 là cả quần thể giống hệt nhau.

> Các bạn nhìn cột Tốt nhất. Thế hệ 0 là quần thể ngẫu nhiên, chỉ được 3249.
> Tới khoảng thế hệ 100 thì lên 3395 rồi dừng ở đó. Đường này chỉ đi lên chứ
> không bao giờ tụt xuống, vì cơ chế giữ lại cá thể tốt nhất mà em vừa nói.

> Ngược lại, cột Đa dạng tụt từ 0.97 xuống dưới 0.1 chỉ sau khoảng 30 thế hệ.
> Nghĩa là ban đầu quần thể rải khắp nơi, càng về sau càng xúm lại quanh một
> vùng. Đây cũng chính là lý do càng về cuối càng khó cải thiện thêm. Nếu quần
> thể co cụm quá sớm thì thuật toán kẹt luôn, phần nhận xét của nhóm em có số
> liệu đo cụ thể cho chuyện này. *(cắt được)*

> Toàn bộ 150 thế hệ chạy hết 0.2 giây, gọi hàm fitness 9060 lần.

*(Bấm Enter.)*

## Cảnh 4, nghiệm, 20 giây

> Đây là lời giải cuối cùng. Nó mang theo 67 trên 100 món, tổng trọng lượng
> đúng 2725 trên 2725, tức là dùng hết sạch sức chứa không thừa một đơn vị nào,
> và tổng giá trị đạt 3395. Phía dưới là chuỗi bit tương ứng của nghiệm đó.

*(Bấm Enter.)*

## Cảnh 5, đối chứng, 60 giây

*(Bảng này là chỗ ăn điểm. Nói chậm, chỉ tay vào cột Lệch tối ưu.)*

> Cuối cùng là phần đối chứng. Em cho giải thuật di truyền chạy đua với ba
> thuật toán khác trên đúng bài toán này.

> Có một chỗ em muốn nhấn mạnh: cả bốn thuật toán đều được cấp đúng 9060 lần
> gọi hàm fitness như nhau. Nếu không khống chế chỗ này thì thuật toán nào được
> chạy lâu hơn sẽ tự khắc cho kết quả tốt hơn, so sánh sẽ mất ý nghĩa.

> Kết quả là di truyền được 3395, lệch 0 phần trăm so với nghiệm tối ưu. Tham
> lam được 3330, lệch 1.91 phần trăm. Leo đồi được 3299, lệch 2.83. Tìm kiếm
> ngẫu nhiên được 3302, lệch 2.74.

> Dòng cuối cùng là quy hoạch động. Nó cho nghiệm tối ưu tuyệt đối là 3395 và
> chỉ mất một phần nghìn giây, tức là nhanh hơn hẳn. Em xin nói rõ chỗ này vì
> chắc sẽ có câu hỏi: với đúng dạng bài này thì quy hoạch động tốt hơn thật,
> nhóm em không giấu chuyện đó. Nhưng nó cần một bảng 100 nhân 2726 ô nhớ, tức
> là bộ nhớ phụ thuộc vào sức chứa của túi, và nó đòi trọng lượng phải là số
> nguyên. Thêm một ràng buộc mới, ví dụ giới hạn thêm về thể tích, là phải
> thiết kế lại thuật toán từ đầu. Còn với giải thuật di truyền thì chỉ cần sửa
> hàm tính fitness, khung thuật toán giữ nguyên.

> Bài cái túi ở đây đóng vai trò một bài toán mẫu: chính vì biết trước nghiệm
> tối ưu nên nhóm em mới đo được giải thuật di truyền sai lệch bao nhiêu phần
> trăm. Phần kết quả chi tiết và các thí nghiệm về tham số, em xin mời bạn tiếp
> theo trình bày. *(cắt được, nhưng nên giữ vì đây là câu chuyển cho TV5)*

---

## Ba câu hỏi dễ bị hỏi ngay tại chỗ

**Chạy lại có ra kết quả khác không?**

> Có ạ, vì đây là thuật toán ngẫu nhiên. Nên trong báo cáo nhóm em chạy lại 30
> lần cho mỗi cấu hình rồi lấy trung bình, trung bình là lệch 0.22 phần trăm và
> có 40 phần trăm số lần chạy chạm đúng nghiệm tối ưu.

**Sao không dùng quy hoạch động cho nhanh?**

> Như em vừa trình bày ở cảnh cuối, nó cần bộ nhớ tỉ lệ với sức chứa, đòi trọng
> lượng nguyên, và chỉ giải được đúng dạng bài này.

**Nhóm có dùng thư viện GA có sẵn không?**

> Không ạ. Chọn lọc, lai ghép, đột biến đều tự cài trong file
> `ga/algorithm.py`, chỉ dùng thư viện chuẩn của Python.

---

## Mốc thời gian nếu mở video thay vì chạy trực tiếp

File `results/demo.mp4`, tổng 34 giây. Tới mốc nào thì bấm tạm dừng, nói đoạn
tương ứng ở trên, xong mới cho chạy tiếp.

| Dừng ở giây | Lúc đó màn hình đang có gì | Nói đoạn nào |
|---|---|---|
| 09 | bảng 10 món và dòng `2^100` đã hiện đủ | Cảnh 1 |
| 13 | đã hiện dòng giá trị 2986 | Cảnh 2 |
| 21 | bảng tiến hoá chạy xong tới thế hệ 150 | Cảnh 3 |
| 25 | đã hiện nghiệm 67 món, 3395 | Cảnh 4 |
| 30 | bảng so sánh đã hiện đủ 5 dòng | Cảnh 5 |

Mở video thì chữ nhỏ hơn chạy trực tiếp, nhớ bật toàn màn hình và thử xem hàng
cuối của bảng so sánh có đọc được từ cuối lớp không.
