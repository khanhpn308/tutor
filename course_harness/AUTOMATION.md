# AGY-native Course Harness v2

Đường production mới là **AGY → Coursera Producer → native Worker/Auditor/Repair → deterministic Python tools**. Python không gọi AGY hoặc API. Xem [hướng dẫn v2](NATIVE_AUTOMATION.md) để mở Producer, vận hành batch và resume.

Continuous Execution là mặc định: batch 5 bài chỉ checkpoint/report rồi Producer tự chọn batch tiếp theo đến hết phạm vi. Không có hard-stop 30 phút trong Continuous Mode. Xem phần continuous/resume trong hướng dẫn v2; runtime AGY vẫn quản lý quota, permissions và vòng đời phiên.

Đã kiểm tra AGY 1.4.7 chọn được Producer và nhận diện skill trong TUI mà không gửi prompt AI. Việc gọi ba subagent và metadata trả về vẫn cần một smoke test do operator thực hiện bên trong AGY. Chưa tuyên bố hoàn thành nghiệm thu runtime end-to-end.

Phần dưới mô tả riêng **legacy v1**. Các chặn chính sách của Python-to-AGY wrapper vẫn giữ nguyên, không áp dụng như một lệnh cấm đối với custom agent native đã được tài liệu AGY hỗ trợ. Bản hướng dẫn trước migration được giữ tại [evidence lịch sử](evidence/native_v2/AUTOMATION-v1-historical.md).

---

# Tự động hóa bằng AGY CLI

TASK_ID: `COURSE-HARNESS-V1-AGY-CLI-AUTOMATION-REALIGNMENT`

Trạng thái: `POLICY_CLARIFICATION_REQUIRED` cho batch live Course Harness. Provider dự kiến là Antigravity CLI với model `gemini-3.8-flash-high`, effort `high`. Không sử dụng Gemini API, API key hoặc pay-per-token integration.

## Chính sách đã đối chiếu

Ngày đối chiếu: 2026-10-25.

