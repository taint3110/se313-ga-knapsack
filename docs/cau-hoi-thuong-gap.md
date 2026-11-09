# Câu hỏi thường gặp và cách trả lời

Mỗi câu trả lời đều kèm số liệu lấy từ `docs/ket-qua-tom-tat.md`. Trả lời có số
đo bao giờ cũng chắc hơn trả lời bằng lý thuyết suông.

## Về lựa chọn thuật toán

**Vì sao không vét cạn?**

Không gian tìm kiếm là `2^n`. Với bài chính `n = 100` thì có `1.27e30` phương
án. Máy xét được một tỉ phương án mỗi giây vẫn cần khoảng `4e13` năm. Nhóm có
chạy vét cạn thật nhưng chỉ với `n = 20`, hết 2.1 giây, và dùng nó để kiểm
chứng rằng quy hoạch động cho ra đúng cùng một nghiệm là 672.

**Vì sao không dùng quy hoạch động cho mọi trường hợp, khi nó cho nghiệm tối ưu
tuyệt đối và chạy chỉ 1 mili giây?**

Đây là câu hỏi đúng trọng tâm nhất, phải trả lời thẳng: với đúng bài toán cái
túi 0/1 có trọng lượng nguyên và `W` không quá lớn thì quy hoạch động tốt hơn
GA, nhóm không giấu chuyện đó. Quy hoạch động thua ở ba chỗ:

1. Bảng tốn `O(n*W)` ô nhớ. Bài `n = 500`, `W = 13505` đã cần gần 7 triệu ô.
   Nếu `W` cỡ `10^9` thì không còn cách nào cấp phát nổi.
2. Chỉ chạy được khi trọng lượng là số nguyên. Trọng lượng thực như 2.73 kg là
   bó tay, phải làm tròn và chấp nhận sai số.
3. Chỉ giải được đúng dạng bài này. Thêm một ràng buộc nữa, ví dụ giới hạn thể
   tích hoặc món A và món B không được đi chung, là phải thiết kế lại từ đầu.
   Với GA thì chỉ cần sửa hàm fitness, khung thuật toán giữ nguyên.

Cái túi 0/1 ở đây đóng vai trò bài toán mẫu: nó có nghiệm tối ưu biết trước nên
đo được GA sai lệch bao nhiêu phần trăm. Đó là lý do nhóm chọn bài này để minh
hoạ chứ không phải vì GA là cách tốt nhất để giải cái túi.

**Vì sao không dùng tham lam, nhanh hơn nhiều?**

Trên bài chính, tham lam theo mật độ giá trị cho 3330 điểm, lệch 1.91% so với
tối ưu 3395, còn GA đạt đúng 3395. Lý do là dữ liệu thuộc lớp
strongly correlated, `v_i = w_i + 10`, nên mật độ giá trị của mọi món gần như
nhau và tham lam mất căn cứ để xếp thứ tự. Nhóm có chạy thêm bộ `kp_easy` cùng
kích thước nhưng dữ liệu không tương quan: ở đó tham lam chỉ lệch 0.09%, gần
bằng GA. Nghĩa là tham lam mạnh hay yếu phụ thuộc cấu trúc dữ liệu.

**GA có luôn thắng tham lam không?**

Không. Trên bài `n = 500` với cùng ngân sách 9060 lần đánh giá, GA lệch 1.46%
còn tham lam chỉ lệch 0.21%, tức GA thua. Phải tăng ngân sách lên 100 nghìn lần
đánh giá thì GA mới xuống 0.14% và vượt tham lam ở cả 30 lần chạy. Bài càng lớn
thì GA càng cần nhiều ngân sách, đó là giới hạn thật của phương pháp.

**So với leo đồi thì sao, cùng là tìm kiếm cục bộ cả mà?**

Cùng ngân sách 9060 lần đánh giá, trên bài chính leo đồi lệch 2.87% còn GA lệch
0.22%. Leo đồi chỉ giữ một lời giải và chỉ đi lên, nên kẹt ở cực trị địa phương
rồi phải khởi động lại từ đầu, mất sạch thông tin đã học. GA giữ cả quần thể và
có lai ghép, tức ghép được mảnh tốt của hai lời giải khác nhau, nên thoát bẫy
mà không phải vứt bỏ những gì đã tìm ra.

## Về tham số

**Chọn tham số như thế nào, đổi thì kết quả ra sao?**

Nhóm quét từng tham số một, mỗi giá trị chạy lại 30 lần, số liệu ở mục 3 của
`docs/ket-qua-tom-tat.md`. Tóm tắt:

- Quần thể: 10 cá thể lệch 0.74%, 200 cá thể lệch 0.00%, khi đã giữ nguyên tổng
  ngân sách đánh giá. Quần thể lớn bù lại bằng ít thế hệ hơn vẫn lợi hơn.
