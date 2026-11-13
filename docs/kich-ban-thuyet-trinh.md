# Kịch bản nói phần demo

Dành cho người trình bày phần cài đặt. Đọc thong thả hết bài khoảng **2 phút
40**. Hai đoạn đánh dấu *(cắt được)* bỏ đi thì còn khoảng **2 phút 15**.

Cách chạy: `python demo.py`. Chương trình dừng chờ Enter sau mỗi cảnh nên nhịp
do mình quyết định. Nếu mở `results/demo.mp4` thay vì chạy trực tiếp thì xem
bảng mốc thời gian ở cuối file.

Quy ước trong file này:

- **Chữ in đậm** là chỗ nhấn giọng, nhấn bằng cách nói chậm lại và to hơn một
  chút. Mỗi đoạn chỉ hai tới ba chỗ, nhấn nhiều quá thì thành ra không nhấn gì.
- Dòng bắt đầu bằng **Chuyển:** là câu nối sang cảnh sau, nói đúng lúc tay bấm
  Enter. Nhờ mấy câu này mà bài nói liền mạch chứ không bị giật cục giữa các
  cảnh.
- *Chữ in nghiêng trong ngoặc* là ghi chú cho mình, không đọc lên.

---

## Mở đầu, 15 giây

*(Terminal mở sẵn ở thư mục dự án, lệnh đã gõ nhưng chưa bấm Enter.)*

> Em xin phép trình bày phần cài đặt. Giải thuật tiến hoá là **cả một họ**
> thuật toán, nhóm em chọn nhánh tiêu biểu nhất là **giải thuật di truyền**, vì
> bài Cái túi 0 1 là bài rời rạc, mỗi món chỉ **lấy hoặc không lấy**, rất hợp
> với cách mã hoá nhị phân. Chương trình viết bằng Python, phần thuật toán
> **tự cài** chứ không dùng thư viện có sẵn.
>
> **Chuyển:** Đầu tiên xin mời các bạn nhìn qua bài toán em dùng để chạy thử.

## Cảnh 1, bài toán, 30 giây

> Có **100 món đồ**, mỗi món một giá trị và một trọng lượng. Chiếc túi chịu
> được **2725** đơn vị, trong khi tổng trọng lượng cả 100 món là **5451**, tức
> là chỉ mang được **một nửa**, và phải chọn đúng cái nửa **đáng giá nhất**.
>
> Cột mật độ ở cuối bảng cho thấy mọi món **đáng giá gần như nhau**, nên cách
> làm tham lam, cứ nhặt món mật độ cao nhất trước, **không còn căn cứ** để xếp
> thứ tự. *(cắt được)*
>
> Còn nếu thử hết thì có **2 mũ 100** phương án. Máy xét một tỉ phương án mỗi
> giây vẫn cần **bốn chục nghìn tỉ năm**. Nên vét cạn **không khả thi**.
>
> **Chuyển:** Muốn thuật toán tiến hoá làm việc được thì trước hết phải cho nó
> một cách biểu diễn lời giải, đó là phần tiếp theo.

## Cảnh 2, mã hoá, 25 giây

> Mỗi lời giải là một **chuỗi 100 bit**, bit thứ i bằng **1 là mang món thứ i
> theo**, bằng 0 là để lại. Chuỗi màu xanh này là một cá thể sinh ngẫu nhiên:
> giải mã ra chọn 44 món, nặng **2546** trên sức chứa 2725 nên **hợp lệ**, tổng
> giá trị **2986**. Con số đó chính là **fitness** của cá thể.
>
> Cá thể nào nặng quá sức chứa thì chương trình **bỏ bớt** món kém giá trị nhất
> cho tới khi vừa túi, nên mọi cá thể luôn dùng được. *(cắt được)*
>
> **Chuyển:** Có cách biểu diễn và cách chấm điểm rồi, giờ thả cho quần thể
> tiến hoá.

## Cảnh 3, tiến hoá, 40 giây

*(Để bảng chạy hết rồi hãy nói, đừng nói chen vào lúc các dòng đang hiện ra.)*

> Quần thể **60 cá thể**, chạy **150 thế hệ**. Chọn lọc theo kiểu thi đấu, bốc
> ngẫu nhiên 3 cá thể rồi lấy con khoẻ nhất. Lai ghép một điểm, đột biến mỗi
> gene một phần trăm, và mỗi thế hệ giữ lại nguyên vẹn **2 cá thể tốt nhất**.
>
> Có hai cột cần nhìn. Cột **Tốt nhất** đi từ **3249** lên **3395** rồi dừng,
> và **không bao giờ tụt xuống**, vì luôn giữ lại con khoẻ nhất. Cột **Đa dạng**
> thì ngược lại, từ **0.97 xuống dưới 0.1**: ban đầu quần thể rải khắp nơi, về
> sau **xúm lại quanh một vùng**, và đó là lý do càng về cuối càng khó cải
> thiện thêm.
>
> Toàn bộ chạy hết **0.2 giây**, gọi hàm fitness **9060 lần**. Xin các bạn nhớ
> giùm em con số 9060 này.
>
> **Chuyển:** Và đây là lời giải cuối cùng mà nó tìm được.

