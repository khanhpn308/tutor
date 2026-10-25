# Thực hành: Xây dựng Product Backlog — Activity: Create a Product Backlog

> **Mã bài học:** M03-L08  
> **Loại học liệu gốc:** ACTIVITY  
> **Nguồn:** Agile_Project_Management / M03  

---

## 1. Mục tiêu bài học (Learning Objectives)

Sau khi hoàn thành bài học thực hành này, người học sẽ có khả năng:

- **Chuyển hóa nhu cầu người dùng thành User Story:** Áp dụng mẫu chuẩn (*User Story Template*) để biên soạn các câu chuyện người dùng hoàn chỉnh dựa trên dữ liệu phản hồi thực tế từ khách hàng.
- **Xác lập Tiêu chí chấp nhận (Acceptance Criteria):** Thiết lập tối thiểu hai tiêu chí kiểm thử cụ thể cho mỗi User Story nhằm làm rõ phạm vi và hỗ trợ định hình Định nghĩa hoàn thành (*Definition of Done - DoD*).
- **Đánh giá chất lượng bằng mô hình I.N.V.E.S.T.:** Vận dụng 6 tiêu chí của khung I.N.V.E.S.T. để rà soát, tinh chỉnh và đảm bảo tính khả thi của các User Story trước khi đưa vào Sprint.
- **Tổ chức và ưu tiên hóa Product Backlog:** Phân nhóm các User Story có cùng mục tiêu chiến lược vào một Chủ đề lớn (*Epic*) và sắp xếp lại thứ tự ưu tiên của Nhật ký sản phẩm (*Product Backlog*) theo giá trị kinh doanh.

---

## 2. Kiến thức nền tảng & Bối cảnh (Context & Prerequisites)

### Vị trí bài học trong chương trình
Bài học thuộc Module 3 của khóa học Quản lý dự án Agile (*Agile Project Management*), tập trung vào kỹ năng thực hành cốt lõi: chuyển đổi insight từ người dùng thành các hạng mục công việc cụ thể trên *Product Backlog*.

### Bối cảnh dự án mô phỏng: Virtual Verde (Office Green)
- **Sứ mệnh dự án:** *Office Green* triển khai dòng sản phẩm mới mang tên *Virtual Verde*, cung cấp cây cảnh để bàn nhằm nâng cao chất lượng không gian làm việc tại nhà (*home office*). Đợt sản phẩm đầu tiên đã được bàn giao tới tay khách hàng mới.
- **Kế hoạch ban đầu:** Nhóm dự kiến mở rộng danh mục sản phẩm của *Virtual Verde*, bắt đầu bằng việc giới thiệu các loại cây Bonsai.
- **Vấn đề phát sinh từ dữ liệu thực tế:** Khảo sát sau đợt giao hàng đầu tiên cho thấy **70% khách hàng mới gặp khó khăn trong việc chăm sóc cây**. Hậu quả là nhiều cây bị héo úa và chết chỉ trong vòng một tháng.
- **Chuyển dịch trọng tâm kinh doanh (*Strategic Pivot*):** Thay vì tập trung mở rộng bán thêm cây mới, đội ngũ quyết định phát triển các sản phẩm đồng hành và giải pháp hỗ trợ chăm sóc cây nhằm giải quyết triệt để nỗi đau của khách hàng.

### 6 Nhu cầu cốt lõi của khách hàng từ khảo sát
1. Biết được loại cây nào dễ chăm sóc nhất (*Find out which plants are easiest to care for*).
2. Tiếp cận hướng dẫn chăm sóc cây một cách dễ dàng (*Access care instructions easily*).
3. Được trang bị đúng công cụ để chăm sóc cây (*Have the right tools to care for their plants*).
4. Nhận được nhắc nhở khi đến lịch tưới cây (*Remember when to water their plants*).
5. Nhận trợ giúp và lời khuyên từ chuyên gia nhanh chóng (*Get expert help and advice quickly*).
6. Có quy trình đổi trả hàng thuận tiện, không rắc rối (*Have a hassle-free way to return their orders*).

### Phân định vai trò trong Scrum
- **Product Owner (Chủ sản phẩm):** Đóng vai trò chủ đạo trong việc định hình thứ tự ưu tiên của *Product Backlog* và phản ứng linh hoạt trước các phản hồi mới từ thị trường.
- **Bất kỳ thành viên nào:** Đều có thể tham gia đề xuất hoặc viết *User Story*.
- **Development Team (Nhóm phát triển):** Chịu trách nhiệm phản hồi, thảo luận về tính khả thi kỹ thuật và ước lượng độ phức tạp của các câu chuyện đó.

