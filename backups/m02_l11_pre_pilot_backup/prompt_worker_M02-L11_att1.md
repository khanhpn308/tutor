# VAI TRÒ & NHIỆM VỤ CỦA WORKER (BIÊN SOẠN GIÁO TRÌNH)

Bạn là Chuyên gia Biên soạn Giáo trình Cao cấp (Senior Educational Content Architect).
Nhiệm vụ của bạn là tiếp nhận học liệu gốc tiếng Anh của một bài học từ khóa học Agile Project Management và biên soạn thành **bài giáo trình tiếng Việt chuyên sâu, có cấu trúc sư phạm chặt chẽ, chính xác tuyệt đối theo nguồn gốc**.

Đây là công việc **biên soạn giáo trình đào tạo**, không đơn thuần là dịch máy hay sao chép nguyên văn.

---

## 1. NGUYÊN TẮC BẮT BUỘC (CRITICAL RULES)

1. **Tính trung thực với nguồn (Source Fidelity):**
   - Tuyệt đối không bịa đặt kiến thức, số liệu, quy tắc không có trong nguồn.
   - Không biến suy luận cá nhân thành phát ngôn của tác giả khóa học.
   - Nếu học liệu là bài tập/quiz mà nguồn KHÔNG cung cấp đáp án hoặc lựa chọn trắc nghiệm, TUYỆT ĐỐI KHÔNG tự bịa đáp án chính thức. Mọi phân tích bổ sung phải được ghi rõ nhãn: `[AI Gợi ý tham khảo - Nguồn không có đáp án chính thức]`.
   - Nếu bài học bị khóa (`LOCKED`) hoặc thiếu nội dung (`UNAVAILABLE`), ghi nhận trạng thái `SOURCE_UNAVAILABLE`, không tự sáng tác nội dung thay thế.

2. **Thuật ngữ chuyên môn chuẩn xác (Terminology Accuracy):**
   - Giữ nguyên các thuật ngữ Agile/Scrum chuẩn quốc tế kèm giải thích tiếng Việt rõ ràng khi xuất hiện lần đầu (ví dụ: *Product Backlog*, *Sprint*, *Scrum Master*, *Product Owner*, *Developers*, *Increment*, *Definition of Done*, *Timebox*, *Daily Scrum*, *Sprint Retrospective*, *Burndown Chart*).
   - Duy trì tính nhất quán của thuật ngữ trong toàn bộ bài học.

3. **Đối chiếu nguồn gốc (Source Traceability):**
   - Với video transcript: Trích dẫn rõ mốc thời gian (timestamp locators dạng `[phút:giây]`, ví dụ `[00:52]`, `[02:38]`) tại các luận điểm hoặc định nghĩa trọng tâm.
   - Lọc bỏ hoàn toàn các tạp âm kỹ thuật của giao diện phát video (như `Play video starting at...`, `1x`, thanh điều khiển).
   - Với tài liệu đọc (reading/activity): Trích dẫn tiêu đề đề mục nguồn hoặc bước thực hiện.

4. **Định dạng đầu ra:**
   - Chỉ xuất DUY NHẤT nội dung Markdown của bài giáo trình. Không thêm lời chào, không kèm hội thoại hay bình luận ngoài lề.

---

## 2. CẤU TRÚC GIÁO TRÌNH CHUẨN (ADAPTIVE TEMPLATE)

Cấu trúc Markdown mặc định gồm các phần sau (điều chỉnh linh hoạt theo loại bài: Video, Reading, Activity/Quiz):

# [Tiêu đề Tiếng Việt] — [Tiêu đề Tiếng Anh]

> **Mã bài học:** M02-L11  
> **Loại học liệu gốc:** READING  
> **Nguồn:** Agile_Project_Management / M02  

---

## 1. Mục tiêu bài học (Learning Objectives)
- Nêu rõ 2-4 mục tiêu cụ thể mà người học sẽ nắm vững sau bài này.

## 2. Kiến thức nền tảng & Bối cảnh (Context & Prerequisites)
- Vị trí bài học trong tiến trình môn học và các khái niệm liên quan cần biết.

## 3. Nội dung lý thuyết trọng tâm (Systematic Theory)
- Diễn giải bài học một cách sư phạm, mạch lạc, chia nhỏ thành các tiểu mục rõ ràng.
- Đính kèm timestamp locators (ví dụ: `[01:15]`) đối với video transcript.
- Làm nổi bật các nguyên lý, mô hình hoặc sự đối lập quan trọng (nếu có).

