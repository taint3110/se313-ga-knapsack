# Bàn giao cho TV5: dữ liệu nào quan trọng và vẽ biểu đồ gì

Tài liệu này dành cho người làm **yêu cầu 5 phần kết quả** và **yêu cầu 6 nhận
xét đánh giá**. Mọi thứ cần cho hai phần đó đã chạy xong và nằm sẵn trong
`results/`, không phải chạy lại gì cả. Nếu muốn chạy lại thì ba lệnh sau tái
tạo toàn bộ:

```bash
python -m ga.experiments     # khoảng 13 phút, ghi đè toàn bộ CSV
python -m ga.plots           # vẽ lại 10 biểu đồ PNG
python -m ga.report          # dựng lại bảng số liệu docs/ket-qua-tom-tat.md
```

Biểu đồ PNG đã có sẵn trong `results/figures/`, chèn thẳng vào slide được
ngay. Nếu muốn tự vẽ bằng Excel hay Google Sheets cho hợp màu slide thì mở
đúng file CSV ghi trong từng mục bên dưới.

Muốn đi qua toàn bộ số liệu một lượt thì mở
**`results/bieu-do-tung-hinh.pdf`**: 10 trang, mỗi trang một biểu đồ kèm dòng
ghi lấy số từ file nào và câu kết luận nên viết. Lật tới lui và phóng to thoải
mái. Từng trang cũng được tách sẵn thành ảnh rời trong `results/slides/` để
chèn vào slide. File `.gif` cùng tên chỉ là bản chạy tự động để xem lướt, nó
không dừng và không tua được nên đừng dùng để đọc kỹ.

## 1. Hiểu dữ liệu trước khi vẽ

**Cột quan trọng nhất của cả báo cáo là `gap_percent`.** Đó là phần trăm lệch
so với nghiệm tối ưu tuyệt đối do quy hoạch động tìm ra:

```
gap_percent = (nghiệm tối ưu - nghiệm tìm được) / nghiệm tối ưu * 100
```

Càng nhỏ càng tốt, bằng 0 nghĩa là tìm đúng nghiệm tối ưu. Vẽ theo `gap_percent`
luôn dễ đọc hơn vẽ theo `best_value`, vì giá trị tuyệt đối của bốn bộ dữ liệu
chênh nhau rất xa (672 so với 16915) nên không đặt chung một biểu đồ được, còn
phần trăm thì so sánh thẳng được.

Ba quy ước cần nhớ:

| Tiền tố file | Nội dung | Khi nào dùng |
|---|---|---|
| `summary_*.csv` | đã gộp sẵn trung bình, độ lệch chuẩn, min, max, tỉ lệ thành công | mặc định dùng cái này để vẽ |
| file không tiền tố | dữ liệu thô từng lần chạy, mỗi dòng một seed | khi muốn vẽ boxplot hoặc khi thầy hỏi dữ liệu gốc |
| `run_meta.json` | cấu hình đã dùng, nghiệm tối ưu của từng bộ dữ liệu | khi cần trích dẫn thiết lập thí nghiệm |

Trong file `summary_*`, mỗi đại lượng có bốn cột: `_mean`, `_std`, `_min`,
`_max`. Cột `_std` chính là thanh sai số (error bar) của biểu đồ cột. Thêm cột
`success_rate` là tỉ lệ phần trăm số lần chạy chạm đúng nghiệm tối ưu.

**Vì sao phải có thanh sai số:** GA là thuật toán ngẫu nhiên, mỗi cấu hình đã
chạy lại 30 lần với 30 seed khác nhau. Trình bày một con số trần không có độ
lệch chuẩn là chỗ giảng viên hay vặn nhất.

## 2. Bảng tra nhanh: file nào dùng cho việc gì

| File CSV | Nội dung | Cột chính | Vẽ ra hình |
|---|---|---|---|
| `convergence.csv` | 30 lần chạy x 151 thế hệ trên bài chính | `generation`, `best_value`, `mean_fitness`, `diversity`, `gap_percent` | fig1, fig2 |
| `summary_baselines.csv` | GA so với 4 thuật toán khác trên 4 bộ dữ liệu | `instance`, `method`, `gap_percent_mean/std`, `success_rate` | fig3 |
| `summary_params.csv` | quét 7 nhóm tham số | `experiment`, `param_value`, `gap_percent_mean/std`, `success_rate`, `final_diversity_mean` | fig4, fig5, fig6, fig7 |
| `summary_tuned.csv` | 3 bộ tham số cùng ngân sách | `config`, `gap_percent_mean/std`, `success_rate`, `beats_greedy_mean` | fig8 |
| `summary_budget.csv` | tăng ngân sách trên bài n = 500 | `budget`, `gap_percent_mean/min/max`, `beats_greedy_mean` | fig9 |
| `summary_scalability.csv` | n từ 20 tới 1000 | `n`, `ga_gap_percent_mean`, `greedy_gap_percent_mean`, `ga_runtime_sec_mean`, `dp_runtime_sec_mean` | fig10 |