## Cảnh 4, nghiệm, 15 giây

> Mang theo **67 trên 100 món**, tổng trọng lượng đúng **2725 trên 2725**, tức
> là **dùng hết sạch sức chứa**, không thừa một đơn vị nào. Tổng giá trị
> **3395**.
>
> **Chuyển:** Nhưng 3395 là tốt hay chưa tốt thì phải có cái để so. Nên em cho
> nó chạy đua với ba thuật toán khác.

## Cảnh 5, đối chứng, 45 giây

*(Bảng này là chỗ ăn điểm. Nói chậm, chỉ tay vào cột Lệch tối ưu.)*

> Cả bốn thuật toán đều được cấp **đúng 9060 lần gọi hàm fitness như nhau**,
> con số em vừa nhắc. Không khống chế chỗ này thì thuật toán nào chạy lâu hơn
> sẽ tự khắc tốt hơn, **so sánh mất ý nghĩa**.
>
> Di truyền được 3395, lệch **0 phần trăm**. Tham lam lệch **1.91**, leo đồi
> **2.83**, ngẫu nhiên **2.74**.
>
> Dòng cuối là quy hoạch động, cho đúng nghiệm tối ưu và còn **nhanh hơn hẳn**.
> Em xin nói rõ luôn vì chắc sẽ có câu hỏi: với **đúng dạng bài này** thì quy
> hoạch động tốt hơn thật. Nhưng nó cần bảng **100 nhân 2726 ô nhớ**, đòi trọng
> lượng phải là **số nguyên**, và thêm một ràng buộc mới là **phải thiết kế lại
> từ đầu**. Còn giải thuật di truyền thì **chỉ sửa hàm fitness**, khung thuật
> toán giữ nguyên. Đổi lại, chính vì quy hoạch động cho **biết trước nghiệm tối
> ưu** nên nhóm em mới đo được giải thuật di truyền lệch bao nhiêu phần trăm.
>
> **Kết:** Tóm lại, phần demo vừa rồi cho thấy ba điều. Một là bài toán này
> **không thể vét cạn**. Hai là giải thuật di truyền tìm được nghiệm **đúng
> bằng nghiệm tối ưu**, chỉ trong **0.2 giây**. Ba là khi so cùng một ngân
> sách, nó **tốt hơn cả ba thuật toán còn lại**. Phần cài đặt của em xin hết,
> em mời bạn tiếp theo ạ.

---

## Một lưu ý khi bàn giao

Slide ngay sau phần demo là slide thiết lập thực nghiệm, do bạn khác trình bày.
**Đừng giới thiệu trước nội dung slide đó**, cứ kết gọn phần mình rồi mời bạn
tiếp theo. Nói chen vào phần của người khác thì vừa mất thời gian của mình, vừa
làm bạn ấy mở đầu bị hụt.

Chỉ có một con số đi xuyên hai phần là **9060 lần đánh giá fitness**. Mình đã
nhắc nó hai lần ở cảnh 3 và cảnh 5, nên khi bạn ấy nói lại thì cả lớp đã quen
tai, đó là chỗ hai phần ăn khớp nhau mà không cần ai giới thiệu cho ai.

---

## Năm cảnh này bám theo yêu cầu nào của đề

| Cảnh | Yêu cầu trong đề |
|---|---|
| 1. Bài toán | yêu cầu 1, phát biểu bài toán: input, output, ràng buộc, mục tiêu |
| 2. Mã hoá | yêu cầu 4, biểu diễn dữ liệu: nhiễm sắc thể và hàm fitness |
| 3. Tiến hoá | yêu cầu 2, phương pháp: các toán tử chạy thật qua từng thế hệ |
| 4. Nghiệm | yêu cầu 5, kết quả của một lần chạy |
| 5. Đối chứng | yêu cầu 5 và 6, so sánh với thuật toán khác và đánh giá |

Thứ tự không đảo được: chưa phát biểu bài toán thì không mã hoá được, chưa biết
nhiễm sắc thể là gì thì nhìn bảng tiến hoá cũng không hiểu.

---

## Ba câu hỏi dễ bị hỏi ngay tại chỗ

**Chạy lại có ra kết quả khác không?**

> Có ạ, vì đây là thuật toán **ngẫu nhiên**. Nên trong báo cáo nhóm em chạy lại
> **30 lần** cho mỗi cấu hình rồi lấy trung bình, trung bình là lệch **0.22
> phần trăm** và có 40 phần trăm số lần chạy chạm đúng nghiệm tối ưu.

**Sao không dùng quy hoạch động cho nhanh?**

> Như em vừa trình bày ở cảnh cuối, nó cần **bộ nhớ tỉ lệ với sức chứa**, đòi
> **trọng lượng nguyên**, và **chỉ giải được đúng dạng bài này**.

**Nhóm có dùng thư viện GA có sẵn không?**

> Không ạ. Chọn lọc, lai ghép, đột biến đều **tự cài** trong file
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
