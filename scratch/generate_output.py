import sys
import os

content = """# Khởi Tạo và Quản Trị GitHub Issues: Cấu Trúc Giải Phẫu, Danh Mục Tác Vụ, Hệ Sinh Thái Nhãn Dán và Vòng Đời Tương Tác Dự Án — 🎥 GitHub Issues - Creating an Issue

> **Mã bài học:** M05-L09  
> **Loại học liệu gốc:** VIDEO_TRANSCRIPT  
> **Nguồn:** Advanced_Git_and_GitHub_Features / Module_05_GitHub_Features  

---

## 1. Mục tiêu bài học (Learning Objectives)

Sau khi hoàn thành bài học chuyên sâu này, người học sẽ làm chủ toàn diện các kiến thức và kỹ năng sau:

- **Thấu hiểu bản chất và vai trò cộng tác của GitHub Issues:** Nhận thức rõ GitHub Issues không chỉ là một công cụ theo dõi lỗi (bug tracker) đơn thuần mà là một nền tảng quản trị công việc toàn diện, kết nối mật thiết với dự án (Projects), kho lưu trữ (Repository), và hỗ trợ cộng tác đa nền tảng từ trình duyệt web, giao diện dòng lệnh đến thiết bị di động [0:00], [1:02], [2:19].
- **Làm chủ quy trình thiết lập môi trường kho lưu trữ thực hành:** Nắm vững mối quan hệ gắn kết giữa Issues và Repository; biết cách tạo kho lưu trữ mới (`GH issues demo`), khởi tạo tệp README, và sử dụng công cụ sinh mã nguồn (ChatGPT) để tạo nhanh cấu trúc trang web mẫu (`index.html`, `styles.css`, `script.js`) phục vụ kịch bản quản lý dự án [2:19], [3:31], [4:40], [6:02].
- **Khảo sát và vận dụng hệ sinh thái nhãn dán (Labels Ecosystem):** Phân tích cặn kẽ 9 nhãn dán mặc định do GitHub khởi tạo sẵn (`bug`, `documentation`, `duplicate`, `enhancement`, `good first issue`, `help wanted`, `invalid`, `question`, `wontfix`); hiểu rõ cách gán nhãn, chỉnh sửa và tạo nhãn tùy biến nhằm phân loại luồng công việc tối ưu [7:03], [7:37], [8:18].
- **Thiết lập và quản trị cột mốc phát hành (Milestones):** Hiểu rõ bản chất Milestone là tập hợp các hạn chót (deadlines) gắn liền với đợt phát hành phần mềm; nắm vững cách gom nhóm các Issues/Pull Requests, cấu hình ngày đến hạn (due date), và giải mã cơ chế tính toán tỷ lệ phần trăm hoàn thành tự động (Percentage Complete Engine) [8:18], [9:08], [10:03].
- **Thành thạo kỹ thuật phân rã công việc với danh mục tác vụ Markdown (Task List):** Sử dụng thuần thục cú pháp hộp kiểm Markdown (`- [ ] `) để chia nhỏ một tính năng lớn (ví dụ: tạo trang đăng nhập) thành các nhiệm vụ hành động độc lập (actionable tasks); khai thác tính năng chuyển đổi giữa tab soạn thảo (`Write`) và xem trước trực quan (`Preview`), cũng như đính kèm tệp đa phương tiện [10:42], [11:30], [12:26], [13:35].
- **Kiểm soát toàn diện vòng đời trạng thái và chu trình tương tác trên Issue:** Phân biệt rõ hai cơ chế đóng tác vụ (`Close as completed` và `Close as not planned`), kỹ thuật gửi bình luận kèm đóng issue (`Close with comment`), khả năng tái mở (`Reopen issue`), phương thức bày tỏ cảm xúc bằng Emojis Reactions, và quy tắc cấp phát số định danh tự động duy nhất (`#1`, `#2`...) [14:14], [14:47], [15:49], [16:43].

---

## 2. Kiến thức nền tảng & Bối cảnh (Context & Prerequisites)

### 2.1. Vị trí của Bài học M05-L09 trong Học phần và Khóa học

Trong lộ trình đào tạo của khóa học **Các tính năng nâng cao của Git và GitHub (Advanced Git and GitHub Features)**:
- **Module 01 (Git History Mastery):** Người học đã trang bị các kỹ thuật viết lại lịch sử commit cục bộ chuyên sâu như sửa đổi commit (`git commit --amend`), rebase tương tác (`git rebase -i`), xử lý xung đột phân nhánh, và cứu hộ con trỏ bị lạc thông qua nhật ký tham chiếu (`git reflog`).
- **Module 02 (Git Tags & Releases):** Chuẩn hóa việc đánh dấu các cột mốc phiên bản phát hành phần mềm cố định trên đồ thị lịch sử bằng Thẻ gọn nhẹ (Lightweight Tags) và Thẻ chú giải (Annotated Tags).
- **Module 03 (GitHub Pull Requests & Collaboration):** Mở rộng không gian làm việc nhóm thông qua quy trình đánh giá mã nguồn (Code Review), thảo luận thay đổi, và cơ chế hợp nhất mã nguồn vào nhánh chính.
- **Module 04 (Git Toolset):** Tối ưu hóa năng suất lập trình viên cục bộ với công cụ cất giữ trạng thái làm việc tạm thời (`git stash`), chuyển đổi ngữ cảnh an toàn (`git stash branch`), và các kỹ thuật dọn dẹp phân nhánh.
- **Module 05: Các tính năng nâng cao của GitHub (Module_05_GitHub_Features):** Đưa người học bước từ tầng công cụ dòng lệnh Git cục bộ lên tầng hạ tầng cộng tác đám mây của GitHub. Sau khi đã làm chủ các công cụ hỗ trợ chia sẻ mã nguồn nhanh như **GitHub Gist** (ở các bài học M05-L07 và M05-L08) và xây dựng tài liệu dự án thông qua **GitHub Wiki** (ở các bài học M05-L05 và M05-L06), bài học **M05-L09** chính thức mở ra trụ cột cốt lõi thứ ba: **GitHub Issues** — hệ thống theo dõi vấn đề, lập kế hoạch và điều phối tác vụ trung tâm của toàn bộ dự án phần mềm [0:00], [1:02].

### 2.2. Sự Chuyển dịch từ Quản lý Phiên bản (VCS) sang Quản trị Dự án và Cộng tác (Project Collaboration)

Một hệ thống quản lý phiên bản phân tán như Git thuần túy chỉ theo dõi trạng thái của các dòng mã lệnh, commit và nhánh. Tuy nhiên, trong môi trường phát triển phần mềm hiện đại, phần lớn thời gian của nhóm kỹ sư và người quản lý dự án dành cho việc:
1. Đặt câu hỏi và thảo luận về các yêu cầu kỹ thuật còn chưa rõ ràng [1:02].
2. Báo cáo, tái hiện và phân tích nguyên nhân gốc rễ của các lỗi phần mềm (Bugs) [1:02].
3. Lập kế hoạch phát triển các tính năng mới và phân rã chúng thành các tác vụ thực thi cụ thể [1:02], [11:30].
4. Đặt ra các mốc thời gian hoàn thành (Milestones / Deadlines) gắn liền với các đợt phát hành phiên bản (Releases) [8:18].

GitHub Issues được thiết kế để đóng vai trò là "Nguồn chân lý duy nhất" (Single Source of Truth) kết nối trực tiếp giữa các cuộc hội thoại của con người với mã nguồn thực tế trong kho lưu trữ (Repository) [0:00], [2:19]. Hiểu được cách khởi tạo, phân loại và tương tác trên Issues chính là bước đầu tiên để làm chủ toàn bộ quy trình quản lý dự án Agile trên GitHub [0:00], [10:42].

---

## 3. Nội dung lý thuyết trọng tâm (Systematic Theory)

### 3.1. Giới thiệu GitHub Issues: Trung tâm Hợp tác và Quản trị Công việc Dự án [0:00], [1:02], [2:19]

Mở đầu bài giảng, giảng viên điều hướng trình duyệt web đến địa chỉ `github.com/features/issues` (hoặc đường dẫn rút gọn `github.com/issues`) để giới thiệu bức tranh toàn cảnh về năng lực của hệ thống GitHub Issues [0:00]. Giảng viên khẳng định: **Issues là một tính năng toàn diện, mạnh mẽ và không thể thiếu của nền tảng GitHub** [0:00].

Theo thông tin chính thức từ giao diện giới thiệu của GitHub, Issues cung cấp một hệ sinh thái công cụ hỗ trợ làm việc nhóm bao gồm [0:00], [1:02]:
- **Khởi tạo vấn đề và phân rã tác vụ (Create issues & break them into tasks):** Chuyển đổi một ý tưởng, một lỗi phát sinh hoặc một yêu cầu nghiệp vụ phức tạp thành các đầu việc hành động có thể theo dõi được [0:00], [1:02].
- **Theo dõi các mối quan hệ (Track relationships):** Thiết lập sự liên kết giữa các Issues có liên quan, các tác vụ phụ thuộc hoặc mối liên kết giữa Issue với Pull Request [0:00], [7:03].
- **Bổ sung các trường dữ liệu tùy biến (Add custom fields):** Mở rộng thông tin theo dõi theo nhu cầu riêng của từng tổ chức hoặc dự án [0:00].
- **Tổ chức thảo luận chuyên sâu (Have conversation):** Thúc đẩy các cuộc trao đổi kỹ thuật, phản biện giải pháp ngay tại ngữ cảnh của vấn đề [0:00], [1:02].
- **Trực quan hóa dự án đa chiều (Visualize large projects):** Tích hợp sâu rộng với GitHub Projects để xem xét dữ liệu dưới dạng bảng danh mục (tables), bảng luồng công việc Kanban (boards), hoặc sơ đồ lộ trình thời gian (roadmaps) [0:00], [1:02].
- **Tự động hóa toàn diện bằng mã lệnh (Automate everything with code):** Kết nối với GitHub Actions và các luồng làm việc tự động nhằm tối ưu hóa quy trình quản trị [0:00].

Giảng viên nhấn mạnh mục đích cốt lõi nhất của Issues: **Issues giúp các thành viên hợp tác và làm việc cùng nhau (collaborate)** [0:00]. 

Hai trường hợp sử dụng điển hình được giảng viên nêu ra trong bài học [1:02]:
1. **Đặt câu hỏi hoặc báo cáo lỗi (Asking questions / Reporting bugs):** Ví dụ lập trình viên hoặc người kiểm thử có thể tạo một Issue với tiêu đề: *"Tại sao trang đăng nhập không hoạt động?" (Why is the login page not working?)* nhằm kêu gọi nhóm cùng điều tra [1:02].
2. **Khởi tạo và phân rã tính năng mới (Creating issues for a project / feature):** Ví dụ tạo một Issue có tên: *"Tạo trang đăng nhập" (Create a login page)* và chia nhỏ nó thành nhiều tác vụ hành động để triển khai tuần tự [1:02].

Về mặt nền tảng truy cập, Issues có tính linh hoạt rất cao: Lập trình viên có thể xem, khởi tạo và quản lý Issues trực tiếp trên **trình duyệt web**, thông qua **giao diện dòng lệnh (terminal)** bằng công cụ GitHub CLI, hoặc trên **điện thoại thông minh và máy tính bảng** thông qua ứng dụng di động của GitHub [2:19].

<!-- FIGURE_START: F01 -->
#### Hình F01: Cấu trúc Giải phẫu và Vòng đời Khởi tạo của một GitHub Issue (Title, Task List Checkboxes, Metadata Sidebar, Đánh số thứ tự tự động Issue #1)

![Hình F01: Sơ đồ cấu trúc giải phẫu của một GitHub Issue thể hiện trình soạn thảo chính, danh mục Task List, thanh thuộc tính Sidebar và cơ chế đánh số tự động](assets/M05-L09/F01_cau_truc_giai_phau_va_vong_doi_khoi_tao.svg)

<details>
<summary>Xem mã nguồn sơ đồ (Mermaid)</summary>

```mermaid
flowchart TD
    subgraph UI ["GIAO DIỆN KHỞI TẠO VÀ CẤU TRÚC GIẢI PHẪU GITHUB ISSUE"]
        direction TB

        subgraph MainEditor ["1. KHÔNG GIAN SOẠN THẢO CHÍNH (BÊN TRÁI)"]
            direction TB
            Title["Tiêu đề Issue (Title)<br/>Ví dụ: create a login page"]
            TabMode["Chế độ hiển thị song song:<br/>- Tab Write: Soạn thảo nội dung Markdown<br/>- Tab Preview: Xem trước giao diện hiển thị"]
            
            subgraph BodyContent ["Nội dung và Danh mục Tác vụ (Task List)"]
                direction TB
                TaskSyntax["Cú pháp Markdown Task List:<br/>Dấu trừ + Dấu cách + Mở ngoặc vuông + Dấu cách + Đóng ngoặc vuông"]
                Task1["Nhiệm vụ 1: create a basic login page"]
                Task2["Nhiệm vụ 2: add authentication"]
                Task3["Nhiệm vụ 3: add recaptcha"]
                Task4["Nhiệm vụ 4: improve styling and layout"]
                TaskSyntax --> Task1 --> Task2 --> Task3 --> Task4
            end

            AttachFiles["Khu vực đính kèm tệp tin đa phương tiện:<br/>Kéo thả (Drag and drop) hoặc chọn tệp (Paste/Click)<br/>Hỗ trợ ảnh chụp màn hình (Screenshots) và video mô tả"]
            
            Title --> TabMode --> BodyContent --> AttachFiles
        end

        subgraph Sidebar ["2. THANH THUỘC TÍNH SIÊU DỮ LIỆU (SIDEBAR BÊN PHẢI)"]
            direction TB
            Assignees["Assignees:<br/>Phân công người chịu trách nhiệm thực thi"]
            Labels["Labels:<br/>Gán nhãn phân loại (enhancement, bug...)"]
            Projects["Projects:<br/>Liên kết bảng quản trị dự án (Tables, Boards, Roadmaps)"]
            Milestones["Milestones:<br/>Gán vào cột mốc phát hành và hạn chót (Deadline)"]
            Development["Development:<br/>Liên kết nhánh làm việc (Branch) hoặc Pull Request"]
            Assignees ~~~ Labels ~~~ Projects ~~~ Milestones ~~~ Development
        end
    end

    subgraph SubmitPhase ["3. QUÁ TRÌNH KHỞI TẠO VÀ CẤP PHÁT ĐỊNH DANH TỰ ĐỘNG"]
        direction TB
        BtnSubmit["Nhấp nút Submit new issue"]
        AutoNumber["Hệ thống GitHub tự động cấp số thứ tự định danh duy nhất:<br/>- Issue đầu tiên trong kho: Gán số định danh Issue #1<br/>- Issue tiếp theo trong kho: Gán số định danh Issue #2 (Tăng tuần tự)"]
        TimelineView["Hiển thị dòng thời gian lịch sử (Issue Timeline):<br/>Ghi nhận người tạo và thời điểm khởi tạo vừa diễn ra"]
        BtnSubmit --> AutoNumber --> TimelineView
    end

    MainEditor --> BtnSubmit
    Sidebar --> BtnSubmit
```
</details>

*Hình F01: Cấu trúc giải phẫu và quy trình khởi tạo GitHub Issue: Từ trình soạn thảo Task List bên trái, thuộc tính Sidebar bên phải đến cơ chế cấp phát số định danh Issue #1 tự động [10:42], [11:30], [12:26], [13:35], [15:49].*

**Giải thích trực quan:** Sơ đồ giải phẫu toàn diện một GitHub Issue theo cấu trúc đối xứng hai cột: Cột bên trái là không gian nội dung (tiêu đề, tab Write/Preview, cú pháp Task List với 4 nhiệm vụ con, và khu vực đính kèm ảnh/video); Cột bên phải là Sidebar quản trị (Assignees, Labels, Projects, Milestones, Development). Khi người dùng nhấn Submit, hệ thống tự động gán nhãn định danh duy nhất `#1` và mở ra dòng thời gian lịch sử hoạt động.
<!-- FIGURE_END: F01 -->

---

### 3.2. Thiết lập Môi trường Thực hành: Khởi tạo Kho `GH issues demo` và Chuẩn bị Tệp Mẫu [2:19], [3:31], [4:40], [6:02]

Để quan sát trực quan cơ chế vận hành thực tế của Issues, giảng viên bắt đầu thiết lập một môi trường làm việc mới [2:19]. Một nguyên lý nền tảng được nhấn mạnh: **Issue là một tính năng gắn liền với kho lưu trữ (Issue is a feature of a repository)**, do đó trước khi tạo Issue, chúng ta bắt buộc phải có một repository [2:19].

Quy trình thiết lập kho lưu trữ được giảng viên tiến hành tuần tự như sau [3:31]:
1. Truy cập vào trang chủ GitHub, nhấp vào nút tạo kho lưu trữ mới (`Create a new repository`) [3:31].
2. Đặt tên kho lưu trữ là `GH issues demo` (hoặc `GH-issues-demo`) [3:31]. Giảng viên bổ sung tên này vào từ điển trình duyệt để tránh xuất hiện dấu gạch lượn sóng màu đỏ báo lỗi chính tả [3:31].
3. Giữ nguyên trạng thái mặc định: Không cần nhập phần mô tả (description), thiết lập quyền truy cập ở chế độ công khai (**Public repository**), và đánh dấu chọn khởi tạo kho với tệp `README.md` [3:31].
4. Nhấp nút xác nhận tạo kho: Kho lưu trữ được khởi tạo thành công với một tệp `README.md` rỗng duy nhất [3:31].

Tiếp theo, để chuẩn bị cho kịch bản tạo Issue mang tên *"Tạo trang đăng nhập" (Create a login page)*, chúng ta cần có một số tệp mã nguồn mẫu trong kho để xử lý [3:31]. Giảng viên chuyển sang sử dụng công cụ trí tuệ nhân tạo **ChatGPT** để sinh nhanh mã nguồn cho trang web đăng nhập mẫu [3:31], [4:40]:
- Giảng viên gửi câu lệnh: *"Hey, please generate code for a sample login page"* [4:40].
- ChatGPT phản hồi và tạo ra cấu trúc trang web gồm ba tệp [4:40], [6:02]:
  1. `index.html`: Chứa cấu trúc đánh dấu HTML hoàn chỉnh từ thẻ mở đến thẻ đóng `<html>` [4:40].
  2. `styles.css`: Chứa mã định dạng tầng kiểu dáng, bắt đầu từ thuộc tính vùng `body` [6:02].
  3. `script.js`: Chứa mã kịch bản xử lý tương tác phía máy khách [6:02].

Giảng viên lần lượt đưa các tệp này lên kho lưu trữ GitHub [4:40], [6:02]:
- Sao chép mã HTML từ ChatGPT, quay lại GitHub, nhấp tạo tệp mới mang tên `index.html`, dán nội dung vào trình soạn thảo trực tuyến. Khi dán mã, tính năng tô màu cú pháp (syntax highlighting) lập tức xuất hiện. Giảng viên chấp nhận thông điệp commit mặc định và thực hiện commit tệp [4:40].
- Sau đó, giảng viên tạm dừng video để tạo nhanh hai tệp còn lại là `script.js` và `styles.css` rồi quay trở lại [6:02].
- Khi hoàn tất, kho lưu trữ đã có đầy đủ ba tệp mã nguồn cơ bản của trang đăng nhập [6:02]. Giảng viên nhấp chuột vào thẻ điều hướng **Issues** trên thanh menu của kho để bắt đầu làm việc với hệ thống Issues [6:02], [7:03].

---

### 3.3. Hệ Sinh thái Nhãn dán (Labels Ecosystem) trong Quản trị GitHub [7:03], [7:37], [8:18]

Khi truy cập vào tab Issues của kho lưu trữ mới, giao diện xuất hiện một thông điệp khuyến nghị: *"Label issues and pull requests for new contributors"* (Gán nhãn cho các Issue và Pull Request để hỗ trợ người đóng góp mới) [7:03]. Giảng viên lưu ý rằng trong các bài học tiếp theo, chúng ta sẽ thấy Issues và Pull Requests có mối liên hệ hữu cơ hết sức chặt chẽ với nhau [7:03].

Tại đây, giảng viên nhấp vào nút **Labels** để kiểm tra hệ thống nhãn dán có sẵn [7:03], [7:37]. Nhãn dán (Labels) trong GitHub là các thẻ định danh phân loại trực quan bằng màu sắc và tên gọi ngắn gọn, cho phép lập trình viên gắn cờ để phân luồng, tìm kiếm và lọc các đầu việc một cách có hệ thống [7:03], [7:37].

Mặc định, GitHub tự động tạo sẵn một bộ **9 nhãn dán tiêu chuẩn** trong mọi kho lưu trữ mới khởi tạo [7:37], [8:18], [10:03]:

1. **`bug` (Màu đỏ):** Chỉ định một sự cố kỹ thuật, lỗi chương trình hoặc một chức năng hoạt động không đúng như kỳ vọng [7:37].
2. **`documentation` (Màu xanh da trời):** Dành riêng cho các yêu cầu bổ sung, sửa đổi hoặc cải tiến hệ thống tài liệu hướng dẫn [7:37].
3. **`duplicate` (Màu trắng/xám):** Gắn cờ cho một Issue hoặc Pull Request bị trùng lặp với một đầu việc đã được tạo từ trước [7:37].
4. **`enhancement` (Màu xanh lục nhạt):** Đại diện cho một tính năng hoàn toàn mới hoặc một đề xuất nâng cấp cải tiến chức năng phần mềm. Giảng viên thông báo sẽ sử dụng chính nhãn `enhancement` này để gán cho Issue tạo trang đăng nhập trong bài thực hành [7:37].
5. **`good first issue` (Màu tím nhạt):** Đánh dấu các tác vụ có độ phức tạp thấp, phù hợp nhất để những người mới tham gia dự án (newcomers) có thể bắt đầu đóng góp mà không bị quá tải [7:37].
6. **`help wanted` (Màu xanh ngọc):** Kêu gọi sự hỗ trợ và chú ý từ cộng đồng khi tác vụ đang bị thiếu nhân lực hoặc cần thêm góc nhìn chuyên môn [7:37].
7. **`invalid` (Màu vàng đất):** Gắn cờ cho các vấn đề không hợp lệ, thông tin không chính xác hoặc không phù hợp với mục tiêu dự án [7:37].
8. **`question` (Màu hồng):** Đánh dấu các trường hợp cần cung cấp thêm thông tin, yêu cầu giải thích hoặc giải đáp thắc mắc chuyên môn [7:37].
9. **`wontfix` (Màu trắng/xám):** Đánh dấu các vấn đề mà nhóm phát triển quyết định từ chối xử lý (không nằm trong kế hoạch triển khai) [7:37].

Bên cạnh bộ nhãn mặc định, người quản trị kho lưu trữ hoàn toàn có thể nhấp vào nút **New label** để tạo các nhãn tùy biến theo quy chuẩn riêng của tổ chức, hoặc nhấp **Edit** để đổi tên, đổi mã màu hex, cập nhật mô tả, cũng như nhấp **Delete** để xóa bỏ vĩnh viễn các nhãn không cần thiết [7:37], [8:18].

<!-- FIGURE_START: F02 -->
#### Hình F02: Hệ thống Phân loại Nhãn trong Quản lý Dự án GitHub (Labels Ecosystem: Bug, Enhancement, Documentation, Good first issue, Help wanted, Question...)

![Hình F02: Sơ đồ cấu trúc hệ sinh thái nhãn dán trong GitHub thể hiện 9 nhãn dán mặc định phân theo 4 nhóm nghiệp vụ và các thao tác quản trị](assets/M05-L09/F02_he_thong_phan_loai_nhan_labels_ecosystem.svg)

<details>
<summary>Xem mã nguồn sơ đồ (Mermaid)</summary>

```mermaid
flowchart TD
    subgraph Ecosystem ["HỆ THỐNG PHÂN LOẠI NHÃN TRONG QUẢN LÝ DỰ ÁN GITHUB (LABELS ECOSYSTEM)"]
        direction TB

        subgraph BuiltInLabels ["1. BỘ 9 NHÃN DÁN ĐƯỢC CẤP SẴN MẶC ĐỊNH (DEFAULT LABELS)"]
            direction TB

            subgraph DefectCat ["Nhóm Phát hiện và Xử lý Lỗi"]
                direction LR
                L_Bug["bug:<br/>Báo cáo lỗi phần mềm hoặc chức năng có vấn đề"]
                L_Invalid["invalid:<br/>Vấn đề không hợp lệ, không đúng thực tế"]
                L_Duplicate["duplicate:<br/>Issue hoặc Pull Request bị trùng lặp"]
                L_Wontfix["wontfix:<br/>Từ chối sửa chữa (không nằm trong kế hoạch)"]
            end

            subgraph FeatureCat ["Nhóm Nâng cấp Tính năng"]
                direction LR
                L_Enhancement["enhancement:<br/>Yêu cầu hoặc phát triển tính năng mới<br/>(Áp dụng cho Issue tạo trang đăng nhập)"]
            end

            subgraph CommunityCat ["Nhóm Hỗ trợ Cộng đồng và Thành viên mới"]
                direction LR
                L_GoodFirst["good first issue:<br/>Tác vụ nhập môn dành cho người mới"]
                L_HelpWanted["help wanted:<br/>Cần trợ giúp thêm từ các thành viên khác"]
            end

            subgraph KnowledgeCat ["Nhóm Thông tin và Tài liệu"]
                direction LR
                L_Doc["documentation:<br/>Cải tiến hoặc bổ sung tài liệu hướng dẫn"]
                L_Question["question:<br/>Yêu cầu làm rõ thông tin hoặc giải đáp thắc mắc"]
            end
        end

        subgraph LabelOperations ["2. CÁC THAO TÁC QUẢN TRỊ NHÃN DÁN (LABEL OPERATIONS)"]
            direction LR
            OpCreate["Tạo nhãn mới (New label):<br/>Tùy biến tên, màu sắc Hex, mô tả"]
            OpEdit["Chỉnh sửa (Edit):<br/>Đổi tên, cập nhật màu, sửa định nghĩa"]
            OpDelete["Xóa nhãn (Delete):<br/>Loại bỏ nhãn khỏi toàn bộ kho lưu trữ"]
        end

        subgraph ApplicationWorkflow ["3. QUY TRÌNH ỨNG DỤNG NHÃN DÁN TRONG THỰC TẾ"]
            direction LR
            AppIssue["Tạo Issue mới"]
            AppSelect["Sidebar: Chọn nhãn tương ứng<br/>(Ví dụ: Gán nhãn enhancement)"]
            AppFilter["Phân luồng và Lọc nhanh:<br/>Tìm kiếm Issues theo nhãn trên kho lưu trữ"]
            AppIssue --> AppSelect --> AppFilter
        end
    end

    BuiltInLabels --> LabelOperations --> ApplicationWorkflow
```
</details>

*Hình F02: Bản đồ cấu trúc hệ sinh thái nhãn dán trong GitHub: Phân loại 9 nhãn tiêu chuẩn thành 4 nhóm nghiệp vụ chính, các quyền thao tác quản trị và quy trình ứng dụng lọc công việc [7:03], [7:37], [8:18].*

**Giải thích trực quan:** Sơ đồ tổ chức 9 nhãn dán mặc định của GitHub thành 4 nhóm nghiệp vụ rõ ràng: Nhóm xử lý lỗi (`bug`, `invalid`, `duplicate`, `wontfix`), Nhóm tính năng (`enhancement`), Nhóm hỗ trợ cộng đồng (`good first issue`, `help wanted`), và Nhóm tài liệu/tri thức (`documentation`, `question`). Nhánh quản trị cho thấy các quyền tạo mới, chỉnh sửa và xóa nhãn, giúp người học hiểu rõ cách nhãn dán biến một kho lưu trữ hỗn độn thành một hệ thống phân luồng công việc khoa học.
<!-- FIGURE_END: F02 -->

---

### 3.4. Quản lý Cột mốc (Milestones) và Theo dõi Tiến độ Phát hành [8:18], [9:08], [10:03]

Sau khi khảo sát nhãn dán, giảng viên chuyển sang thẻ điều hướng bên cạnh mang tên **Milestones** [8:18]. Giảng viên đưa ra định nghĩa nền tảng: **Milestones về bản chất chính là các hạn chót (Milestones are basically deadlines)** [8:18].

Trong quy trình phát triển sản phẩm thực tế, khi chuẩn bị tung ra một đợt phát hành phần mềm mới (release), nhóm phát triển thường đặt tên phiên bản như `release 1`, `release 2`, `v1.0`, `v2.0`... và mỗi đợt phát hành đều gắn chặt với một hạn chót hoàn thành bắt buộc [8:18]. 

GitHub cung cấp Milestones với mục đích: **Sử dụng Milestone để tạo ra một tập hợp (collection) gom nhóm các Issues và Pull Requests phục vụ cho một phiên bản phát hành hoặc một dự án cụ thể** [8:18], [9:08]. Khi chúng ta khởi tạo các Issues và gắn thẻ chúng vào Milestone `release 1`, toàn bộ các đầu việc cần làm cho phiên bản 1 sẽ tự động nằm gọn dưới sự quản lý tập trung của Milestone đó [8:18].

Giảng viên thực hiện các bước khởi tạo Milestone mẫu trực tiếp trên giao diện [9:08], [10:03]:
1. Nhấp vào nút **Create a milestone** (hoặc **New milestone**) [9:08].
2. **Tiêu đề (Title):** Nhập `release 1` [9:08].
3. **Mô tả ngắn (Short description):** Nhập *"This is a milestone for release 1 version of our login page"* (Đây là cột mốc cho phiên bản phát hành 1 của trang đăng nhập) [9:08]. Lý do chọn mô tả này là vì lát nữa chúng ta sẽ tạo một Issue mang tên *create a login page* gắn liền với phiên bản này [9:08].
4. Nhấp nút lưu cột mốc: Cột mốc hiển thị ban đầu với trạng thái `release 1` kèm ghi chú *"no due date"* (chưa có ngày đến hạn) [9:08].
5. **Cấu hình hạn chót (Deadline):** Giảng viên nhấp vào nút **Edit**, chọn trường Due date và thiết lập hạn chót là **ngày 30 của tháng hiện tại (30th of this month)**, sau đó nhấp lưu thay đổi [10:03].
6. **Động cơ đo lường tiến độ (Progress Tracking Engine):** Giao diện Milestone hiển thị thanh tiến độ với thông số: **`0% complete`**, kèm bộ đếm các đầu việc đang mở (`open`) và đã đóng (`closed`) [10:03]. Do chưa có Issue nào trong Milestone này được giải quyết và đóng lại, tỷ lệ hoàn thành được tính toán chính xác là 0% [10:03].
7. Người quản trị có toàn quyền nhấp **Edit** để cập nhật hạn chót, **Close** để đóng toàn bộ cột mốc khi phiên bản được phát hành thành công, hoặc **Delete** để xóa cột mốc nếu kế hoạch phát hành bị hủy bỏ [10:03].

Kết thúc phần thiết lập, giảng viên nhấp quay lại thẻ **Issues** chính: Giao diện tổng quan lúc này xác nhận hệ thống đã sẵn sàng với **1 Milestone** vừa tạo và **9 nhãn dán tiêu chuẩn** có sẵn [10:03].

<!-- FIGURE_START: F03 -->
#### Hình F03: Mô hình Quản lý Cột mốc và Theo dõi Tiến độ Phát hành (Milestones & Release Tracking: Gom nhóm Issues, Thiết lập Deadline, Tính toán tỷ lệ hoàn thành %)

![Hình F03: Sơ đồ mô hình quản lý cột mốc GitHub thể hiện cấu trúc thiết lập, cơ chế gom nhóm Issues và Pull Requests, cùng công thức tính tỷ lệ phần trăm hoàn thành](assets/M05-L09/F03_mo_hinh_quan_ly_cot_moc_va_tien_do_phat_hanh.svg)

<details>
<summary>Xem mã nguồn sơ đồ (Mermaid)</summary>

```mermaid
flowchart TD
    subgraph MilestoneSystem ["MÔ HÌNH QUẢN LÝ CỘT MỐC VÀ THEO DÕI TIẾN ĐỘ PHÁT HÀNH (MILESTONES & RELEASE TRACKING)"]
        direction TB

        subgraph InitMilestone ["1. THIẾT LẬP CỘT MỐC PHÁT HÀNH (CREATE MILESTONE)"]
            direction LR
            M_Title["Tên cột mốc: release 1<br/>(Đại diện cho phiên bản phát hành)"]
            M_Desc["Mô tả: This is a milestone for<br/>release 1 version of our login page"]
            M_Date["Hạn chót (Deadline): Ngày 30 trong tháng<br/>(Due date xác định mốc thời gian hoàn thành)"]
            M_Title --> M_Desc --> M_Date
        end

        subgraph GroupingIssues ["2. CƠ CHẾ GOM NHÓM ISSUES VÀ PULL REQUESTS"]
            direction TB
            GroupDesc["Gom nhóm các đầu việc phục vụ cho cùng một phiên bản phát hành"]
            
            subgraph IssuesInRelease ["Các Issues được gán thuộc tính Milestone: release 1"]
                direction LR
                I1["Issue #1: create a login page<br/>(Đang mở - Open)"]
                I2["Issue #2: setup database schema<br/>(Tác vụ tiếp theo)"]
                PR1["Pull Request #3: Implement basic auth<br/>(Đề xuất mã nguồn tích hợp)"]
            end
            GroupDesc --> IssuesInRelease
        end

        subgraph ProgressEngine ["3. ĐỘNG CƠ THEO DÕI TIẾN ĐỘ VÀ TÍNH TOÁN TỶ LỆ HOÀN THÀNH (%)"]
            direction TB
            Formula["Công thức tính tỷ lệ hoàn thành tự động:<br/>Tỷ lệ % = (Số Issues và PRs đã đóng) / (Tổng số Issues và PRs trong Milestone) x 100%"]
            
            subgraph StatusStages ["Các giai đoạn tiến độ thực tế"]
                direction LR
                Stage0["Khởi tạo ban đầu:<br/>0% complete<br/>(0 closed / 1 open)"]
                StageMid["Quá trình thực hiện:<br/>Tăng dần theo số task hoàn thành<br/>(Ví dụ: 50% complete)"]
                Stage100["Hoàn thành toàn bộ:<br/>100% complete<br/>(Tất cả Issues/PRs đã đóng)"]
                Stage0 --> StageMid --> Stage100
            end
            Formula --> StatusStages
        end

        subgraph LifecycleActions ["4. VÒNG ĐỜI QUẢN TRỊ CỘT MỐC (MILESTONE MANAGEMENT)"]
            direction LR
            ActEdit["Chỉnh sửa (Edit):<br/>Gia hạn deadline hoặc cập nhật mô tả"]
            ActClose["Đóng cột mốc (Close):<br/>Đóng phiên bản khi hoàn thành nghiệm thu"]
            ActDelete["Xóa cột mốc (Delete):<br/>Hủy bỏ khi kế hoạch phiên bản thay đổi"]
        end
    end

    InitMilestone --> GroupingIssues --> ProgressEngine --> LifecycleActions
```
</details>

*Hình F03: Mô hình quản lý cột mốc và theo dõi tiến độ phát hành trong GitHub: Cấu trúc thiết lập release 1, cơ chế gom nhóm đầu việc và công thức đo lường tỷ lệ hoàn thành [8:18], [9:08], [10:03].*

**Giải thích trực quan:** Sơ đồ minh họa tường minh cách Milestone hoạt động như một thùng chứa gom nhóm các Issues và Pull Requests cho đợt phát hành `release 1`. Động cơ theo dõi tiến độ tự động tính toán tỷ lệ % hoàn thành dựa trên tỷ số giữa các đầu việc đã đóng (closed) và tổng số đầu việc. Nhờ đó, người quản lý dự án có cái nhìn trực quan và chính xác về trạng thái sẵn sàng phát hành trước khi chạm hạn chót (deadline).
<!-- FIGURE_END: F03 -->

---

### 3.5. Trình Soạn thảo Issue và Cấu trúc Danh mục Tác vụ (Task List) [10:42], [11:30], [12:26], [13:35]

Khi các cấu hình nền tảng về Nhãn dán và Cột mốc đã hoàn tất, giảng viên nhấp vào nút xanh **New issue** để tiến hành khởi tạo Issue đầu tiên [10:42].

Giao diện trình soạn thảo Issue hiện ra với cấu trúc hai phân vùng rõ rệt [10:42], [11:30]:
- **Phân vùng soạn thảo chính (Bên trái):**
  - **Trường Tiêu đề (Title):** Giảng viên nhập tên của Issue là `create a login page` [10:42].
  - **Chế độ hiển thị kép:** Gồm hai tab chuyển đổi linh hoạt: tab **Write** (khung nhập liệu văn bản với thanh công cụ định dạng Markdown) và tab **Preview** (kết xuất giao diện trực quan trước khi gửi) [10:42], [13:35].
- **Thanh thuộc tính siêu dữ liệu (Sidebar bên phải):** Cho phép gán các thuộc tính quản trị quan trọng cho Issue [10:42], [11:30]:
  - **Assignees:** Phân công thành viên cụ thể trong nhóm chịu trách nhiệm xử lý Issue [10:42], [11:30].
  - **Labels:** Gán một hoặc nhiều nhãn phân loại (ví dụ: `enhancement`) [11:30].
  - **Projects:** Đưa Issue vào các bảng quản lý dự án của GitHub [11:30].
  - **Milestones:** Gán Issue vào một cột mốc phát hành cụ thể (ví dụ: `release 1`) [11:30].
  - **Development:** Liên kết Issue với nhánh làm việc (branch) hoặc Pull Request liên quan để tự động đóng Issue khi mã nguồn được hợp nhất [11:30].

Giảng viên nhấn mạnh nguyên lý sư phạm cốt lõi: **Issue là công cụ lý tưởng để tạo ra một danh mục các nhiệm vụ (list of tasks) nhằm giải quyết một đầu việc lớn hơn** [11:30]. Trong ví dụ tạo trang đăng nhập, thay vì để các lập trình viên tự phỏng đoán công việc, người tạo Issue sẽ phân rã nó thành các nhiệm vụ hành động (actionable tasks) cụ thể thông qua cú pháp **Task List** của Markdown [11:30].

Cú pháp tạo Task List được giảng viên hướng dẫn chi tiết từng ký tự [11:30]:
- Gõ dấu trừ `-`, sau đó là một dấu cách (space), mở ngoặc vuông `[`, một dấu cách, đóng ngoặc vuông `]`, tiếp tục một dấu cách và nhập nội dung nhiệm vụ [11:30].
- Khi gõ xong dòng đầu tiên và nhấn phím Enter, trình soạn thảo GitHub sẽ tự động điền sẵn cú pháp `- [ ] ` cho dòng tiếp theo, giúp quá trình nhập liệu diễn ra liền mạch [11:30], [12:26].

Bốn nhiệm vụ hành động được giảng viên tuần tự thiết lập cho Issue `create a login page` bao gồm [11:30], [12:26]:
1. `- [ ] create a basic login page` (Xây dựng khung giao diện trang đăng nhập cơ bản) [11:30].
2. `- [ ] add authentication` (Bổ sung cơ chế xác thực danh tính người dùng) [12:26].
3. `- [ ] add recaptcha` (Tích hợp dịch vụ reCAPTCHA để phòng chống thư rác và bot) [12:26].
4. `- [ ] improve styling and layout` (hoặc `add styling`: Tinh chỉnh và hoàn thiện định dạng thẩm mỹ, bố cục trang) [12:26].

Khi chuyển sang tab **Preview**, danh sách các dòng văn bản mã nguồn Markdown lập tức được chuyển hóa thành một **danh mục hộp kiểm tương tác (interactive checkbox checklist)** cực kỳ đẹp mắt và trực quan [12:26].

Quay trở lại tab **Write**, giảng viên chỉ ra hai tính năng hỗ trợ quan trọng [13:35]:
- Dòng chữ *"Markdown is supported"*: Khi nhấp vào liên kết này, người dùng sẽ được điều hướng đến tài liệu hướng dẫn định dạng Markdown chính thức của GitHub [13:35].
- Khu vực đính kèm tệp tin đa phương tiện với dòng chữ *"Attach files by pasting, dropping, or selecting them"*: Lập trình viên có thể kéo-thả trực tiếp hoặc dán từ clipboard các tệp hình ảnh, ảnh chụp màn hình (screenshots) để chứng minh lỗi (ví dụ minh họa trang đăng nhập không hoạt động khi hỏi *"Why is the login page not working?"*), hoặc thậm chí tải lên cả tệp video ngắn để mô tả quy trình tái hiện lỗi [13:35].

Sau khi hoàn tất nội dung mô tả, giảng viên nhấp vào nút **Submit new issue** màu xanh lá cây để chính thức tạo Issue [14:14].

---

### 3.6. Vòng đời Trạng thái, Chu trình Thảo luận và Đánh số Thứ tự Tự động [14:14], [14:47], [15:49], [16:43]

Ngay sau khi Issue được khởi tạo thành công, giao diện chuyển sang chế độ hiển thị chi tiết của Issue, mở ra chu trình tương tác và quản lý vòng đời tác vụ [14:14].

#### 1. Cơ chế Tương tác Thảo luận Đa chiều (Engagement & Collaboration) [14:14], [14:47]
- **Phản hồi cảm xúc qua Emojis (Reactions):** Bất kỳ ai có quyền truy cập vào Issue đều có thể nhấp vào biểu tượng cảm xúc (nút like/reaction) ở góc trên bên phải của hộp nội dung để thể hiện sự đồng tình (upvote), không tán thành (downvote), thả tim, cười vui vẻ hoặc ngạc nhiên [14:14]. Tính năng này giúp nhóm khảo sát nhanh ý kiến mà không làm loãng dòng thảo luận [14:14].
- **Chuỗi bình luận (Comment Thread):** Phía dưới nội dung chính là khung nhập bình luận. Giảng viên nhập một lời nhắn mẫu: *"let's get started with creating the login page"* (hãy cùng bắt tay vào xây dựng trang đăng nhập nào) [14:47].
- **Dòng thời gian lịch sử (Issue History / Timeline):** Khi bình luận được gửi đi bằng cách nhấp nút **Comment**, giao diện cập nhật dòng thời gian minh bạch: hiển thị thông báo người dùng vừa bình luận cách đây một phút (*"commented a minute ago"*) [14:47], [15:49]. Mọi sự thay đổi về nhãn dán, cột mốc hay phân công người làm đều được ghi lại tuần tự tại dòng thời gian này [15:49].

#### 2. Quyết định Đóng Issue và Hai Lựa chọn Ý nghĩa (Closing Decisions) [14:47]
Tại khu vực dưới khung soạn bình luận, giảng viên chỉ ra nút điều khiển đóng Issue với hai lựa chọn mang ý nghĩa nghiệp vụ hoàn toàn khác biệt [14:47]:
1. **`Close as completed` (Đóng dưới dạng đã hoàn thành - Màu tím với dấu tích):** Sử dụng khi tác vụ đã được hiện thực hóa trọn vẹn, lỗi đã được sửa chữa, mã nguồn đã được nghiệm thu hoặc yêu cầu đã được đáp ứng đầy đủ (done, closed, fixed, resolved) [14:47].
2. **`Close as not planned` (Đóng dưới dạng không nằm trong kế hoạch - Màu xám với biểu tượng gạch chéo):** Sử dụng khi nhóm quyết định không tiếp tục triển khai đầu việc này vì không còn phù hợp với định hướng, không sửa chữa (wont fix), không thể tái hiện được lỗi (can't produce), hoặc phát hiện Issue bị trùng lặp (duplicate) [14:47].

Người dùng có thể lựa chọn đóng kèm bình luận (**Close with comment**) để giải thích rõ lý do trước khi đóng [14:47]. Trong video, giảng viên chỉ thực hiện gửi bình luận thuần túy mà không đóng Issue để giữ trạng thái mở cho bài học tiếp theo [14:47]. Đồng thời, giảng viên nhấn mạnh: **Nếu một Issue đã bị đóng, người dùng hoàn toàn có thể mở lại nó bất kỳ lúc nào thông qua nút `Reopen issue`** (hoặc `Reopen with comment`), ví dụ khi lỗi bị tái phát (regression bug) hoặc phát sinh yêu cầu bổ sung [14:47].

#### 3. Cơ chế Đánh số Thứ tự Tự động Bất biến (Issue Numbering Engine) [15:49]
Một đặc điểm kỹ thuật rất quan trọng được giảng viên chỉ ra: **GitHub tự động gán số thứ tự `#1` cho Issue này (`create a login page #1`)** [15:49]. 
- Do đây là Issue đầu tiên được khởi tạo trong kho lưu trữ `GH issues demo`, hệ thống tự động cấp phát số định danh bắt đầu từ 1 [15:49].
- Nếu chúng ta tiếp tục khởi tạo Issue thứ hai, nó sẽ tự động nhận số `#2`, và cứ thế tăng tiến tuần tự [15:49].
- Số định danh `#N` này là duy nhất trong phạm vi kho lưu trữ và đóng vai trò là "mã khóa" để tham chiếu chéo giữa các Issue, Pull Request và commit message (ví dụ gõ `#1` trong commit sẽ tạo liên kết trực tiếp tới Issue này) [15:49].

#### 4. Định hướng các Tính năng Nâng cao Kế tiếp [15:49], [16:43]
Khép lại bài học, giảng viên khẳng định bài giảng đã minh họa trọn vẹn và hiệu quả quy trình tạo lập một Issue chuẩn mực [15:49]. Tuy nhiên, hệ sinh thái GitHub Issues vẫn còn rất nhiều năng lực mạnh mẽ sẽ được khai phá chi tiết trong các bài học tiếp theo, bao gồm [15:49], [16:43]:
- Kỹ thuật phân quyền và làm việc với Assignees, Labels, Projects, Milestones, và Development link [15:49].
- Hệ thống thông báo tự động (Notifications), quản lý chuỗi hội thoại (Conversations), ghim Issue trọng tâm lên đầu trang (Pin issue), điều chuyển Issue sang kho lưu trữ khác (Transfer issue), và xóa bỏ vĩnh viễn Issue (Delete issue) [16:43].

<!-- FIGURE_START: F04 -->
#### Hình F04: Vòng đời Trạng thái và Chu trình Tương tác trên Issue (Issue State & Interaction Lifecycle: Open -> Thảo luận/Bình luận/Emojis -> Đóng Close as completed vs Close as not planned -> Reopen)

![Hình F04: Sơ đồ biểu diễn vòng đời trạng thái của một GitHub Issue từ trạng thái Open, chu trình tương tác thảo luận, phân nhánh đóng tác vụ đến cơ chế tái kích hoạt Reopen](assets/M05-L09/F04_vong_doi_trang_thai_va_chu_trinh_tuong_tac.svg)

<details>
<summary>Xem mã nguồn sơ đồ (Mermaid)</summary>

```mermaid
flowchart TD
    subgraph IssueLifecycle ["VÒNG ĐỜI TRẠNG THÁI VÀ CHU TRÌNH TƯƠNG TÁC TRÊN GITHUB ISSUE"]
        direction TB

        subgraph StateOpen ["1. TRẠNG THÁI MỞ (OPEN STATE)"]
            direction TB
            Created["Khởi tạo Issue thành công (Submit new issue)<br/>Tự động gán nhãn trạng thái Open (Màu xanh lục)"]
            
            subgraph EngagementEngine ["Chu trình Tương tác và Thảo luận (Collaboration)"]
                direction LR
                Comments["Thảo luận qua chuỗi bình luận (Comment thread):<br/>Ví dụ: 'let us get started with creating the login page'"]
                Reactions["Phản hồi cảm xúc (Emojis Reactions):<br/>Upvote/Downvote qua nút biểu tượng thích (Like button)"]
                Timeline["Lịch sử cập nhật dòng thời gian (Issue Timeline):<br/>Ghi nhận hoạt động 'user commented a minute ago'"]
                Comments <--> Reactions
                Comments <--> Timeline
            end
            Created --> EngagementEngine
        end

        subgraph DecisionClosure ["2. QUYẾT ĐỊNH ĐÓNG ISSUE (CLOSING DECISION)"]
            direction TB
            CloseAction["Thực thi đóng Issue:<br/>Nút Close issue hoặc Close with comment"]
            
            subgraph TwoCloseModes ["Phân nhánh Trạng thái Đóng (2 Lựa chọn)"]
                direction LR
                CloseCompleted["Close as completed (Màu tím):<br/>- Đã giải quyết triệt để (resolved, fixed)<br/>- Đã hoàn thành các tác vụ (done, closed)"]
                CloseNotPlanned["Close as not planned (Màu xám):<br/>- Không triển khai theo kế hoạch (wont fix)<br/>- Không thể tái hiện lỗi (cant produce)<br/>- Trùng lặp với tác vụ khác (duplicate)"]
            end
            CloseAction --> TwoCloseModes
        end

        subgraph StateClosed ["3. TRẠNG THÁI ĐÓNG (CLOSED STATE)"]
            direction TB
            ClosedResult["Issue chuyển sang trạng thái Closed<br/>Cập nhật tiến độ Milestone và đồ thị dự án"]
        end

        subgraph ReopenMechanism ["4. CƠ CHẾ TÁI KHỞI ĐỘNG (REOPEN MECHANISM)"]
            direction TB
            BtnReopen["Nhấp nút Reopen issue (hoặc Reopen with comment)"]
            ReopenReason["Nguyên nhân tái mở:<br/>- Phát sinh lỗi hồi quy (Regression bug)<br/>- Cần bổ sung yêu cầu mới liên quan"]
            ReopenReason --> BtnReopen
        end
    end

    EngagementEngine --> DecisionClosure
    TwoCloseModes --> StateClosed
    StateClosed --> ReopenMechanism
    BtnReopen -->|Khôi phục trạng thái hoạt động| StateOpen
```
</details>

*Hình F04: Vòng đời trạng thái và chu trình tương tác của một GitHub Issue: Từ khởi tạo trạng thái Open, tương tác thảo luận/Reactions, hai phân nhánh đóng tác vụ đến khả năng tái mở Reopen [14:14], [14:47], [15:49].*

**Giải thích trực quan:** Sơ đồ trạng thái mô tả chu trình khép kín của một Issue. Bắt đầu từ trạng thái `Open`, nhóm dự án tiến hành trao đổi qua comment thread và biểu cảm Emojis. Khi công việc kết thúc, người dùng đứng trước hai ngã rẽ: `Close as completed` (cho các tác vụ thành công) hoặc `Close as not planned` (cho các tác vụ hủy/trùng lặp). Điểm đặc biệt của GitHub Issues là tính khả nghịch cao: Bất kỳ Issue nào ở trạng thái `Closed` đều có thể được phục hồi về `Open` thông qua hành động `Reopen issue` khi xuất hiện lỗi hồi quy.
<!-- FIGURE_END: F04 -->

---

## 4. Ví dụ thực tế & Tình huống minh họa (Practical Application)

### 4.1. Tình huống Thực tế từ Bài giảng: Triển khai Tính năng Trang Đăng nhập

Trong bài học, giảng viên đã dẫn dắt một tình huống thực tế kinh điển trong phát triển phần mềm: Nhóm cần phát triển một giao diện đăng nhập hoàn chỉnh cho hệ thống [3:31], [10:42]. 

Quy trình quản trị Issue được áp dụng chuẩn xác theo các bước sau:
1. **Thiết lập mục tiêu phát hành:** Nhóm xác định tính năng đăng nhập thuộc đợt phát hành `release 1`, hạn chót nghiệm thu là ngày 30 trong tháng [9:08], [10:03].
2. **Khởi tạo Issue mẹ:** Lập trình viên tạo Issue `#1` mang tên `create a login page` [10:42], [15:49].
3. **Phân rã thành 4 đầu việc hành động (Actionable Tasks):** Thay vì một mô tả chung chung, Issue chứa danh mục hộp kiểm Markdown rõ ràng [11:30], [12:26]:
   - `[ ] create a basic login page`: Tạo khung sườn giao diện với HTML (`index.html`) [11:30].
   - `[ ] add authentication`: Xây dựng logic xác thực thông tin đăng nhập [12:26].
   - `[ ] add recaptcha`: Tích hợp bảo mật chống tấn công tự động bằng bot [12:26].
   - `[ ] improve styling and layout`: Áp dụng CSS (`styles.css`) và kịch bản (`script.js`) để nâng cao trải nghiệm người dùng [12:26].
4. **Gán nhãn phân loại:** Gán nhãn `enhancement` để biểu thị đây là tính năng nâng cấp sản phẩm mới [7:37].
5. **Khởi động trao đổi:** Gửi thông điệp mở đầu trong chuỗi bình luận: *"let's get started with creating the login page"* [14:47].

---

### 4.2. [Tình huống mô phỏng sư phạm] Xử lý Báo cáo Sự cố An ninh và Lỗi Xác thực Đăng nhập

Để người học hiểu sâu hơn về cách ứng dụng nhãn dán, đính kèm tệp tin và hai cơ chế đóng Issue trong thực tế vận hành doanh nghiệp, hãy cùng phân tích kịch bản mô phỏng sau:

> **Bối cảnh dự án:** Sau khi phát hành trang đăng nhập, người dùng bên ngoài liên tục gửi phản hồi rằng họ không thể đăng nhập vào hệ thống khi sử dụng trình duyệt di động, màn hình trả về mã lỗi 403 Forbidden.

**Quy trình phản ứng chuẩn mực của nhóm kỹ thuật:**

1. **Khởi tạo Issue báo lỗi (Bug Report):**
   - **Tiêu đề:** `[Bug] Lỗi 403 Forbidden khi đăng nhập từ trình duyệt di động`
   - **Nhãn dán (Labels):** Gán đồng thời hai nhãn `bug` (báo cáo lỗi) và `help wanted` (cần trợ giúp khẩn cấp).
   - **Đính kèm bằng chứng trực quan:** Người báo cáo kéo thả ảnh chụp màn hình điện thoại thể hiện mã lỗi 403 và thông tin phiên bản trình duyệt vào khung đính kèm tệp tin.

2. **Phân công và Điều tra:**
   - **Assignee:** Gán cho kỹ sư Backend phụ trách cổng xác thực API.
   - **Milestone:** Gán vào cột mốc vá lỗi khẩn cấp `hotfix-v1.0.1`.
   - **Thảo luận:** Kỹ sư Backend để lại bình luận giải thích rằng máy chủ phân quyền bị cấu hình sai tiêu đề CORS đối với các yêu cầu từ thiết bị di động.

3. **Xử lý và Đóng Issue (Hai kịch bản phân nhánh):**
   - **Kịch bản A (Khắc phục thành công):** Kỹ sư Backend đẩy commit sửa đổi và tạo Pull Request. Sau khi kiểm thử thành công trên điện thoại thật, kỹ sư nhấp chọn **Close as completed** kèm bình luận: *"Đã sửa lỗi cấu hình CORS trong PR #5, chức năng đăng nhập di động đã hoạt động bình thường."* Thanh tiến độ của Milestone `hotfix-v1.0.1` lập tức nhảy từ 0% lên 100%.
   - **Kịch bản B (Không tái lập được lỗi / Lỗi do người dùng):** Sau khi kiểm tra toàn bộ nhật ký máy chủ, nhóm phát hiện người dùng nhập sai tên miền của môi trường thử nghiệm thay vì môi trường thực tế. Nhóm kỹ thuật nhấp chọn **Close as not planned** kèm bình luận: *"Không thể tái lập lỗi trên môi trường production; sự cố xuất phát từ việc người dùng nhập nhầm URL thử nghiệm. Đóng issue theo quy định."*

Qua tình huống mô phỏng này, người học thấy rõ cách các công cụ trong bài học (Nhãn dán, Đính kèm ảnh, Milestone, Close as completed vs Close as not planned) phối hợp nhịp nhàng để tạo nên một quy trình phát triển phần mềm chuyên nghiệp.

---

## 5. Bảng thuật ngữ chuyên ngành Anh - Việt (Terminology Glossary)

Bảng dưới đây tổng hợp và chuẩn hóa toàn bộ các thuật ngữ chuyên môn then chốt xuất hiện trong bài giảng:

| Thuật ngữ tiếng Anh | Thuật ngữ tiếng Việt | Giải thích ý nghĩa trong ngữ cảnh bài học |
| :--- | :--- | :--- |
| **GitHub Issue** | Vấn đề / Đầu việc GitHub | Tính năng cốt lõi gắn liền với kho lưu trữ, dùng để ghi nhận câu hỏi, báo cáo lỗi phần mềm hoặc lập kế hoạch tính năng mới [0:00], [1:02], [2:19]. |
| **Actionable Task** | Nhiệm vụ hành động | Một đầu việc cụ thể, có thể thực hiện và đo lường được, được phân rã từ một Issue lớn [0:00], [1:02], [11:30]. |
| **Task List** | Danh mục tác vụ | Cú pháp danh sách hộp kiểm trong Markdown (`- [ ] `) cho phép tạo các nhiệm vụ con có thể tương tác đánh dấu hoàn thành [11:30], [12:26]. |
| **Checkbox** | Hộp kiểm | Biểu tượng ô vuông hiển thị trên giao diện Preview của Issue, cho phép nhấp chuột để đánh dấu hoàn thành tác vụ [12:26]. |
| **Labels** | Nhãn dán phân loại | Các thẻ màu sắc ngắn gọn dùng để gắn cờ, phân loại và lọc các Issue và Pull Request theo tính chất nghiệp vụ [7:03], [7:37]. |
| **Default Labels** | Nhãn dán mặc định | Bộ 9 nhãn dán tiêu chuẩn được GitHub tạo sẵn trong mọi kho lưu trữ mới (`bug`, `enhancement`, `documentation`...) [7:37], [8:18]. |
| **Milestone** | Cột mốc phát hành | Công cụ gom nhóm các Issue và Pull Request gắn liền với một hạn chót (deadline) cụ thể cho một phiên bản phần mềm [8:18], [9:08]. |
| **Due Date / Deadline** | Hạn chót hoàn thành | Ngày ấn định mà toàn bộ các đầu việc trong một Milestone phải được giải quyết xong [8:18], [10:03]. |
| **Percentage Complete** | Tỷ lệ phần trăm hoàn thành | Chỉ số đo lường tiến độ tự động của Milestone, tính bằng số đầu việc đã đóng chia cho tổng số đầu việc [10:03]. |
| **Assignees** | Người chịu trách nhiệm | Thuộc tính trên Sidebar chỉ định các thành viên trực tiếp thực thi và giải quyết Issue [10:42], [11:30]. |
| **Development Link** | Liên kết phát triển | Tính năng Sidebar liên kết Issue với nhánh Git (branch) hoặc Pull Request để tự động hóa quy trình [11:30]. |
| **Write & Preview Tabs** | Tab Soạn thảo & Xem trước | Hai chế độ hiển thị song song của trình soạn thảo GitHub: một bên nhập mã Markdown, một bên hiển thị kết quả trực quan [10:42], [12:26], [13:35]. |
| **Syntax Highlighting** | Tô màu cú pháp | Cơ chế tự động nhận diện phần mở rộng tệp và định dạng màu sắc cho từ khóa, biến số và chuỗi ký tự trong mã lệnh [4:40]. |
| **Emojis Reactions** | Phản hồi cảm xúc | Các biểu tượng cảm xúc (like, dislike, heart, smile...) cho phép người dùng upvote hoặc bày tỏ thái độ nhanh trên Issue [14:14]. |
| **Comment Thread** | Chuỗi bình luận | Dòng trao đổi thảo luận chuyên sâu dạng hội thoại bên dưới nội dung chính của Issue [14:14], [14:47]. |
| **Close as Completed** | Đóng: Đã hoàn thành | Thao tác đóng Issue khi công việc đã được xử lý xong, lỗi đã được khắc phục hoàn toàn (màu tím) [14:47]. |
| **Close as Not Planned** | Đóng: Không theo kế hoạch | Thao tác đóng Issue khi nhóm quyết định hủy bỏ, không sửa, không tái lập được lỗi hoặc phát hiện trùng lặp (màu xám) [14:47]. |
| **Reopen Issue** | Mở lại Issue | Hành động phục hồi trạng thái mở của một Issue đã đóng khi phát sinh lỗi hồi quy hoặc cần xử lý tiếp [14:47]. |
| **Issue Numbering (`#N`)** | Cấp phát số định danh tự động | Quy tắc tăng dần tự động của GitHub gán số định danh bất biến (ví dụ `#1`, `#2`) cho mỗi Issue mới trong kho lưu trữ [15:49]. |
| **Project Views** | Góc nhìn dự án | Các chế độ hiển thị dữ liệu Issue đa chiều trong GitHub Projects bao gồm bảng (tables), thẻ kanban (boards) và lộ trình (roadmaps) [0:00], [1:02]. |

---

## 6. Tóm tắt cốt lõi (Key Takeaways)

1. **Issue là trung tâm cộng tác dự án:** GitHub Issues không chỉ dành riêng cho việc báo cáo lỗi mà còn là công cụ lập kế hoạch tính năng mới, đặt câu hỏi kỹ thuật và phân rã các tác vụ hành động thực thi [0:00], [1:02].
2. **Issue gắn chặt với Repository:** Mọi Issue đều thuộc quyền quản lý của một kho lưu trữ cụ thể. Việc tổ chức Issue song hành cùng mã nguồn giúp nhóm lập trình viên kiểm soát toàn diện ngữ cảnh phát triển [2:19], [3:31].
3. **Bộ nhãn dán tiêu chuẩn định hướng luồng công việc:** Sử dụng thành thạo 9 nhãn dán có sẵn (`bug`, `enhancement`, `good first issue`, `documentation`...) giúp phân loại, gắn cờ và lọc nhanh các đầu việc theo mức độ ưu tiên và đối tượng tham gia [7:03], [7:37].
4. **Milestone đo lường tiến độ theo hạn chót:** Milestone gom nhóm các Issue và Pull Request phục vụ một phiên bản phát hành (`release 1`), thiết lập deadline cụ thể và tự động tính toán tỷ lệ phần trăm hoàn thành khi các đầu việc được đóng lại [8:18], [9:08], [10:03].
5. **Cú pháp Task List Markdown biến Issue thành bản kế hoạch hành động:** Sử dụng cú pháp `- [ ] ` để tạo danh mục hộp kiểm có thể tương tác; đính kèm ảnh/video để làm rõ bằng chứng; quản lý chặt chẽ vòng đời qua hai chế độ đóng `Close as completed` và `Close as not planned`, đồng thời tận dụng số định danh duy nhất `#N` để tham chiếu xuyên suốt dự án [11:30], [12:26], [13:35], [14:47], [15:49].

---

## 7. Bài tập & Câu hỏi tự luyện (Review Questions / Practice)

### Câu hỏi ôn tập lý thuyết

1. **Phân tích sự khác biệt về bản chất giữa hai lựa chọn đóng Issue:** Hãy so sánh chi tiết mục đích sử dụng, ngữ cảnh áp dụng và biểu tượng hiển thị giữa `Close as completed` và `Close as not planned`. Nếu một lập trình viên báo cáo lỗi trùng lặp với một Issue đã có từ trước, bạn nên chọn phương án đóng nào và tại sao? [14:47]
2. **Nguyên lý tính toán tiến độ của Milestones:** Hãy giải thích cách GitHub tính toán chỉ số phần trăm hoàn thành (`% complete`) trong một Milestone. Giả sử một Milestone có 4 Issues được gán vào, trong đó có 1 Issue được đóng với trạng thái `Close as completed` và 1 Issue đóng với trạng thái `Close as not planned`, tỷ lệ hoàn thành hiển thị là bao nhiêu phần trăm? [8:18], [10:03]
3. **Cú pháp Task List và Lợi ích sư phạm:** Tại sao trong quản lý dự án Agile, việc phân rã một Issue lớn (như *Create a login page*) thành danh mục các nhiệm vụ nhỏ bằng cú pháp `- [ ] ` lại mang lại hiệu quả cao hơn việc viết một đoạn văn bản mô tả thông thường? [1:02], [11:30], [12:26]

---

### Bài tập thực hành tái hiện Lab (Hands-on Practice Guide)

Hãy truy cập vào tài khoản GitHub cá nhân và thực hiện chính xác các bước sau để làm chủ toàn bộ kỹ năng trong bài học:

- **Bước 1: Khởi tạo kho lưu trữ thực hành:**
  1. Đăng nhập vào GitHub, nhấp vào biểu tượng dấu cộng `+` ở góc trên cùng bên phải và chọn **New repository**.
  2. Đặt tên kho lưu trữ là `GH-issues-demo` (chế độ **Public**).
  3. Đánh dấu chọn **Add a README file** và nhấp nút **Create repository** [3:31].
- **Bước 2: Chuẩn bị mã nguồn trang đăng nhập mẫu:**
  1. Tạo tệp `index.html`: Nhấp **Add file** -> **Create new file**, đặt tên `index.html`, nhập mã khung HTML cơ bản của trang đăng nhập và nhấp **Commit changes** [4:40].
  2. Tạo tệp `styles.css`: Tạo tệp mới đặt tên `styles.css`, nhập một số thuộc tính CSS mẫu cho `body` và commit tệp [6:02].
  3. Tạo tệp `script.js`: Tạo tệp mới đặt tên `script.js` và commit tệp [6:02].
- **Bước 3: Khảo sát nhãn dán và khởi tạo Milestone:**
  1. Nhấp vào tab **Issues** trên thanh điều hướng kho [7:03].
  2. Nhấp vào nút **Labels**, khảo sát danh sách 9 nhãn mặc định và xác định nhãn `enhancement` [7:37].
  3. Nhấp vào nút **Milestones** -> nhấp **New milestone** [8:18], [9:08].
  4. Nhập tiêu đề: `release 1`; phần mô tả: `This is a milestone for release 1 version of our login page` [9:08].
  5. Thiết lập hạn chót (Due date) là ngày cuối cùng của tháng hiện tại và nhấp lưu [10:03].
  6. Quan sát thanh tiến độ ban đầu hiển thị `0% complete` [10:03].
- **Bước 4: Khởi tạo Issue với danh mục Task List:**
  1. Quay lại tab **Issues**, nhấp nút **New issue** [10:42].
  2. Nhập tiêu đề: `create a login page` [10:42].
  3. Trong khung soạn thảo tab `Write`, nhập danh mục 4 tác vụ bằng cú pháp Markdown [11:30], [12:26]:
     ```markdown
     - [ ] create a basic login page
     - [ ] add authentication
     - [ ] add recaptcha
     - [ ] improve styling and layout
     ```
  4. Chuyển sang tab `Preview` để kiểm tra các hộp kiểm được hiển thị chuẩn xác [12:26].
  5. Trên Sidebar bên phải, tại mục **Labels** chọn `enhancement`; tại mục **Milestones** chọn `release 1` [11:30].
  6. Nhấp nút **Submit new issue** [14:14].
- **Bước 5: Trải nghiệm tương tác và quản lý Issue:**
  1. Quan sát số thứ tự Issue được cấp phát tự động là `#1` [15:49].
  2. Nhấp vào biểu tượng Reactions (nút Like) trên đầu Issue để thử thả biểu cảm cảm xúc [14:14].
  3. Tại khung bình luận phía dưới, nhập: `let's get started with creating the login page` và nhấp nút **Comment** [14:47].
  4. Quan sát dòng thời gian lịch sử hiển thị bình luận mới được ghi nhận [15:49].
  5. Thử nhấp chuột vào một hộp kiểm trong Task List (ví dụ đánh dấu `create a basic login page` đã xong) và quan sát hộp kiểm được chuyển sang trạng thái đã tích chọn trực tiếp trên giao diện [12:26].

---

## 8. Nguồn đối chiếu (Source Traceability) — 📜 Transcript (Lời giảng viên)

### 8.1. Ma trận đối chiếu chi tiết theo dòng thời gian và đề mục gốc (📜 Transcript (Lời giảng viên))

Bảng dưới đây thiết lập mối liên kết truy vết 100% giữa nội dung giáo trình sư phạm, hệ thống sơ đồ trực quan và các mốc định danh/thời gian trong tài liệu bài giảng gốc:

| Phần giáo trình | Hình vẽ trực quan | Mốc vị trí / Định danh gốc | Nội dung đối chiếu trong tài liệu gốc |
| :--- | :--- | :--- | :--- |
| **Tiêu đề bài học & Mở đầu tổng quan** | **Hình F01** | `🎥 GitHub Issues - Creating an Issue`, `📜 Transcript (Lời giảng viên)`, `0:00` | Giới thiệu bài học về GitHub Issues; mở trình duyệt tại URL `github.com/issues` hoặc `github.com/features/issues`; nhấn mạnh Issues là tính năng toàn diện của GitHub; liệt kê các khả năng: tạo issue, phân rã thành tasks, theo dõi quan hệ, thêm trường tùy biến, hội thoại, xem bảng/boards/roadmaps và tự động hóa; khẳng định Issues giúp làm việc cộng tác nhóm [0:00]. |
| **Hai trường hợp sử dụng & Năng lực cộng tác** | **Hình F01** | `📜 Transcript (Lời giảng viên)`, `1:02` | Hướng dẫn đặt câu hỏi qua việc tạo issue (ví dụ: "Tại sao trang đăng nhập không hoạt động?"); tạo issue cho dự án nhỏ (ví dụ: "Tạo trang đăng nhập") và phân rã thành nhiều tác vụ hành động; giới thiệu giao diện project view gom nhóm issues; nhấn mạnh issues giúp thúc đẩy hội thoại và theo dõi tiến độ qua project insights [1:02]. |
| **Đa nền tảng quản trị & Khởi tạo kho lưu trữ** | **Hình F01** | `📜 Transcript (Lời giảng viên)`, `2:19` | Chia sẻ quy chuẩn thực hành với mẫu dự án; issues có thể xem, tạo và quản lý trên trình duyệt, terminal hoặc điện thoại/máy tính bảng; giải thích FAQs; chuyển sang GitHub tạo kho lưu trữ mới để thử nghiệm; nhấn mạnh Issue là một tính năng gắn liền với một kho lưu trữ (repository) [2:19]. |
| **Tạo kho `GH issues demo` & Hỏi mã nguồn ChatGPT** | — | `📜 Transcript (Lời giảng viên)`, `3:31` | Tạo kho mới mang tên `GH issues demo`; thêm tên vào từ điển để không hiện gạch đỏ; không cần mô tả; chọn public repository; khởi tạo với tệp README; giải thích mục tiêu tạo issue "create a login page" và nhu cầu có mã nguồn mẫu; chuyển sang ChatGPT nhờ sinh mã cho trang đăng nhập [3:31]. |
| **Sinh mã HTML và Commit tệp `index.html`** | — | `📜 Transcript (Lời giảng viên)`, `4:40` | Ra lệnh cho ChatGPT sinh mã trang đăng nhập mẫu; ChatGPT tạo `index.html` và `styles.css`; sao chép mã HTML; quay lại GitHub tạo tệp mới `index.html`, dán mã; hiển thị tính năng tô màu cú pháp (syntax highlighting); commit tệp với thông điệp mặc định [4:40]. |
| **Tạo tiếp `script.js`, `styles.css` & Vào tab Issues** | — | `📜 Transcript (Lời giảng viên)`, `6:02` | Sao chép mã CSS từ ChatGPT (bắt đầu từ body); tạm dừng video tạo nhanh `script.js` và `styles.css`; quay lại xác nhận có đủ 3 tệp (`index.html`, `script.js`, `styles.css`); điều hướng sang tab Issues của kho lưu trữ [6:02]. |
| **Giao diện Issues & Khảo sát nút Labels** | **Hình F02** | `📜 Transcript (Lời giảng viên)`, `7:03` | Vào kho `GH issues demo`; xuất hiện thông điệp gán nhãn cho issues và pull requests cho người đóng góp mới; lưu ý issues và PR liên quan chặt chẽ với nhau; nhấp vào nút Labels để xem các nhãn dán đơn giản có sẵn [7:03]. |
| **Phân tích 9 nhãn dán tiêu chuẩn của GitHub** | **Hình F02** | `📜 Transcript (Lời giảng viên)`, `7:37` | Giải thích chi tiết các loại nhãn: `bug` (lỗi), `documentation` (tài liệu), `duplicate` (trùng lặp), `enhancement` (tính năng mới - sẽ gán cho issue mẫu), `good first issue` (dành cho người mới), `help wanted` (cần trợ giúp), `invalid` (không hợp lệ), `question` (cần thêm thông tin); khả năng tạo nhãn mới [7:37]. |
| **Quản trị nhãn & Giới thiệu Cột mốc (Milestones)** | **Hình F02**, **Hình F03** | `📜 Transcript (Lời giảng viên)`, `8:18` | Có thể chỉnh sửa (edit), xóa (delete) các nhãn mặc định; nhấp sang tab Milestones; định nghĩa Milestones về bản chất là các hạn chót (deadlines); ví dụ tạo bản phát hành `release 1`, `release 2`; dùng milestone để gom nhóm các issues và PRs cho một đợt phát hành hoặc dự án [8:18]. |
| **Khởi tạo Milestone `release 1` cho trang đăng nhập** | **Hình F03** | `📜 Transcript (Lời giảng viên)`, `9:08` | Nhấp tạo milestone mới; đặt tên `release 1`; nhập mô tả: "This is a milestone for release 1 version of our login page" (vì sẽ tạo issue create a login page); tạo milestone; hiển thị ban đầu chưa có ngày đến hạn (no due date); nhấp Edit để nhập deadline [9:08]. |
| **Thiết lập Deadline ngày 30 & Kiểm tra tiến độ 0%** | **Hình F03** | `📜 Transcript (Lời giảng viên)`, `10:03` | Cấu hình hạn chót là ngày 30 trong tháng; lưu thay đổi; hiển thị deadline; các nút edit, close, delete; hiển thị tiến độ 0% complete (do chưa đóng issue nào); nhấp lại tab Issues; xác nhận có 1 milestone và 9 nhãn có sẵn [10:03]. |
| **Mở trình soạn thảo Issue & Đặt tiêu đề** | **Hình F01** | `📜 Transcript (Lời giảng viên)`, `10:42` | Nhấp nút New issue; vào giao diện soạn thảo issue; đặt tiêu đề issue: `create a login page`; giới thiệu bố cục hai phần: editor bên trái với tab Write/Preview và thanh công cụ Markdown, sidebar bên phải với các trường phân công [10:42]. |
| **Thanh thuộc tính Sidebar & Bắt đầu tạo Task List** | **Hình F01** | `📜 Transcript (Lời giảng viên)`, `11:30` | Phân tích các mục sidebar: Assignees, Labels, Projects, Milestones, Development; giải thích issue là cách tạo danh sách tác vụ cho một đầu việc lớn; hướng dẫn cú pháp Markdown Task List: dấu trừ, dấu cách, mở ngoặc vuông, dấu cách, đóng ngoặc vuông; tạo tác vụ đầu tiên: `create a basic login page` [11:30]. |
| **Phân rã đủ 4 tác vụ hành động & Xem Preview** | **Hình F01** | `📜 Transcript (Lời giảng viên)`, `12:26` | Nhấn Enter tự sinh dòng task tiếp; tác vụ 2: `add authentication`; tác vụ 3: `add recaptcha`; tác vụ 4: `improve styling and layout` (hoặc add styling); hoàn thành 4 tác vụ; chuyển sang tab Preview xem danh mục hộp kiểm Markdown được định dạng đẹp mắt [12:26]. |
| **Hỗ trợ Markdown & Khu vực đính kèm ảnh/video** | **Hình F01** | `📜 Transcript (Lời giảng viên)`, `13:35` | Quay lại tab Write; dòng chữ "Markdown is supported" dẫn đến tài liệu GitHub; khu vực đính kèm tệp tin: paste, drop hoặc click để thêm tệp; hỗ trợ đính kèm ảnh chụp màn hình (screenshots) để chứng minh lỗi khi hỏi tại sao trang đăng nhập không chạy; hỗ trợ đính kèm tệp video [13:35]. |
| **Xuất bản Issue & Tính năng phản hồi Emojis** | **Hình F01**, **Hình F04** | `📜 Transcript (Lời giảng viên)`, `14:14` | Nhấp nút Submit new issue để chính thức tạo issue; tính năng thêm biểu cảm emojis (like button) để upvote/downvote ý kiến; tính năng thêm bình luận thảo luận [14:14]. |
| **Gửi bình luận & Cơ chế đóng `completed` vs `not planned`** | **Hình F04** | `📜 Transcript (Lời giảng viên)`, `14:47` | Thêm bình luận mẫu: "let's get started with creating the login page"; gửi bình luận; nút Close with comment; giải thích hai cách đóng: `Close as completed` (done, closed, fixed, resolved) và `Close as not planned` (wont fix, can't produce, duplicate); chỉ bình luận không đóng; nhắc đến tính năng mở lại (reopen issue) [14:47]. |
| **Lịch sử tương tác & Tự động cấp số định danh `#1`** | **Hình F01**, **Hình F04** | `📜 Transcript (Lời giảng viên)`, `15:49` | Quan sát dòng thời gian lịch sử hiển thị bình luận vừa gửi ("commented a minute ago"); chỉ ra GitHub tự động gán số định danh `#1` cho issue này; giải thích issue tiếp theo sẽ nhận số `#2` (đánh số tuần tự bắt đầu từ 1); tổng kết video đã minh họa hiệu quả cách tạo issue [15:49]. |
| **Định hướng tính năng mở rộng & Kết thúc bài học** | — | `📜 Transcript (Lời giảng viên)`, `16:43` | Nhắc đến các tính năng chuyên sâu trong video sau: notifications (thông báo), conversations (hội thoại), pin issue (ghim issue), transfer issue (chuyển kho), delete issue (xóa issue); kết thúc bài học [16:43]. |
"""

output_path = "generated_course/Advanced_Git_and_GitHub_Features/native_v2/attempts/M05-L09/worker-e2b60a0cc81e4721/output.md"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip() + "\n")

print(f"Successfully wrote {len(content)} characters to {output_path}")