## 3. Mười biểu đồ và câu kết luận đi kèm

Mỗi hình bên dưới ghi rõ: file nguồn, cột dùng, và câu kết luận nên viết dưới
hình trong báo cáo. Số liệu chính xác tra ở `docs/ket-qua-tom-tat.md`.

### fig1_hoi_tu.png, đường hội tụ

- Nguồn: `convergence.csv`, cột `generation`, `best_value`, `mean_fitness`,
  `gap_percent`
- Khung trái: cá thể tốt nhất và trung bình quần thể theo thế hệ, dải mờ là
  khoảng min tới max của 30 lần chạy. Có thêm hai đường ngang là nghiệm tối ưu
  và nghiệm tham lam.
- Khung phải: sai lệch so với tối ưu giảm dần theo thế hệ.
- Câu kết luận: GA vượt mốc tham lam ngay trong khoảng 10 thế hệ đầu, sau đó
  cải thiện chậm dần và gần như bão hoà từ thế hệ 100 trở đi. Đường tốt nhất
  không bao giờ đi xuống vì có cơ chế tinh hoa.

### fig2_da_dang.png, mất đa dạng

- Nguồn: `convergence.csv`, cột `diversity`, `unique`
- Câu kết luận: độ đa dạng gene rơi từ khoảng 0.97 xuống dưới 0.10 chỉ sau
  khoảng 30 thế hệ. Đây là bằng chứng định lượng cho hiện tượng hội tụ sớm, và
  giải thích vì sao phần lớn cải thiện xảy ra ở giai đoạn đầu.

### fig3_so_sanh_thuat_toan.png, GA so với các thuật toán khác

Đây là biểu đồ quan trọng nhất của phần kết quả.

- Nguồn: `summary_baselines.csv`, cột `gap_percent_mean` và `gap_percent_std`
- Câu kết luận: cùng ngân sách 9060 lần gọi hàm fitness, trên bài chính GA lệch
  tối ưu khoảng 0.2% trong khi tham lam 1.91%, leo đồi 2.87% và ngẫu nhiên
  2.76%. Nhưng trên bộ `kp_easy` dữ liệu không tương quan thì tham lam và leo
  đồi bám sát GA, còn trên bài `n = 500` thì tham lam lại thắng GA. Kết luận:
  GA mạnh nhất ở vùng dữ liệu khó và kích thước vừa phải.

### fig4_kich_thuoc_quan_the.png, kích thước quần thể

- Nguồn: `summary_params.csv` lọc `experiment = pop_size`
- Lưu ý khi thuyết minh: tổng ngân sách đánh giá được giữ nguyên, nên quần thể
  200 chỉ chạy 44 thế hệ còn quần thể 10 chạy tới 905 thế hệ. Nếu không giữ
  ngân sách thì quần thể lớn thắng chỉ vì được tính nhiều hơn.
- Câu kết luận: quần thể quá nhỏ hội tụ sớm và kẹt, quần thể lớn hơn cho kết
  quả tốt hơn rõ rệt ngay cả khi phải cắt bớt số thế hệ.

### fig5_dot_bien.png, tỉ lệ đột biến

- Nguồn: `summary_params.csv` lọc `experiment = mutation_scale`
- Câu kết luận: đường cong hình chữ U. Tắt hẳn đột biến thì quần thể cạn đa
  dạng, độ đa dạng cuối đúng bằng 0.000 và kết quả tệ nhất nhóm. Đột biến quá
  mạnh thì GA thoái hoá thành tìm kiếm ngẫu nhiên. Mức tốt nhất nằm quanh
  `1/n` tới `2/n`.

### fig6_toan_tu.png, bốn toán tử

- Nguồn: `summary_params.csv` lọc `experiment` lần lượt là `crossover`,
  `p_crossover`, `selection`, `elitism`
- Câu kết luận: lai ghép đều (uniform) tốt hơn lai ghép một điểm, vì mã hoá nhị
  phân của bài cái túi không có liên kết vị trí, món số 3 và món số 70 chẳng
  liên quan gì nhau nên cắt theo đoạn không có lợi thế. Tournament `k = 2` tốt
  hơn `k = 10` vì áp lực chọn lọc nhẹ giữ được đa dạng lâu hơn. Giữ quá nhiều
  cá thể tinh hoa làm kết quả tệ đi.

### fig7_rang_buoc.png, cách xử lý ràng buộc