- Đột biến: tắt hẳn thì lệch 2.28%, mức `2/n` tốt nhất với 0.02%, đẩy lên
  `30/n` thì lệch 2.47%, lúc đó GA thoái hoá thành tìm kiếm ngẫu nhiên.
- Lai ghép: không lai ghép lệch 0.52%, lai ghép đều (uniform) tốt nhất 0.02%.
- Chọn lọc: tournament `k = 2` tốt nhất 0.03%, `k = 10` tệ nhất 0.82% vì áp lực
  chọn lọc quá mạnh làm quần thể mất đa dạng chỉ sau vài thế hệ.

**Vậy cứ lấy giá trị tốt nhất của từng tham số ghép lại là ra cấu hình tốt nhất?**

Không. Nhóm đã thử đúng chuyện đó và kết quả tệ hơn cả cấu hình nền: ghép cơ
học cho 0.32% trong khi cấu hình nền 0.22%. Nguyên nhân là các tham số tương
tác với nhau, quần thể 200 cá thể chỉ còn 44 thế hệ mà tỉ lệ đột biến lại tăng
gấp đôi thì không đủ thời gian khai thác. Phải thử theo tổ hợp, cấu hình tốt
nhất tìm được là quần thể 100, 89 thế hệ, tournament `k = 2`, lai ghép đều,
đột biến `1/n`, tinh hoa 1, đạt 0.00% và chạm tối ưu ở cả 30 lần chạy. Cấu
hình đó cũng kéo sai lệch trên bài `n = 500` từ 1.46% xuống 0.20%, đủ để vượt
tham lam ở một nửa số lần chạy mà không cần thêm ngân sách nào.

**Vì sao tỉ lệ đột biến mặc định lại là 1/n?**

Để trung bình mỗi cá thể con có đúng một gene bị lật. Đây là mức khuyến nghị
kinh điển cho mã hoá nhị phân: đủ để sinh thông tin mới, chưa đủ để phá nát
những mảnh gene tốt vừa tìm được.

**Giữ bao nhiêu cá thể tinh hoa là hợp lý?**

Số liệu của nhóm cho thấy 0 tới 1 là tốt nhất (0.05% và 0.08%), giữ 10 thì tệ
hơn hẳn (0.50%). Giữ quá nhiều tinh hoa thì thế hệ sau gần như là bản sao của
thế hệ trước, quần thể hết chỗ để thử cái mới. Lưu ý là điều này đúng khi đã có
chọn lọc tournament, vốn đã tự ưu ái cá thể khoẻ rồi.

## Về bản chất thuật toán

**GA có đảm bảo tìm được nghiệm tối ưu toàn cục không?**

Không. Không có bảo đảm nào hết, đó là bản chất của thuật toán xấp xỉ ngẫu
nhiên. Chỉ nói được bằng xác suất: với cấu hình nền, GA chạm đúng tối ưu ở 40%
số lần chạy trên bài chính, sau khi tinh chỉnh thì 100%. Cũng vì không có bảo
đảm nên phải chạy lại 30 lần và báo cáo trung bình kèm độ lệch chuẩn.

**Làm sao tránh hội tụ sớm?**

Nhóm đo độ đa dạng gene theo từng thế hệ, công thức là trung bình `4p(1-p)`
trên từng vị trí gene với `p` là tỉ lệ cá thể mang bit 1. Trên bài chính, độ đa
dạng rơi từ 0.97 ở thế hệ 0 xuống dưới 0.10 sau khoảng 30 thế hệ. Bốn cách
chống, đều có số đo trong báo cáo:

1. Giảm áp lực chọn lọc: `k = 2` thay vì `k = 10`.
2. Tăng đột biến: ở mức `2/n` thì độ đa dạng cuối còn 0.196 thay vì 0.063.
3. Dùng chọn lọc theo thứ hạng thay cho roulette, giữ áp lực ổn định.
4. Giảm số cá thể tinh hoa.

**Lai ghép và đột biến khác nhau vai trò chỗ nào?**

Lai ghép là khai thác: ghép lại những mảnh gene tốt đã có sẵn trong quần thể,
không tạo ra bit nào mới nếu cả quần thể đã giống nhau tại vị trí đó. Đột biến
là khám phá: nó là nguồn duy nhất sinh ra giá trị gene chưa từng xuất hiện. Tắt
đột biến thì độ đa dạng cuối bằng đúng 0.000 và kết quả lệch 2.28%, con số này
chứng minh vai trò của đột biến rõ nhất.

**Fitness tốt nhất có bao giờ đi xuống không?**