---

## 3. Nội dung lý thuyết trọng tâm (Systematic Theory)

### 3.1. Cấu trúc chuẩn của một Câu chuyện người dùng (User Story)

Một User Story chuẩn mực phải mô tả ngắn gọn yêu cầu từ góc nhìn của người trực tiếp thụ hưởng giá trị, tuân thủ cấu trúc 3 phần:

$$\text{As a } \langle \text{user role} \rangle, \text{ I want } \langle \text{action} \rangle \text{ so that I can } \langle \text{value} \rangle.$$

- **$\langle \text{user role} \rangle$ (Vai trò người dùng):** Xác định rõ đối tượng có nhu cầu cụ thể (ví dụ: *khách hàng tiềm năng*, *người mới sở hữu cây*, *người nuôi thú cưng*). Cần tập trung vào người chưa có nhiều kinh nghiệm trồng cây trong nhà.
- **$\langle \text{action} \rangle$ (Hành động mong muốn):** Mô tả hành vi hoặc tính năng mà người dùng muốn thực hiện để đáp ứng nhu cầu cụ thể.
- **$\langle \text{value} \rangle$ (Giá trị thu được):** Nêu rõ lý do sâu xa tại sao người dùng cần tính năng này và lợi ích thực tế mà họ nhận được sau khi hành động hoàn thành.

### 3.2. Tiêu chí chấp nhận (Acceptance Criteria) và mối liên hệ với Definition of Done

- **Bản chất:** *Acceptance Criteria* là tập hợp các điều kiện cụ thể, có thể đo lường và kiểm thử được, mà một User Story phải đáp ứng để được xem là hoàn thành.
- **Vai trò:** Giúp thiết lập ranh giới rõ ràng cho giải pháp, loại bỏ sự mơ hồ giữa nhóm phát triển và bên liên quan, đồng thời cấu thành nên Định nghĩa hoàn thành (*Definition of Done - DoD*) cho từng câu chuyện người dùng cụ thể.
- **Yêu cầu chuẩn:** Mỗi User Story cần xây dựng tối thiểu **hai tiêu chí chấp nhận** có thể hành động hóa (*actionable tasks*).

### 3.3. Bộ tiêu chuẩn đánh giá I.N.V.E.S.T.

Để đảm bảo User Story ngắn gọn, cụ thể và có khả năng triển khai, nhóm cần đối chiếu với 6 tiêu chí thuộc khung I.N.V.E.S.T.:

```
  I - Independent  (Độc lập)
  N - Negotiable   (Có thể thương lượng)
  V - Valuable     (Mang lại giá trị)
  E - Estimable    (Có thể ước lượng)
  S - Small        (Kích thước vừa vặn trong 1 Sprint)
  T - Testable     (Có thể kiểm thử được)
```

1. **Independent (Độc lập):** Việc hoàn thành câu chuyện này không bị phụ thuộc chặt chẽ hoặc chặn bởi câu chuyện khác, giúp phân phối công việc linh hoạt.
2. **Negotiable (Có thể thương lượng):** Story không phải là hợp đồng kỹ thuật cố định; luôn có không gian để Product Owner và Developers bàn bạc cách tối ưu hóa giải pháp.
3. **Valuable (Có giá trị):** Việc hoàn tất câu chuyện phải trực tiếp tạo ra giá trị đo lường được cho vai trò người dùng mục tiêu.
4. **Estimable (Có thể ước lượng):** Tiêu chuẩn hoàn thành đủ sáng tỏ để Nhóm phát triển có thể ước tính khối lượng công việc và điểm nỗ lực (*Story Points*).
5. **Small (Nhỏ gọn / Vừa vặn):** Quy mô của câu chuyện phải đủ gọn để Nhóm phát triển có thể thiết kế, xây dựng và kiểm thử hoàn chỉnh trong một khung thời gian Sprint.
6. **Testable (Có thể kiểm thử):** Tồn tại các bước hoặc bài kiểm tra rõ ràng nhằm xác nhận tính năng đã thỏa mãn toàn bộ tiêu chí chấp nhận đã đề ra.

