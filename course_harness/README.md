# Course Harness v2: AGY-native production

Đường production mới chạy bằng custom agent **Coursera Producer bên trong AGY**. Producer gọi native subagents, còn Python chỉ kiểm tra, render, ghi evidence/checkpoint và xuất bản. Không dùng Gemini API hoặc Python-to-AGY adapter trong đường này. Xem [hướng dẫn vận hành v2](NATIVE_AUTOMATION.md).

Continuous Execution là mặc định: batch 5 bài chỉ checkpoint/report rồi Producer tự chọn batch tiếp theo đến hết phạm vi. Không có hard-stop 30 phút trong Continuous Mode. Xem phần continuous/resume trong hướng dẫn v2; runtime AGY vẫn quản lý quota, permissions và vòng đời phiên.

Từ repo root, operator mở `agy --agent coursera-producer --model gemini-3.8-flash-high --effort high`, rồi yêu cầu sản xuất khóa học bằng ngôn ngữ tự nhiên. Producer/skill discovery đã kiểm tra trong AGY 1.4.7. Native subagent invocation và hình dạng metadata vẫn cần operator smoke test; chưa xác nhận production end-to-end.

Các phần tiếp theo giữ tài liệu **legacy v1**. Chặn batch Python-to-AGY `POLICY_CLARIFICATION_REQUIRED` và Gemini API disabled vẫn giữ nguyên.

Hệ thống điều phối sản xuất giáo trình đa tác tử (Multi-Agent Course Production Harness) chuyển đổi tài liệu khóa học tiếng Anh từ Coursera thành giáo trình đào tạo tiếng Việt chuyên sâu, có cấu trúc sư phạm, đối chiếu nguồn gốc và được kiểm định độc lập bằng mô hình **Gemini 3.8 Flash High** qua **AGY CLI**.

---

## 1. Kiến trúc hệ thống (Architecture)

```text
tutor/
├── output_course/                 # Học liệu gốc bất biến (Immutable raw sources)
│   └── Agile_Project_Management/
│
├── course_harness/                # Mã nguồn bộ điều tốc (Python Controller)
│   ├── run.py                     # Entry point & CLI Orchestrator
│   ├── config.yaml                # Cấu hình pipeline & model pinning
│   ├── cli_adapter.py             # Adapter giao tiếp AGY CLI & an toàn bảo mật
│   ├── ingest.py                  # Ingestion, SHA256 checksum & phân loại học liệu
│   ├── validator.py               # Deterministic JSON Schema & consistency validator
│   ├── visual.py                  # Visual Learning Design & Mermaid Asset Manager
│   ├── visual_design_system.md    # Hệ thống thiết kế trực quan sư phạm (2.0-visual-first)
│   ├── state.py                   # State machine, Checkpoint & Resume manager
│   ├── fixtures/                  # Deterministic test fixtures & M01-L07 calibration
│   ├── prompts/                   # Prompts tách biệt cho từng vai trò
│   │   ├── worker.md              # Biên soạn giáo trình Visual-First (Drafting)
│   │   ├── auditor.md             # Kiểm định độc lập & Visual Pedagogy
│   │   └── repair.md              # Sửa đổi theo findings & sơ đồ (Targeted Repair)
│   ├── schemas/
│   │   ├── audit.schema.json      # JSON Schema kiểm định chuẩn Draft-07 (Quality Rubric 2.0)
│   │   └── visual_plan.schema.json # JSON Schema Kế hoạch Trực quan hóa & Figure Specs
│   └── tests/                     # Deterministic test suite (128 focused tests)
│
└── generated_course/              # Kết quả sản xuất (Derived outputs)
    └── Agile_Project_Management/
        ├── manifest.json          # Bảng chỉ mục khóa học
        ├── assets/                # Diagram assets (.mmd, .svg, visual_manifest.json)
        ├── drafts/                # Các bản draft Markdown theo phiên bản
        ├── audits/                # Báo cáo JSON kiểm định độc lập
        ├── evidence/              # Checkpoints, logs và metadata phiên gọi AGY
        └── modules/               # Giáo trình hoàn thiện sau khi PASS
```

### 3 Vai trò cốt lõi (Core Roles)
1. **Worker (`draft`):** Nhận học liệu gốc, biên soạn giáo trình tiếng Việt đầy đủ 8-9 phần sư phạm, giữ timestamp và phân loại câu hỏi luyện tập.
2. **Auditor (`independent_audit`):** Hoạt động trong fresh session, không nhận reasoning của Worker, kiểm tra tám chiều Rubric 2.0 và xuất JSON report qua validator xác định.
3. **Repair (`repair`):** Chỉ phẫu thuật các câu chữ thuộc `findings` do Auditor chỉ định, tối đa 2 vòng lặp (repair budget = 2).

---

## 2. Cấu hình Model Pinning (Model Configuration)

