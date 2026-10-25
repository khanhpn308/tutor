# Sản xuất tự động qua Gemini API

Course Harness dùng `GeminiApiAdapter` với SDK `google-genai==2.33.0`, model `gemini-3.8-flash`, thinking `high`. Mỗi Worker, Auditor và Repair là một request độc lập qua `models.generate_content`. Không có thao tác sao chép prompt hay gọi AGY trong chế độ `gemini_api`.

```text
SOURCE → WORKER → VISUAL RENDER → STRUCTURAL VALIDATION → AUDITOR
       → REPAIR khi cần, tối đa 2 lượt → AUDITOR mới
       → FINAL QUALITY GATE → PUBLISH → CHECKPOINT → bài tiếp theo
```

Dùng cấu hình [gemini_api.yaml](gemini_api.yaml). Cấu hình và prompt cũ giữ nguyên để không làm thay đổi hash của các baseline đã duyệt. Đầu ra API nằm riêng tại `generated_course/Agile_Project_Management/gemini_api/`. `output_course/` chỉ được đọc. M02-L11, M03-L08 và các bài HUMAN_ACCEPTED không được chạy lại tự động.

Cài môi trường tại thư mục gốc dự án:

```bash
python -m venv course_harness/.venv
course_harness/.venv/bin/python -m pip install -r course_harness/requirements.txt pytest
```

Cung cấp `GEMINI_API_KEY` qua môi trường hoặc secret manager. Không ghi khóa vào YAML, Git hay file `.env`. Adapter chỉ kiểm tra sự hiện diện của biến khi dry-run. Xác thực, quyền truy cập model và billing chưa được kiểm tra bằng API trong task này.

## Chạy thử không mất phí

```bash
course_harness/.venv/bin/python -m course_harness.batch --config course_harness/gemini_api.yaml --course Agile_Project_Management --lessons M01-L01 --dry-run --json
```

```bash
course_harness/.venv/bin/python -m course_harness.batch --config course_harness/gemini_api.yaml --course Agile_Project_Management --lessons M01-L01 M01-L02 M01-L03 M01-L04 M01-L05 --dry-run --json
```

Dry-run kiểm tra ID khóa học/bài học, nguồn, hai baseline được duyệt, hash draft M01-L01, manifest hình và cấu trúc draft. Nó in kế hoạch đầy đủ, trạng thái SDK/key/renderer, giới hạn tài nguyên và xác nhận không có bước bàn giao thủ công. Nó không gọi provider hay ghi checkpoint bài học.

M01-L01 có draft cũ khớp SHA256 `c50c81928cbfc4d17813c0e24976776ee1853ab31f73b06db63b14b9d3fc2f3b`. Draft này làm đầu vào cho Worker API mới. Evidence AGY cũ chưa xác minh được model nên không được đổi thành evidence API hay dùng để tự cấp PASS. Worker mới kiểm tra lại nguồn, xuất candidate mới; Auditor mới đánh giá đúng hash candidate đó. Các file draft, handoff và evidence cũ giữ nguyên.

## Lệnh live để người vận hành chạy sau

Một bài, khi đã cung cấp khóa và kiểm tra billing/quota:

```bash
course_harness/.venv/bin/python -m course_harness.batch --config course_harness/gemini_api.yaml --course Agile_Project_Management --lessons M01-L01 --execute
```

Năm bài tuần tự:

```bash
course_harness/.venv/bin/python -m course_harness.batch --config course_harness/gemini_api.yaml --course Agile_Project_Management --lessons M01-L01 M01-L02 M01-L03 M01-L04 M01-L05 --execute
```

Scheduler in tiến độ và kết quả từng bài, lưu checkpoint sau từng bài và usage sau từng request. Một bài không đạt chất lượng hoặc nhận response lỗi không nghiêm trọng không chặn các bài tiếp theo. Lỗi xác thực, provenance, checksum hoặc ngân sách dừng batch.

Resume dùng chính danh sách ID đã lưu, không chọn lại các bài:

```bash
course_harness/.venv/bin/python -m course_harness.batch --config course_harness/gemini_api.yaml --course Agile_Project_Management --resume BATCH_ID_FROM_PREVIOUS_RUN --execute
```