> **Quy tắc thực hành:** Hãy cố gắng thỏa mãn tối đa các tiêu chí trên. Nếu một User Story chỉ đạt từ ba tiêu chí trở xuống (*three or fewer criteria*), hãy cân nhắc chỉnh sửa lại (*consider revising it*) hoặc chia nhỏ câu chuyện để đáp ứng tốt hơn.

### 3.4. Cấu trúc Epic và Tổ chức Product Backlog

- **Epic (Chủ đề lớn):** Là một tập hợp các User Story có chung định hướng chiến lược hoặc giải quyết cùng một nhóm vấn đề lớn. Epic đóng vai trò làm tiêu đề phân nhóm trong Backlog.
- **Cấu trúc phân cấp:**  
  $$\text{Product Backlog} \longrightarrow \text{Epic} \longrightarrow \text{User Stories} \longrightarrow \text{Acceptance Criteria}$$
- **Quy tắc ưu tiên:** Trong một Product Backlog thực tế có nhiều Epic khác nhau. Khi có thông tin mới phản ánh rủi ro kinh doanh hoặc nhu cầu khẩn cấp của người dùng, Product Owner sẽ đẩy toàn bộ Epic mang tính cấp bách lên đỉnh ưu tiên (*Top Priority*).

---

## 4. Ví dụ thực tế & Tình huống minh họa (Practical Application)

### Ví dụ mẫu từ bài học (Dòng sản phẩm Bonsai)

Dưới đây là mô hình mẫu chuẩn do giảng viên cung cấp để người học tham chiếu:

- **Epic:** *Bonsai Tree Offerings* (Dòng sản phẩm cây Bonsai)
- **Tiêu đề User Story:** Tìm hiểu phong cách tạo hình Bonsai (*Learn Bonsai Styles*)
- **User Story:**
  > *"As a new Bonsai tree owner, I want to learn about different Bonsai styles so that I can pick the right one for my tree."*  
  > *(Với vai trò là người mới sở hữu cây Bonsai, tôi muốn tìm hiểu về các phong cách tạo hình Bonsai khác nhau để tôi có thể chọn đúng kiểu dáng phù hợp cho cây của mình.)*
- **Acceptance Criteria (Tiêu chí chấp nhận mẫu):**
  1. *Customers can access a guide to different styles (formal & informal upright, broom, cascade, etc.) on website.* (Khách hàng có thể truy cập tài liệu hướng dẫn các phong cách tạo hình khác nhau như trực quân tử, trực lắc, chổi, thác đổ... ngay trên website).
  2. *Customers can take a quiz to match their trees to suitable styles.* (Khách hàng có thể làm bài trắc nghiệm ngắn để gợi ý phong cách phù hợp nhất với cây của họ).

### Ứng dụng thực tế: Thiết lập ưu tiên mới cho Virtual Verde

Khi dữ liệu khảo sát phát hiện 70% khách hàng mới gặp khó khăn trong việc chăm sóc cây (khiến nhiều cây bị héo úa và chết trong vòng một tháng):
- Các câu chuyện thuộc Epic Bonsai (đã lập từ trước) tạm thời hạ thứ tự ưu tiên.
- Toàn bộ 6 nhu cầu chăm sóc cây mới được đóng gói thành Epic: **"Plant Care Initiatives"** (Các sáng kiến chăm sóc cây cảnh) và được đẩy lên vị trí ưu tiên cao nhất trong Backlog.

---

## 5. Bảng thuật ngữ chuyên ngành Anh - Việt (Terminology Glossary)