Không, vì cơ chế tinh hoa chép thẳng cá thể tốt nhất sang thế hệ sau. Nhưng
trung bình của cả quần thể thì có lúc lên lúc xuống, do đột biến liên tục tạo
ra cá thể kém. Nhìn hình `fig1_hoi_tu.png` thấy rõ hai đường này.

**Vì sao đo chi phí bằng số lần gọi hàm fitness chứ không bằng thời gian?**

Vì mỗi thuật toán có cấu trúc vòng lặp khác nhau, so theo số vòng lặp thì không
có nghĩa. Số lần đánh giá fitness là phần việc nặng nhất và chung cho cả bốn
thuật toán, nên lấy làm đơn vị chi phí thì mới công bằng. Thời gian chạy vẫn
được ghi lại trong CSV để đối chiếu.

## Về phần cài đặt

**Xử lý ràng buộc sức chứa bằng cách nào?**

Hai cách, có so sánh số liệu. Cách sửa chữa: cá thể nào quá nặng thì bỏ dần món
có mật độ giá trị thấp nhất cho tới khi vừa túi, nhờ vậy mọi cá thể luôn hợp
lệ, kết quả lệch 0.22%. Cách phạt điểm: `fitness = giá trị - hệ số * phần vượt`,
kết quả tệ hơn ở mọi mức hệ số: 0.5 cho 4.71%, hệ số 2 cho 0.71%, hệ số 10 cho
1.27%.

Trường hợp hệ số 0.5 đáng để nói kỹ vì nó hỏng theo một kiểu rất đặc trưng:
mỗi món nhét thêm được cộng `w + 10` điểm mà chỉ bị phạt `0.5w`, tức là càng
quá tải càng được điểm cao, nên cả quần thể trôi hẳn ra ngoài vùng hợp lệ.
Chương trình vì thế luôn trả về cá thể hợp lệ tốt nhất từng gặp chứ không trả
về cá thể có fitness cao nhất, nếu không thì nghiệm trả ra là một chiếc túi
không đóng được.

**Độ phức tạp của chương trình là bao nhiêu?**

Mỗi lần đánh giá fitness tốn `O(n)`. Một thế hệ đánh giá `pop_size` cá thể nên
tốn `O(pop_size * n)`. Tổng cộng `O(generations * pop_size * n)`. Với cấu hình
nền và `n = 100` là khoảng 0.25 giây trên máy thường. Thứ tự mật độ giá trị
dùng cho thủ tục sửa chữa được tính sẵn một lần cho mỗi bộ dữ liệu, nếu sắp xếp
lại trong từng lần đánh giá thì chi phí thành `O(n log n)`.

**Kết quả có tái lập được không?**

Có. Cùng một `seed` thì cho ra kết quả giống hệt nhau tới từng con số, vì toàn
bộ phần ngẫu nhiên đi qua một đối tượng `random.Random(seed)` duy nhất. Seed
được ghi vào mọi dòng CSV.

**Nhóm có dùng thư viện GA có sẵn không?**

Không. Phần lõi thuật toán viết bằng thư viện chuẩn của Python, từ khởi tạo
quần thể cho tới từng toán tử chọn lọc, lai ghép, đột biến. `numpy` chỉ dùng để
tăng tốc bảng quy hoạch động của phần đối chứng, `matplotlib` chỉ dùng để vẽ
biểu đồ.

## Về họ giải thuật tiến hoá

**Ngoài GA còn những nhánh nào?**

- **ES** (Evolution Strategies): mã hoá số thực, đột biến theo phân phối chuẩn
  và tự điều chỉnh bước đột biến, hợp với bài tối ưu hàm liên tục.
- **GP** (Genetic Programming): cá thể là một cây biểu thức hoặc chương trình,
  lai ghép bằng cách tráo cây con.
- **DE** (Differential Evolution): cá thể mới sinh ra từ hiệu của các cặp cá thể
  khác, rất mạnh với bài số thực nhiều chiều.

Cả bốn đều dùng chung một khung: quần thể, chọn lọc theo độ thích nghi, sinh cá
thể mới, lặp qua nhiều thế hệ. Khác nhau ở cách mã hoá và ở toán tử sinh con.

**Bài toán nào ngoài đời dùng tới hướng này?**

Xếp lịch sản xuất, xếp thời khoá biểu, thiết kế ăng ten, định tuyến xe giao
hàng, chọn danh mục đầu tư, tối ưu siêu tham số của mô hình học máy. Điểm chung
là không gian lời giải rời rạc và cực lớn, hàm mục tiêu không có đạo hàm hoặc
phải tính bằng mô phỏng, và chỉ cần nghiệm đủ tốt trong thời gian cho phép chứ
không bắt buộc tối ưu tuyệt đối.