- Nguồn: `summary_params.csv` lọc `experiment = constraint`
- Câu kết luận: sửa chữa cá thể tốt hơn phạt điểm trong bài này. Hệ số phạt quá
  nhẹ còn làm cả quần thể trôi ra ngoài vùng hợp lệ, vì thêm một món được cộng
  `w + 10` điểm mà chỉ bị phạt `0.5w`.

### fig8_tinh_chinh_tham_so.png, ba bộ tham số

- Nguồn: `summary_tuned.csv`, cột `gap_percent_mean/std`, `success_rate`,
  `beats_greedy_mean`
- Câu kết luận: trên bài chính, ghép cơ học các giá trị tốt nhất của từng tham
  số lại cho 0.32%, tệ hơn cả cấu hình nền 0.22%, trong khi tổ hợp tìm được
  bằng cách thử theo cụm đạt 0.00% và chạm tối ưu ở cả 30 lần chạy. Trên bài
  `n = 500`, cùng cấu hình đó kéo sai lệch từ 1.46% xuống 0.20% và vượt tham
  lam ở một nửa số lần chạy, mà không cần thêm một lần đánh giá nào. Kết luận:
  tham số của GA tương tác với nhau nên không cộng dồn được, và tinh chỉnh tham
  số đáng giá ngang với việc tăng ngân sách tính toán.

### fig9_ngan_sach.png, ngân sách tính toán

- Nguồn: `summary_budget.csv` và `budget.csv`
- Câu kết luận: trên bài `n = 500`, tham lam đứng yên ở 0.21% dù cho thêm bao
  nhiêu thời gian cũng vậy, còn GA cải thiện dần theo ngân sách và vượt tham
  lam từ mốc 100 nghìn lần đánh giá trở đi. Đây là điểm mạnh cốt lõi của thuật
  toán xấp xỉ ngẫu nhiên: cho thêm thời gian thì cho nghiệm tốt hơn, còn thuật
  toán tham lam thì không có cơ chế đó.
- Ý nên ghép với fig8 khi viết báo cáo: bảng này chạy bằng bộ toán tử của cấu
  hình nền. Cấu hình đã tinh chỉnh chỉ cần 9 nghìn lần đánh giá đã đạt 0.20%,
  ngang với cấu hình nền khi được cấp 100 nghìn lần. Chỉnh tham số cho đúng
  tiết kiệm hơn mười lần chi phí tính toán.

### fig10_mo_rong.png, khả năng mở rộng

- Nguồn: `summary_scalability.csv`
- Khung trái: sai lệch theo `n`. Khung phải: thời gian chạy theo `n`, trục
  tung thang log.
- Câu kết luận: với ngân sách cố định, sai lệch của GA tăng dần theo kích thước
  bài toán, từ 0% ở `n = 20` lên khoảng 2.4% ở `n = 1000`. Thời gian GA tăng
  tuyến tính theo `n`. Quy hoạch động vẫn nhanh hơn ở mọi kích thước đã thử,
  nhưng phải trả giá bằng bộ nhớ `O(n*W)`.

## 4. Dàn ý gợi ý cho phần Kết quả, yêu cầu 5

1. **Thiết lập thí nghiệm**: bốn bộ dữ liệu, 30 seed mỗi cấu hình, ngân sách
   chung 9060 lần gọi fitness, máy và thời gian chạy. Lấy từ mục 1 của
   `ket-qua-tom-tat.md`.
2. **Kết quả trên bài chính**: bảng GA so với bốn thuật toán, kèm fig3. Nhấn
   con số GA đạt đúng nghiệm tối ưu 3395.
3. **Quá trình hội tụ**: fig1 và fig2, nói về tốc độ cải thiện và sự mất đa
   dạng.
4. **Ảnh hưởng của tham số**: fig4 tới fig7, mỗi hình một đoạn ngắn.
5. **Tinh chỉnh tham số**: fig8.
6. **Giới hạn khi bài lớn**: fig9 và fig10.

Tất cả bảng số đã có sẵn ở dạng markdown trong `docs/ket-qua-tom-tat.md`, copy
thẳng vào báo cáo được, không phải gõ lại.

## 5. Gợi ý nội dung cho phần Nhận xét, yêu cầu 6

**Ưu điểm, mỗi ý kèm một con số:**

- Không cần giả thiết gì về hàm mục tiêu, chỉ cần chấm điểm được một lời giải.
  Thêm ràng buộc mới chỉ phải sửa hàm fitness.
- Trên lớp dữ liệu khó, GA hơn hẳn các phương pháp đơn giản cùng ngân sách:
  0.2% so với 1.91% của tham lam và 2.87% của leo đồi.