| Thuật ngữ tiếng Anh | Thuật ngữ tiếng Việt | Giải thích ý nghĩa trong ngữ cảnh bài học |
| :--- | :--- | :--- |
| **Product Backlog** | Nhật ký sản phẩm / Danh mục sản phẩm | Danh sách có thứ tự ưu tiên chứa mọi tính năng, yêu cầu, lỗi cần sửa hoặc sáng kiến cần làm cho sản phẩm. |
| **Epic** | Chủ đề lớn / Sử thi | Nhóm tính năng hoặc mục tiêu lớn, bao gồm nhiều User Story liên quan với nhau. |
| **User Story** | Câu chuyện người dùng | Bản mô tả ngắn gọn yêu cầu tính năng từ góc nhìn của người dùng cuối theo mẫu: *Vai trò - Hành động - Giá trị*. |
| **Acceptance Criteria** | Tiêu chí chấp nhận | Các điều kiện bắt buộc mà giải pháp phải thỏa mãn để câu chuyện được nghiệm thu. |
| **Definition of Done (DoD)** | Định nghĩa hoàn thành | Thỏa thuận chung giữa các thành viên Scrum về tiêu chuẩn chất lượng kỹ thuật mà một hạng mục phải đáp ứng trước khi coi là hoàn tất. |
| **I.N.V.E.S.T.** | Khung tiêu chuẩn I.N.V.E.S.T. | Bộ 6 tiêu chí (Independent, Negotiable, Valuable, Estimable, Small, Testable) dùng để đánh giá chất lượng User Story. |
| **Product Owner (PO)** | Chủ sản phẩm | Người chịu trách nhiệm tối ưu hóa giá trị của sản phẩm và quản lý, ưu tiên hóa Product Backlog. |
| **Development Team** | Nhóm phát triển | Những người thực thi kỹ thuật, đóng góp phản hồi về tính khả thi và ước lượng khối lượng công việc. |
| **Sprint** | Chu kỳ Sprint | Khoảng thời gian đóng khung (thường từ 1-4 tuần) mà trong đó nhóm hoàn thành một Increment có khả năng bàn giao. |
| **Low-maintenance** | Ít tốn công chăm sóc | Thuộc tính của cây cảnh hoặc sản phẩm phù hợp cho người mới bắt đầu hoặc người bận rộn. |

---

## 6. Tóm tắt cốt lõi (Key Takeaways)

1. **Khách hàng là trọng tâm của Backlog:** Các hạng mục trên Product Backlog không phải là danh sách công việc thuần kỹ thuật, mà xuất phát từ việc giải quyết các nỗi đau cụ thể của người dùng.
2. **Cấu trúc 3 thành tố không thể tách rời:** Một User Story chỉ có giá trị khi liên kết chặt chẽ: *Ai cần?* $\rightarrow$ *Cần làm gì?* $\rightarrow$ *Nhận được giá trị cụ thể nào?*
3. **Tiêu chí chấp nhận là thước đo hoàn thành:** Không có Acceptance Criteria rõ ràng thì không thể kiểm thử và không thể xác lập Definition of Done.
4. **Bộ lọc I.N.V.E.S.T. đảm bảo khả thi:** Mọi User Story cần được kiểm tra tính Độc lập, Thương lượng được, Giá trị, Ước lượng được, Nhỏ gọn và Kiểm thử được trước khi đưa vào Sprint Planning.
5. **Agile là phản ứng linh hoạt với thay đổi:** Khi dữ liệu thực tế chỉ ra khủng hoảng chăm sóc cây (70% gặp vấn đề), Product Owner lập tức tái ưu tiên Backlog, tạm gác việc mở rộng tính năng mới (Bonsai) để tập trung bảo vệ trải nghiệm cốt lõi của khách hàng.

---

## 7. Bài tập & Câu hỏi tự luyện (Review Questions / Practice)

### Hướng dẫn thực hiện bài tập thực hành (Step-by-Step Activity)

Người học thực hiện bài tập trên mẫu bảng tính (*Activity Template: Product Backlog*) với 6 bước:

- **Bước 1 (Truy cập biểu mẫu):** Tải hoặc mở bản sao biểu mẫu Google Sheet / tệp XLSX *Product Backlog*.
- **Bước 2 (Viết 6 User Stories):** Dựa vào 6 nhu cầu khảo sát của Virtual Verde, viết 6 User Story hoàn chỉnh theo cấu trúc:  
  `As a <user role>, I want <this action> so that I can <get this value>.`
- **Bước 3 (Thiết lập Tiêu chí chấp nhận):** Bổ sung ít nhất hai tiêu chí chấp nhận cụ thể, có thể đo lường và hành động hóa cho từng Story.
- **Bước 4 (Đối chiếu I.N.V.E.S.T.):** Rà soát từng câu chuyện qua 6 tiêu chuẩn; cân nhắc chỉnh sửa nếu câu chuyện chỉ đạt từ ba tiêu chí trở xuống (*three or fewer criteria*).
- **Bước 5 (Đặt tiêu đề ngắn):** Đặt tiêu đề mô tả ngắn gọn kết quả mong muốn cho mỗi câu chuyện để dễ tra cứu.
- **Bước 6 (Đặt tên Epic):** Đặt tiêu đề Epic tổng thể (ví dụ: *Plant Care Initiatives*) và đưa lên đầu bảng Backlog.