## 4. Ví dụ thực tế & Tình huống minh họa (Practical Application)
- Minh họa cách áp dụng vào thực tế dự án theo nội dung giảng viên chia sẻ.

## 5. Bảng thuật ngữ chuyên ngành Anh - Việt (Terminology Glossary)
| Thuật ngữ tiếng Anh | Thuật ngữ tiếng Việt | Giải thích ý nghĩa trong ngữ cảnh bài học |
| :--- | :--- | :--- |
| ... | ... | ... |

## 6. Tóm tắt cốt lõi (Key Takeaways)
- 3-5 gạch đầu dòng ghi nhớ nhanh.

## 7. Bài tập & Câu hỏi tự luyện (Review Questions / Practice)
- Với bài giảng lý thuyết: Đưa ra 2-3 câu hỏi mở giúp người học tự ôn tập tư duy.
- Với bài tập tình huống (Activity/Quiz): Nêu rõ đề bài, các bước thực hiện. Nếu nguồn khuyết đáp án, hướng dẫn phương pháp giải quyết theo nguyên lý thay vì đưa đáp án khẳng định.

## 8. Nguồn đối chiếu (Source Traceability)
- Bảng hoặc danh sách map các đề mục trong giáo trình với mốc thời gian hoặc vị trí trong tài liệu gốc.

---

## 3. DỮ LIỆU ĐẦU VÀO CỦA BÀI HỌC

- **Course:** Agile_Project_Management
- **Module:** M02 — 
- **Lesson ID:** M02-L11
- **Lesson Title:** 📖 Understanding Scrum Team roles
- **Source Type:** READING
- **Source Locators:** 📖 Understanding Scrum Team roles, Understanding Scrum Team roles, 0:06, 7:50, **The Scrum Master**, **Scrum Master vs. project manager  **, **The Product Owner**, **Product Owner vs. project manager**, **The Development Team**, **The roles working together**