[Tài liệu headless chính thức](https://antigravity.google/docs/cli/headless/) mô tả `agy -p`, JSON output, structured output, stream-json, điều khiển nhiều prompt bằng stdin, pin model/effort và CI. Đây là bằng chứng hỗ trợ các cơ chế CLI. Cached authentication vẫn do CLI quản lý; không cần đọc hoặc xuất credential.

[FAQ chính thức](https://antigravity.google/docs/faq) phân biệt script/CI trực tiếp với wrapper trong coding agent hoặc ứng dụng bên thứ ba trên gói consumer. [Điều 6 Additional Terms](https://antigravity.google/terms) hạn chế truy cập bằng phần mềm/công cụ bên thứ ba. [Phản hồi trên diễn đàn Google ngày 16-10-2026](https://discuss.ai.google.dev/t/clarification-on-consumer-plan-policy-for-invoking-official-agy-via-local-subprocess/189905) xác nhận FAQ hiện hành ưu tiên hơn các phản hồi diễn đàn cũ khi chúng khác nhau.

Đánh giá cho repo này là một suy luận có giới hạn. Course Harness có Controller, Scheduler và vòng lặp nhiều vai trò, nên không thể tự nhận là direct scripting được phép chỉ vì dùng subprocess cục bộ. Không có xác nhận cụ thể cho ứng dụng này. Chặn batch live vẫn có hiệu lực.

## Workflow trực tiếp nhỏ nhất và phần chưa rõ

Cơ chế được tài liệu hỗ trợ là script/CI do người vận hành trực tiếp khởi động, chuyển prompt tới CLI chính thức, chờ JSON result, kiểm tra terminal status rồi chuyển prompt tiếp theo. Worker và Auditor cần tiến trình CLI riêng để tách phiên. Một stream-json session chứa cả Worker và Auditor không đáp ứng yêu cầu Auditor độc lập.

Tài liệu hỗ trợ script phản hồi theo kết quả trước đó. Tuy nhiên, đưa Controller/Scheduler Course Harness vào script đó có thể thuộc phạm vi application wrapper mà FAQ không hỗ trợ. Vì vậy chưa thêm script shell/Python mới thực thi vòng lặp này, chưa đổi tên wrapper để bỏ qua chặn, và chưa cung cấp lệnh live cho nó. Cần provider xác nhận chính ứng dụng và luồng sau:

```text
Operator starts Course Harness once
  -> exact course/lesson selection -> immutable source checks
  -> AGY Worker in a fresh CLI process
  -> visual manifest binding and deterministic validation
  -> independent AGY Auditor in another fresh CLI process
  -> up to 2 educational Repairs, each followed by a fresh Auditor
  -> final quality gate -> publication -> checkpoint -> next lesson
```

Phạm vi cần làm rõ là script Python cá nhân, consumer login do CLI chính thức quản lý, không Codex/Claude Code hay coding agent bên thứ ba trong runtime, không OAuth extraction/private endpoint, không account rotation, không server/MCP bridge. Việc mô tả phạm vi này không tự cấp quyền sử dụng. Chưa gửi thông điệp nào tới provider.

## Những gì giữ lại và thay đổi

`config.yaml` và toàn bộ prompt giữ nguyên để bảo toàn hash đã dùng cho baseline. `AgyAdapter` vẫn có `automated_cli`, `manual_cli_handoff` và `mock`. Tích hợp Worker/Auditor/Repair từng bài vẫn hoạt động trong test deterministic. Handoff chỉ là công cụ debug/fallback, không phải đáp án cho workflow sản xuất tự động.

Adapter giữ JSON CLI gốc theo invocation ID riêng, trước cả bước validate. Metadata ghi hash raw/response/prompt, thời gian, model, session và usage thực tế. Thiếu model/session/usage/ID thì giữ trạng thái thiếu, không suy ra từ flag yêu cầu. Các lần chạy mới không ghi đè evidence cũ. Receipt Auditor giữ provenance này cùng SHA256 chính xác của candidate. Fresh process không chứng minh OS-level read-only sandbox; trạng thái đó vẫn `NOT_VERIFIED`.

Deterministic JSON Schema, tám chiều Rubric 2.0, ngưỡng >=90, chặn HIGH/BLOCKING, giới hạn hai Repair, source/content/visual hash và checkpoint/resume được giữ. Không tự cấp `HUMAN_ACCEPTED`. Ảnh, portrait, avatar, headshot, screenshot và likeness của giảng viên/tác giả vẫn bị cấm; suitability của hình không xác minh được bằng kiểm tra tĩnh vẫn cần người duyệt.

`batch.py` vẫn lập kế hoạch đúng course và lesson ID, kiểm tra nguồn/baseline, lưu checkpoint/resume trong các chế độ đã có. Readiness/dry-run nay nêu rõ trạng thái chính sách. Batch/module/pilot AGY dừng trước gọi CLI. Khả năng chạy batch AGY live chưa được xác nhận hoặc bật.

Code/evidence Gemini API được giữ riêng. `gemini_api.yaml` có `enabled: false`, Controller từ chối cấu hình này, và adapter không thể tự tạo SDK client live ngay cả khi môi trường có API key. Chỉ regression test offline truyền mock client. SDK đã tách khỏi `requirements.txt` mặc định sang `requirements-gemini-api.txt`. Hướng dẫn API trước đây được lưu nguyên bản tại [evidence lịch sử](evidence/provider_r1/AUTOMATION-historical.md), không phải hướng dẫn vận hành hiện tại.

## Lệnh operator được cung cấp

Chỉ readiness/dry-run offline, không gọi AGY hoặc API:

```bash
course_harness/.venv/bin/python -m course_harness.batch --readiness
```

```bash
course_harness/.venv/bin/python -m course_harness.batch --config course_harness/config.yaml --course Agile_Project_Management --lessons M01-L01 M01-L02 M01-L03 M01-L04 M01-L05 --dry-run --json
```

Không cung cấp lệnh live Course Harness khi chính sách còn chưa rõ. Không kiểm tra AGY authentication, model availability hoặc quota bằng gọi CLI trong task này. Binary hiện diện không chứng minh account readiness.

## Kiểm thử

```bash
course_harness/.venv/bin/python -m pytest -q course_harness/tests/test_agy_realignment.py
course_harness/.venv/bin/python -m pytest -q
```

Test gọi subprocess bằng mock, kiểm tra chính xác flags/model/effort, các phiên riêng, JSON/usage/hash, Repair và Auditor mới, resume, chặn các entrypoint batch và API inactive. Đây là kiểm thử kỹ thuật, không phải xác nhận chính sách hoặc live readiness. Không sửa nguồn, baseline, evidence/handoff cũ; không commit/push/merge.