---

### Bộ câu hỏi đánh giá kèm gợi ý phương pháp giải

> [!NOTE]  
> Các câu hỏi từ Câu 2 đến Câu 5 trong học liệu gốc không cung cấp sẵn các phương án trắc nghiệm hoặc đáp án cố định. Mục dưới đây cung cấp định hướng phương pháp luận sư phạm giúp người học tự đối chiếu và giải quyết bài toán.

#### Câu 1: Xác nhận hoàn thành bài tập thực hành
- **Yêu cầu:** Đạt tối thiểu 80% (4/5 điểm) trong bài kiểm tra tính điểm để vượt qua bài học.
- **Câu hỏi:** *Did you complete this activity?* (Bạn đã hoàn thành bài thực hành này chưa?)

---

#### Câu 2: Hoàn thiện mệnh đề hành động trong User Story
- **Đề bài:** Lựa chọn hành động hoàn thành tốt nhất câu chuyện người dùng sau:  
  *“As a pet owner, I want to _____ so that my cat doesn’t get sick.”*  
  *(Với vai trò là người nuôi thú cưng, tôi muốn _____ để mèo của tôi không bị ốm/ngộ độc.)*

> [!IMPORTANT]  
> **[AI Gợi ý tham khảo - Nguồn không có đáp án chính thức]**  
> - **Nguyên lý tư duy:** Phần hành động ($\langle action \rangle$) phải phản ánh chính xác giải pháp kết nối trực tiếp vai trò người nuôi thú cưng với mục tiêu bảo vệ sức khỏe cho mèo khi tiếp xúc với cây cối trong nhà.  
> - **Đặc điểm đáp án đúng cần tìm:** Hành động phải liên quan đến việc xác định độ an toàn độc hại của cây, ví dụ: *"biết loại cây nào an toàn/không có độc tính đối với vật nuôi"* (*identify which plants are pet-friendly / non-toxic to animals*) hoặc *"lọc các loại cây không gây hại cho thú cưng"* (*filter out toxic plants*).

---

#### Câu 3: Nhận diện Tiêu chí chấp nhận (Acceptance Criteria) phù hợp
- **Đề bài:** Xét User Story sau:  
  *“As a potential customer, I want to find out which plants are easiest to care for so that I can purchase low-maintenance options.”*  
  *(Với vai trò là khách hàng tiềm năng, tôi muốn tìm hiểu loại cây nào dễ chăm sóc nhất để tôi có thể mua các lựa chọn ít tốn công chăm sóc.)*  
  *Tiêu chí chấp nhận nào sau đây là phù hợp cho câu chuyện này? (Chọn tất cả các phương án đúng).*

> [!IMPORTANT]  
> **[AI Gợi ý tham khảo - Nguồn không có đáp án chính thức]**  
> - **Nguyên lý tư duy:** Acceptance Criteria phải là những điều kiện đo lường được, kiểm thử được trên hệ thống (website/catalog) và chứng minh rằng người dùng có thể phân loại, nhận biết mức độ chăm sóc của từng loại cây.
> - **Đặc điểm tiêu chí hợp lệ:**
>   1. Có nhãn hiển thị hoặc bộ lọc mức độ chăm sóc rõ ràng (ví dụ: "Dễ", "Trung bình", "Khó") gắn trên từng trang chi tiết sản phẩm.
>   2. Có chuyên mục hoặc trang danh mục riêng gom nhóm các loại cây "Ít tốn công chăm sóc / Dành cho người mới bắt đầu".
> - **Dấu hiệu tiêu chí không hợp lệ:** Những mô tả chung chung không thể kiểm thử (ví dụ: "Khách hàng cảm thấy yên tâm") hoặc những tính năng không liên quan đến việc tìm kiếm độ khó của cây (ví dụ: "Tích hợp cổng thanh toán quốc tế").

---

#### Câu 4: Nhận biết User Story đúng cấu trúc chuẩn
- **Đề bài:** *Which of the following user stories is complete and follows the correct structure?* (Câu chuyện người dùng nào sau đây là hoàn chỉnh và tuân thủ đúng cấu trúc chuẩn?)