Bài PASS chỉ được bỏ qua khi checksum nguồn, nội dung, audit, receipt và hình còn khớp. Candidate và audit đã xác minh cũng được dùng lại nếu tiến trình dừng trước publish. Repair budget giữ qua các lần resume. Nếu tiến trình chết trong lúc request chưa trả về thì usage chưa thể biết; scheduler dừng để đối soát request đó trước khi chi tiếp, không đoán chi phí hoặc tự gọi lại.

Sau khi có batch tuần tự PASS với receipt còn hợp lệ, có thể thêm `--concurrency 2`, tối đa 4. Mỗi bài dùng Controller riêng; scheduler khóa theo khóa học và kiểm tra ngân sách ở ranh giới wave/request. Request đã gửi trong cùng wave có thể hoàn thành khi một request khác gặp lỗi nghiêm trọng. Không có thực thi live đồng thời nào trong task này.

## Giới hạn và chất lượng

`resources` cho phép chọn tối đa 10.000 bài. Cấu hình mặc định vẫn giới hạn 60 request, 500.000 token và 3.600 giây mỗi batch. Tăng các giới hạn này có chủ ý khi triển khai lớn hơn. Không có queue, database hay dịch vụ mới.

Retry lỗi 429/timeout/server tối đa 2 lần, tách riêng khỏi tối đa 2 lượt Repair nội dung. SDK retry ẩn được tắt. Retry-After được tôn trọng; thời gian chờ vượt 60 giây kết thúc bằng lỗi transient để không giữ tiến trình chờ lâu. Mỗi lần thử có metadata riêng và được tính vào quota request. Quota token/runtime chặn request mới ở ranh giới an toàn; request đã gửi có thể vượt phần quota còn lại. Token dùng số provider trả về; thinking token không được cộng lần nữa vào total. Chi phí tiền và currency để `null` vì API không trả hóa đơn cho request. Không quy đổi token thành tiền hoặc suy ra billing readiness. Response thành công thiếu total token khiến batch dừng trước request tiếp theo.

Auditor dùng JSON Schema qua SDK và vẫn phải qua validator xác định của dự án. PASS cần Rubric 2.0 đủ tám chiều, score ≥ 90, không HIGH/BLOCKING, source/content/visual hash khớp và receipt API hợp lệ. Source INCOMPLETE cần `--allow-incomplete`; Worker/Auditor/Repair phải nêu phạm vi thiếu bằng tiếng Việt, không bịa dữ liệu Coursera.

Ảnh giảng viên/tác giả, portrait, avatar, headshot, video screenshot và likeness bị cấm. Tự động chỉ nhận sơ đồ Mermaid render nội bộ và ràng buộc manifest. Ảnh ngoài, raster, media nhúng và đường dẫn không ràng buộc đều bị chặn. SVG giữ trạng thái cần người duyệt; kiểm tra tĩnh không chứng minh nội dung hay bố cục phù hợp. Production PASS không bao giờ tự trở thành HUMAN_ACCEPTED.

Raw response JSON được lưu nguyên văn trong `evidence/gemini_api/`, cùng hash, ID response/request khi có, model version, thời gian và usage gốc. Không ghi exception message của provider vì có thể chứa thông tin xác thực. Các draft/audit API dùng tên invocation riêng để tránh ghi đè bằng chứng.

## Kiểm thử và evidence

```bash
course_harness/.venv/bin/python -m pytest -q
```

`pytest.ini` thu toàn bộ suite đang phát triển ở `course_harness/tests`. Các bản sao lịch sử trong review/acceptance bundle và script đăng nhập Coursera không thuộc suite này. Test API chạy SDK thật trên `httpx.MockTransport`, không gọi endpoint live.

Kế hoạch canary và năm bài cùng báo cáo bảo toàn file nằm tại [evidence/provider_r1](evidence/provider_r1/).

Tài liệu provider dùng để đối chiếu giao diện: [Google GenAI SDK](https://googleapis.github.io/python-genai/), [structured output](https://ai.google.dev/gemini-api/docs/structured-output), [thinking](https://ai.google.dev/gemini-api/docs/thinking).