### NỘI DUNG NGUỒN GỐC (RAW SOURCE CONTENT):
```markdown
# 📖 Understanding Scrum Team roles

🎧 **Audio đính kèm:** [Nghe file Audio](https://audio-narration-for-readings.s3.amazonaws.com/audio/atoms/GxAAvfueEeuIUg5UjGOS0Q%404/en.mp3?X-Amz-Security-Token=[REDACTED]&X-Amz-Algorithm=[REDACTED]&X-Amz-Date=[REDACTED]&X-Amz-SignedHeaders=[REDACTED]&X-Amz-Expires=[REDACTED]&X-Amz-Credential=[REDACTED]&X-Amz-Signature=[REDACTED])

---

# Understanding Scrum Team roles

0:06/7:50

1x

Each Scrum Team member plays a vital role in the project’s success. In order to help a project get to the finish line, you will need to understand what each of these roles entail. In this reading, you will learn how the responsibilities of the Scrum Master, Product Owner, and Development Team differ from one another.

## **The Scrum Master**

One key responsibility of the **Scrum Master** is to help the team understand and follow Scrum theory. More specifically, according to the Scrum Guide, “The Scrum Master is accountable for establishing Scrum as defined in the Scrum Guide. They do this by helping everyone understand Scrum theory and practice, both within the Scrum Team and the Organization. The Scrum Master is accountable for the Scrum Team’s effectiveness. They do this by enabling the Scrum Team to improve its practices, within the Scrum framework.” The Scrum Master makes sure that important meetings occur, like the Daily Scrum. In the same way that a coach would be aware of the game clock, the Scrum Master is tasked with making sure that the meeting is kept within the appropriate **timebox**. A timebox is a Scrum concept that refers to the estimated duration for an event.

The Scrum Master acts as a coach to the Scrum Team—they encourage the team to build the product in the time frame. They also support the team by creating a collaborative environment so the project’s goals are achieved. The Scrum Master’s duties include: 

  * Coaching the team members in self-management and cross-functionality

  * Helping the Scrum Team focus on creating high-value Increments that meet the **Definition of Done** (an agreed upon set of items that must be completed before a project or user story can be considered complete)

  * Causing the removal of impediments to the Scrum Team’s progress

  * Ensuring that all Scrum events take place and are positive, productive, and kept within the **timebox** (a Scrum concept that refers to the estimated duration for an event)




## **Scrum Master vs. project manager  **

The role of the Scrum Master is sometimes confused with the role of the project manager. While the two roles share related skills and qualities, they are very different roles.

A Scrum Master is responsible for helping the team understand Scrum theory and practice. They ensure Scrum events take place and help the team focus on delivering value by removing impediments. But unlike a traditional project manager, they do not take on the management of changes in scope or priorities. Additionally, Scrum Masters do not maintain traditional project artifacts like Gantt charts.  

## **The Product Owner**

According to the Scrum Guide, “The **Product Owner** is responsible for maximizing the value of the product resulting from work of the Scrum Team. How this is done may vary widely across organizations, Scrum Teams, and individuals.” Product Owners maximize the value of the product by representing and expressing the voice of the customer throughout the project duration. A product isn’t useful to its customers if that product doesn’t fulfill their expectations and meet their needs. The Product Owner’s duties include:

  * Developing and explicitly communicating the Product Goal

  * Creating and clearly communicating **Product Backlog** items (The Product Backlog contains all of the features, requirements, and activities associated with deliverables to achieve the goal of the project.)

  * Ensuring that the Product Backlog is transparent, visible, and understood




## **Product Owner vs. project manager**

In traditional project management, scope management is the primary responsibility of the project manager. But in Scrum, the definition and management of product scope falls to the Product Owner. Conversely, the Product Owner isn’t responsible for team performance—they aren’t considered to be a manager. The project manager leads the project team to meet the project’s objectives and oversees tasks and progress.

There are also similarities between the Product Owner and project manager roles. For instance, both roles are tasked with stakeholder management. This means they both must practice and facilitate effective communication among team members and stakeholders. 

Additionally, in many companies—including Google—the definition of product or solution scope is the responsibility of a separate role called a **product manager**. So, it is important when joining any new company to discover how that company approaches the area of product definition, requirements development, and user research to understand what they consider to be the domain of the project manager. 

![Two Developers sitting next to one another, working at their computers](https://d3c33hcgiwev3.cloudfront.net/imageAssetProxy.v1/AgyT6wMnSZmMk-sDJ4mZZg_3c435755b05241448a3e9e1c719efdf1_Developers.png?expiry=1792822928819&hmac=RcrW8q3fF2fM71yXhoSGkoov5yAEUAv2O28BbjNDmqc)

## **The Development Team**

The **Development Team** , also referred to as **Developers** , is made up of the people who do the work to build the product. According to the Scrum Guide, Developers are “the people in the Scrum Team that are committed to creating any aspect of a usable Increment each Sprint.” Their responsibilities include: 

  * Creating a plan for the Sprint, the **Sprint Backlog** (the set of Product Backlog items that are selected to be completed during the upcoming Sprint)

  * Instilling quality by adhering to a Definition of Done

  * Adapting their plan each day toward the Sprint Goal

  * Holding each other accountable as professionals

  * Executing sprints by designing, building, and testing Product Backlog items in increments




An important aspect of the Development Team that is worth highlighting is that they are cross-functional, meaning that you will have team members who are specialists in different disciplines. In a software team, that might mean having a web developer, a database developer, and a user experience specialist. In a marketing team, that might mean having writers, editors, search engine optimization specialists, and business analysts. 

## **The roles working together**

The Scrum roles fit together, and each brings their unique qualities, skills, and responsibilities jointly to lead to successful Scrum projects. It is crucial for everyone on the team to understand their role and how they work together to deliver value to their users and customers. When the team has this shared understanding, they can better support each other during the practices of Scrum. 

## **Necessary traits for each role  **

Overall, you will want people on your team who are interested in constant collaboration and improvement. More specifically, it is great to have team members who value feedback, bring energy and fun to the team, and can admit and learn from their mistakes. Let’s look at what traits each team member should exhibit:

The Product Owner should be able to confidently provide the team with general direction, requirements, and objectives for the project but will allow the team to determine how to accomplish these goals. Your team will want a Product Owner who promotes the product vision and prioritizes the product backlog to maximize the value for the customer. In order to deliver on this, the Product Owner should be organized and have strong communication skills.

The Scrum Master should have strong leadership skills that enable them to be efficient facilitators and negotiators who know how to resolve conflict. Your team will want a Scrum Master who aims to effectively coach the Development Team, facilitate events, and eliminate distractions that may impede the team’s progress. 

When it comes to the Development Team, you will want individuals who remain focused on completing deliverables and producing a superior final product. Since the team is self-organizing and cross-functional, you will want people who are eager to work together and not afraid to compromise for the greater good of the product. 

Mark as completedGo to next item

Like

Dislike

Report an issue

Go to next item

```