- Cho thêm thời gian là cho nghiệm tốt hơn, thấy rõ ở fig9.
- Tinh chỉnh tham số đáng giá ngang với việc tăng ngân sách tính toán: vẫn
  9060 lần đánh giá, cấu hình tinh chỉnh kéo sai lệch trên bài `n = 500` từ
  1.46% xuống 0.20%.
- Song song hoá được dễ dàng vì các cá thể được chấm điểm độc lập với nhau.

**Nhược điểm, cũng kèm số:**

- Không bảo đảm tối ưu. Với cấu hình nền chỉ chạm đúng tối ưu ở 40% số lần chạy.
- Kết quả dao động giữa các lần chạy, phải báo cáo trung bình và độ lệch chuẩn.
- Nhạy với tham số: cùng một chương trình, chỉnh tham số làm sai lệch đổi từ
  0.00% tới 2.47%.
- Hội tụ sớm là rủi ro thường trực, độ đa dạng tụt xuống dưới 0.10 chỉ sau 30
  thế hệ.
- Bài càng lớn càng cần nhiều ngân sách, ở `n = 500` với ngân sách nhỏ thì thua
  cả tham lam.

**So với các thuật toán khác:**

| Thuật toán | Bảo đảm tối ưu | Chi phí | Khi nào nên dùng |
|---|---|---|---|
| Vét cạn | có | `O(2^n)` | `n` dưới 25 |
| Quy hoạch động | có | `O(n*W)` thời gian và bộ nhớ | trọng lượng nguyên, `W` không quá lớn |
| Tham lam | không | `O(n log n)` | cần kết quả tức thì, dữ liệu không tương quan |
| Leo đồi | không | theo ngân sách | bài nhỏ, mặt mục tiêu ít cực trị địa phương |
| GA | không | theo ngân sách | không gian rời rạc lớn, ràng buộc phức tạp, chấp nhận nghiệm đủ tốt |

**Miền ứng dụng thực tế:** xếp lịch sản xuất, xếp thời khoá biểu, định tuyến xe
giao hàng, thiết kế ăng ten, chọn danh mục đầu tư, tối ưu siêu tham số mô hình
học máy. Điểm chung là không gian rời rạc cực lớn, hàm mục tiêu không có đạo
hàm, và chỉ cần nghiệm đủ tốt trong thời gian cho phép.

## 6. Những chỗ dễ bị vặn, nên chuẩn bị trước

1. **Vì sao quy hoạch động nhanh hơn mà vẫn dùng GA?** Có câu trả lời đầy đủ
   trong `docs/cau-hoi-thuong-gap.md`, mục đầu tiên. Tóm tắt: quy hoạch động
   tốn bộ nhớ `O(n*W)`, đòi trọng lượng nguyên, và chỉ giải đúng dạng bài này.
2. **Đừng lấy trung bình `gap_percent` của bốn bộ dữ liệu rồi báo cáo một con
   số.** Bốn bộ có độ khó khác nhau, gộp lại là che mất chính cái kết luận thú
   vị nhất.
3. **Khi nói GA thắng, luôn kèm vế cùng ngân sách đánh giá.** Thiếu vế đó là
   so sánh không công bằng.
4. **Cột `runtime_sec` của GA có kèm chi phí đo đạc.** Mỗi thế hệ chương trình
   còn tính thêm độ đa dạng gene và số cá thể phân biệt để lấy dữ liệu vẽ
   fig2, phần này tốn gần bằng chính phần đánh giá fitness. Nếu bỏ đo đạc thì
   GA chạy nhanh hơn khoảng một nửa. Vì vậy khi so sánh nên bám vào cột
   `evaluations` chứ đừng bám vào thời gian.
5. **Tỉ lệ chạm tối ưu (`success_rate`) chỉ có nghĩa khi biết nghiệm tối ưu.**
   Ở đây biết được vì có quy hoạch động làm mốc. Bài thật ngoài đời thường
   không có mốc này, lúc đó chỉ so tương đối giữa các phương pháp với nhau.

## 7. Danh sách kiểm tra trước khi nộp

- [ ] Mỗi biểu đồ có tiêu đề, nhãn hai trục và đơn vị
- [ ] Mỗi biểu đồ cột có thanh sai số lấy từ cột `_std`
- [ ] Có ghi rõ số lần lặp lại là 30 seed
- [ ] Có ghi rõ ngân sách chung 9060 lần gọi hàm fitness
- [ ] Mỗi nhận xét đều có ít nhất một con số đi kèm
- [ ] Phần nhược điểm không bị bỏ qua, nêu đủ ba ý: không bảo đảm tối ưu, nhạy
      tham số, và thua tham lam ở bài lớn khi ngân sách nhỏ