> [!IMPORTANT]  
> **[AI Gợi ý tham khảo - Nguồn không có đáp án chính thức]**  
> - **Nguyên lý tư duy:** Đối chiếu từng phương án với công thức chuẩn 3 vế bắt buộc:  
>   1. **Vai trò:** `As a <user role>` (chỉ rõ vai trò cụ thể, không dùng từ quá mơ hồ như *As a person*).  
>   2. **Hành động:** `I want <action>` (chỉ rõ hành vi cần làm, không nêu giải pháp kỹ thuật cụ thể của database hay mã nguồn).  
>   3. **Giá trị:** `so that I can <value>` (nêu rõ lợi ích nhận được, không lặp lại hành động).
> - **Dấu hiệu phương án sai:** Bị khuyết vế `so that`, đảo lộn vị trí các vế, hoặc viết dưới dạng mệnh lệnh thức kỹ thuật (ví dụ: *"Hệ thống phải có nút X"*).

---

#### Câu 5: Liên kết nhu cầu người dùng với giải pháp Cẩm nang chăm sóc trực tuyến
- **Đề bài:** *Which of the following user stories could lead to the option of an online plant care manual? Select all that apply.* (Những câu chuyện người dùng nào sau đây có thể dẫn đến giải pháp xây dựng một cẩm nang chăm sóc cây trực tuyến? Chọn tất cả các phương án đúng.)

> [!IMPORTANT]  
> **[AI Gợi ý tham khảo - Nguồn không có đáp án chính thức]**  
> - **Nguyên lý tư duy:** Cẩm nang chăm sóc cây trực tuyến (*Online plant care manual*) là giải pháp kỹ thuật nhằm giải quyết nhu cầu **tiếp cận kiến thức và hướng dẫn chăm sóc thuận tiện**.
> - **Đặc điểm câu chuyện phù hợp:**
>   1. Các câu chuyện có hành động liên quan trực tiếp đến nhu cầu số 2 trong khảo sát: *"Access care instructions easily"* (tiếp cận hướng dẫn chăm sóc nhanh chóng, mọi lúc mọi nơi).
>   2. Các câu chuyện mong muốn tra cứu thông tin chi tiết về điều kiện ánh sáng, độ ẩm, chu kỳ bón phân của từng loại cây cụ thể để giữ cây sống lâu.
> - **Dấu hiệu câu chuyện không liên quan:** Các câu chuyện liên quan đến chính sách trả hàng hoàn tiền (Nhu cầu 6), công cụ vật lý như bình tưới, kéo tỉa (Nhu cầu 3), hoặc tư vấn trực tiếp 1-1 với chuyên gia (Nhu cầu 5).

---

## 8. Nguồn đối chiếu (Source Traceability)

| Đề mục trong giáo trình | Vị trí đối chiếu trong tài liệu nguồn gốc |
| :--- | :--- |
| **Mục 1: Mục tiêu bài học** | Tổng hợp từ *Activity Overview*, *Step 2* đến *Step 6*. |
| **Mục 2: Bối cảnh dự án & Vai trò** | Trích xuất từ đề mục `Scenario` (số liệu 70% khách hàng gặp khó khăn; sự thay đổi từ Bonsai sang Plant Care) và các ghi chú `Note` về vai trò Product Owner / Developers. |
| **Mục 3.1 & 3.2: User Story & Acceptance Criteria** | Trích xuất từ đề mục `Step 2: Create six user stories` và `Step 3: Create acceptance criteria`. |
| **Mục 3.3: Tiêu chuẩn I.N.V.E.S.T.** | Trích xuất toàn bộ từ đề mục `Step 4: Check your stories against the I.N.V.E.S.T. criteria`. |
| **Mục 3.4: Epic & Đặt tiêu đề** | Trích xuất từ đề mục `Step 5: Title each user story` và `Step 6: Add an epic title`. |
| **Mục 4: Ví dụ thực tế** | Trích xuất từ các đoạn văn bản mẫu về Bonsai: *"As a new Bonsai tree owner..."* và ví dụ về Acceptance Criteria trong `Step 2`, `Step 3`. |
| **Mục 7: Bài tập thực hành & Câu hỏi Quiz** | Ánh xạ trực tiếp từ `Step-by-Step Instructions` cùng nội dung các câu hỏi: `Câu 1`, `Câu 2`, `Câu 3`, `Câu 4`, `Câu 5`. |