Hệ thống bắt buộc gắn chặt (model pinning) cấu hình:
- **CLI:** `agy` (Google Antigravity CLI v1.4.5+)
- **Model:** `gemini-3.8-flash-high`
- **Reasoning Effort:** `high`
- **Policy:** Không tự ý fallback sang Gemini Pro, OpenAI Codex hay bất kỳ model nào khác. Nếu model không khả dụng, hệ thống dừng với mã lỗi `BLOCKED_MODEL_UNAVAILABLE`.

---

## 3. Chế độ thực thi & Chính sách Provider-Use (Execution Modes & Provider-Use Policy)

Hệ thống hỗ trợ 3 chế độ thực thi thông qua cờ `--mode`:

1. **`automated_cli` (Provider dự kiến, giữ tích hợp từng bài đã kiểm thử):**
   - Controller thực thi tiến trình con `agy -p ... --model gemini-3.8-flash-high --effort high --disable-slash-commands --output-format json`.
   - **Chính sách:** [Headless mode](https://antigravity.google/docs/cli/headless/) hỗ trợ script/CI trực tiếp. [FAQ](https://antigravity.google/docs/faq) nói không hỗ trợ wrapper trong coding agent hoặc ứng dụng bên thứ ba trên gói consumer. Script Python cục bộ không tự chứng minh Course Harness được phép.
   - **Batch:** Chặn batch/module/pilot với `POLICY_CLARIFICATION_REQUIRED` trước khi gọi CLI. Không thay chặn này bằng script shell, handoff hay API. Giữ đường code từng bài để bảo toàn tích hợp; kiểm thử kỹ thuật không phải xác nhận chính sách cho tích hợp đó.
2. **`manual_cli_handoff`:**
   - Chỉ dùng để debug/fallback. Đây không phải workflow sản xuất hàng loạt.
   - Controller xuất prompt và tạo file hướng dẫn chi tiết lệnh `agy`.
   - Cơ chế kiểm soát phiên: Controller từ chối các file output cũ từ lần chạy trước (`STALE_MANUAL_OUTPUT`) và ngăn dùng lại output đã tiêu thụ (`REUSED_MANUAL_OUTPUT`). *Lưu ý:* Cơ chế UUID/mtime/consumed cung cấp vệ sinh phiên cục bộ chống dùng nhầm file cũ; đây không phải là bằng chứng xác thực danh tính người vận hành hay chữ ký số mật mã cấp cao.
3. **`mock`:**
   - Dùng cho kiểm thử hồi quy và CI/CD mà không tốn quota hay gọi network.

---

## 4. Hướng dẫn sử dụng (User Guide)

### Kiểm tra readiness offline
```bash
python3 -m course_harness.batch --readiness
```

### Xem kế hoạch năm bài, không gọi provider
```bash
python3 -m course_harness.batch --config course_harness/config.yaml --course Agile_Project_Management --lessons M01-L01 M01-L02 M01-L03 M01-L04 M01-L05 --dry-run --json
```

Chưa cung cấp lệnh live Course Harness vì quyền sử dụng wrapper này trên gói consumer chưa được xác nhận. Không cần sao chép prompt để chạy kiểm thử hoặc dry-run.

### Tiếp tục (Resume) sau khi gián đoạn & Kiểm tra tính toàn vẹn (Integrity Invalidation)
Hệ thống tự động kiểm tra checkpoint tại `generated_course/Agile_Project_Management/evidence/checkpoints/<lesson_id>.json`.
- **Điều kiện Resume:** Bài học chỉ được bỏ qua khi đồng thời:
  1. Checkpoint có trạng thái `PASS`.
  2. Băm nội dung nguồn (`source_sha256`) tính lại trên ổ đĩa khớp 100%.
  3. Băm cấu hình và prompts (`prompt_config_hash`) khớp 100%.
  4. File giáo trình thành phẩm (`final_path`) tồn tại và khớp băm `final_sha256`.
  5. Báo cáo kiểm định (`audit_path`) tồn tại và khớp băm `audit_sha256`.
- **Tự động vô hiệu hóa (Invalidation):** Nếu bất kỳ file nào (nguồn, thành phẩm, báo cáo audit) bị sửa đổi ngoài luồng, checkpoint lập tức chuyển sang `INVALIDATED` và yêu cầu biên dịch lại.
- **Phát hiện Manifest Stale:** Nếu file nguồn trên ổ đĩa bị sửa sau khi manifest tạo ra, Controller kích hoạt `ManifestStaleError`.

---

## 5. Tiêu chuẩn Chất lượng Hợp nhất & Thang điểm (Unified Quality Standard 2.0)

Mỗi báo cáo kiểm định lưu tại `generated_course/Agile_Project_Management/audits/<lesson_id>_audit_v<attempt>.json`. Thang điểm áp dụng trọng số chuẩn hóa:

| Tiêu chí | Trọng số | Mô tả kiểm định |
| :--- | :---: | :--- |
| **SOURCE_FIDELITY** | 25 | Tính trung thực với nguồn, không bịa đặt số liệu hoặc chiều mũi tên sơ đồ. |
| **CONTENT_COMPLETENESS** | 15 | Đầy đủ luận điểm trọng tâm, phát hiện thiếu hụt trực quan hóa. |
| **PEDAGOGICAL_QUALITY** | 15 | Chất lượng diễn đạt sư phạm tiếng Việt, giải thích sâu sắc. |
| **VISUAL_PEDAGOGY** | 15 | Đánh giá 10 khía cạnh trực quan (tương xứng, vị trí, liên kết, alt text, caption, provenance). |
| **TERMINOLOGY_CONSISTENCY** | 10 | Nhất quán thuật ngữ chuyên môn Anh - Việt trong cả chữ và sơ đồ. |
| **SOURCE_TRACEABILITY** | 10 | Đầy đủ mốc thời gian locator đối chiếu với nguồn gốc. |
| **CLARITY_ORGANIZATION** | 5 | Bố cục đề mục logic, mạch lạc. |
| **FORMATTING** | 5 | Chuẩn định dạng Markdown, khối Mermaid, trích dẫn. |
| **TỔNG CỘNG** | **100** | **Ngưỡng đạt (Target Threshold): >= 90.0 điểm** |

```json
{
  "lesson_id": "M01-L07",
  "verdict": "PASS",
  "summary": "Đánh giá tổng quan...",
  "dimension_scores": {
    "SOURCE_FIDELITY": "MET",
    "CONTENT_COMPLETENESS": "MET",
    "PEDAGOGICAL_QUALITY": "MET",
    "VISUAL_PEDAGOGY": "MET",
    "TERMINOLOGY_CONSISTENCY": "MET",
    "SOURCE_TRACEABILITY": "MET",
    "CLARITY_ORGANIZATION": "MET",
    "FORMATTING": "MET"
  },
  "quality_score": 100.0,
  "quality_rubric_version": "2.0-visual-first",
  "visual_figures_audited": 2,
  "findings": []
}
```

### Ý nghĩa của Verdict & Hard Gates:
- **`PASS`:** Điểm chuẩn hóa `>= 90.0`, không có lỗi `HIGH` hoặc `BLOCKING`, không có tiêu chí nào trong `dimension_scores` bị `FAILED`.
- **`FAIL`:** Điểm `< 90.0`, hoặc tồn tại ít nhất một lỗi `HIGH`/`BLOCKING`, hoặc bất kỳ tiêu chí nào bị `FAILED`. Kích hoạt bước Repair (tối đa 2 vòng).
- **`INCONCLUSIVE`:** Tài liệu gốc bị thiếu hoặc khóa (`LOCKED`), không thể kiểm định khách quan.
- **Chuẩn hóa `NOT_APPLICABLE`:** Các bài học ngắn, quiz trắc nghiệm hoặc glossary được miễn trừ trực quan hóa (`NOT_APPLICABLE`), trọng số được chuẩn hóa tương ứng mà không bị trừ điểm oan.

---

## 6. Chạy Bộ Kiểm thử Tự động (Deterministic Test Suite)

Chạy toàn bộ suite bằng môi trường kiểm thử hiện có, không gọi provider live:
```bash
course_harness/.venv/bin/python -m pytest -q
```

Dependencies AGY ở `requirements.txt`. SDK trong `requirements-gemini-api.txt` chỉ phục vụ regression test offline của thử nghiệm API được lưu lại; không phải dependency sản xuất AGY.

Kiểm tra:
- Phân loại học liệu (Video transcript, Reading, Quiz, Activity, Locked).
- Bất biến của thư mục nguồn `output_course/`.
- Validate JSON Schema và tính nhất quán của phán quyết (chặn PASS khi có lỗi HIGH hoặc dimension FAILED).
- Kiểm tra các bẫy xuyên tạc số liệu học liệu (Numerical Claims Fidelity Fixtures).
- Vòng đời State machine, Checkpoint Integrity, và Invalidation khi file thành phẩm/audit bị sửa đổi.
- Phát hiện Manifest Stale khi file nguồn thay đổi.
- Chặn envelope lỗi của AGY CLI (ERROR, WAITING, INTERRUPTED, Model Mismatch).
- Khử thông tin nhạy cảm trên signed URLs và stderr.
- Chặn manual handoff chấp nhận output cũ sai phiên.

---

## 7. Ranh giới Bảo vệ của Auditor & Vấn đề Chưa Kiểm chứng (NOT_VERIFIED)

1. **Ranh giới Read-Only của Auditor:**
   - **Mức Prompt:** Prompt chỉ định Auditor chỉ có nhiệm vụ đánh giá và trả về định dạng JSON thuần túy, tuyệt đối không chỉnh sửa file.
   - **Mức Controller:** Controller chỉ bóc tách JSON từ stdout, không chuyển giao quyền ghi file nào cho Auditor.
   - **Mức Hệ điều hành (Filesystem Sandbox):** Tích hợp hiện có ghi **`NOT_VERIFIED`**. Không suy ra mức cô lập filesystem từ fresh session hoặc từ prompt read-only.
2. **Chính sách Provider-Use:**
   - Hệ thống không tự nhận là "Provider Approved". Cần làm rõ phạm vi Course Harness với provider trước khi bật batch consumer. Không gọi AGY từ Codex hoặc coding agent bên thứ ba.
