# Course Harness v2 chạy bên trong AGY

TASK_ID: `COURSE-HARNESS-V2-CONTINUOUS-EXECUTION`

Trạng thái triển khai: agent/skill và deterministic tools đã tạo; workflow kiểm thử offline. Producer discovery và skill discovery được quan sát trong AGY CLI **1.4.7**. Native invocation của Worker/Auditor/Repair và metadata thực tế chưa được kiểm chứng bằng AI call. Chưa tuyên bố Definition of Done ở runtime đã đạt.

## Ranh giới thực thi

```text
Operator opens AGY
  → coursera-producer
      → invoke_subagent(coursera-worker, new context)
      → native_tools: record → render → validate
      → invoke_subagent(coursera-auditor, new context, read-only tools)
      → native_tools: schema / rubric / exact hashes
      → if educational FAIL: coursera-repair → revalidate → NEW Auditor, at most 2 repairs
      → native_tools: publish → checkpoint → report → next lesson
```

AGY điều phối mọi lượt suy luận. `course_harness.native_tools` không import Controller, Batch Scheduler, AGY adapter, Gemini adapter hoặc SDK. Mermaid CLI là tiến trình render xác định duy nhất mà visual manager có thể gọi. Không có Python-to-AGY adapter mới, API key hoặc nested `agy -p`.

Tái sử dụng ingest/source classification/checksum, StateManager atomic checkpoint writer, AuditValidator/JSON Schema, Rubric 2.0 score calculation, VisualAssetManager, path normalization, semantic figure binding và image policy. Policy baseline/ảnh đã tách sang `quality_policy.py`; `batch.py` re-export tên cũ để giữ callers/tests. StateManager chỉ import archived API receipt verifier khi thực sự kiểm tra legacy API receipt, ngoài đường native.

Giữ nguyên source, prompts, `config.yaml`, audit schema và các quyết định human acceptance v1. Native state nằm riêng trong `generated_course/COURSE/native_v2/`; không ghi vào `modules/`, `drafts/`, `evidence/checkpoints/` hoặc asset lịch sử v1. `GeminiApiAdapter` tiếp tục disabled và legacy batch policy guard vẫn còn.

## Tài liệu AGY đã đối chiếu

Ngày kiểm tra migration: 2026-10-25. Continuous Execution đối chiếu lại ngày 2026-10-26.

- [Custom subagents](https://antigravity.google/docs/subagents/): Markdown/YAML frontmatter, workspace discovery, `mainAgent`, `subagent`, model tiers, tools, skills và `invoke_subagent` với context mới.
- [Agent manager](https://antigravity.google/docs/cli/commands/agents/): `/agents` để chọn main agent; agent `mainAgent: false` không xuất hiện như một main-agent choice.
- [Skills](https://antigravity.google/docs/skills/): `.agents/skills/NAME/SKILL.md`, progressive loading và CLI skill completion.
- [CLI reference](https://antigravity.google/docs/cli/reference/): các flags của operator command. Local `agy --help` xác nhận `--agent`, `--model`, `--effort`.
- [FAQ](https://antigravity.google/docs/faq): consumer account không hỗ trợ wrapper bên trong coding agent/ứng dụng bên thứ ba. Migration sử dụng chính cơ chế custom agent của AGY; Python không truy cập model/consumer login. Đây không phải xác nhận chung cho mọi use case hay gói tài khoản.

Không dùng API managed-agent docs làm bằng chứng cho consumer CLI. Không vô hiệu hóa permission/provider controls. `commandExecutionPolicy: sandbox` giữ cơ chế permissions của runtime; không tự cấp terminal approval. Thông báo approval của AGY có thể xuất hiện theo thiết lập operator, nhưng không có yêu cầu sao chép prompt hoặc chạy từng vai trò bằng tay.

## Mở Producer và bắt đầu

Operator chạy trực tiếp trong terminal, từ repo root:

```bash
cd /home/khanh/projects/tutor
agy --agent coursera-producer --model gemini-3.8-flash-high --effort high
```

Hoặc mở AGY tại repo root, dùng `/agents`, chọn `coursera-producer`, Enter rồi Esc. Worker/Auditor/Repair là subagent-only, không phải ba main-agent lựa chọn. Frontmatter dùng `model: inherit`; flags/setting parent là yêu cầu model/effort, không phải bằng chứng model thực tế của mọi child.

Skill `coursera-harness` được discovery tự động. Trong lần kiểm tra TUI, completion `/coursera` hiển thị `/coursera-harness`; không thực thi skill hay gửi prompt AI trong task migration.

Yêu cầu mẫu:

> Hãy dùng Coursera Producer biên soạn toàn bộ khóa Agile_Project_Management thành giáo trình tiếng Việt, Continuous Execution, Run Until Complete. Khôi phục checkpoint hiện tại, bỏ qua M01-L01/M01-L02 đã PASS và các bài HUMAN_ACCEPTED. Tự gọi Worker, Auditor độc lập, tối đa hai Repair và Quality Gates. Mỗi 5 bài lưu checkpoint và báo cáo rồi tự lấy batch tiếp theo, không chờ tôi nhập Tiếp tục. Bài lỗi không nghiêm trọng phải ghi BLOCKED cùng nguyên nhân rồi tiếp bài khác; không tự nhận PASS.

Producer mặc định chạy liên tục đến hết phạm vi được giao. Batch 5 bài chỉ là đơn vị checkpoint/report, concurrency 1. Exact lesson IDs giới hạn phạm vi nếu operator yêu cầu; nếu chỉ yêu cầu một khóa thì scope là toàn bộ manifest. Bài BLOCKED/NEEDS_HUMAN_REVIEW được giữ để chẩn đoán và không tự đưa lại vào hàng chờ. Kết quả cuối có thể là COMPLETED_WITH_FAILURES, không đồng nghĩa mọi bài PASS.

Để runtime AGY cũng ngăn kết thúc lượt sớm, operator có thể dùng một lệnh ban đầu, đã được tài liệu chính thức hỗ trợ:

```text
/goal Dùng Coursera Producer khôi phục batch batch-4354c79d8f424ec3 của Agile_Project_Management và chạy liên tục đến hết phạm vi khóa đã lưu. Bỏ qua PASS/HUMAN_ACCEPTED, tự gọi Worker/Auditor/Repair và deterministic tools. Mỗi 5 bài chỉ checkpoint/report rồi tự tiếp batch mới. Không dừng do 30 phút hoặc chờ tôi nhập Tiếp tục. Ghi BLOCKED và tiếp bài khác khi lỗi không nghiêm trọng; chỉ xuất bản đúng Quality Gates và báo đầy đủ các bài lỗi khi hết phạm vi.
```

Đây là một lần khởi động native goal bên trong AGY, không phải lệnh Python/CLI lồng nhau hoặc yêu cầu nhập từng batch. Request ngôn ngữ tự nhiên thông thường vẫn mặc định Continuous Mode trong Producer. /goal bổ sung stop guard của runtime; custom agent không có field đã xác minh để tự bật goal và không giả lập slash command qua terminal. Không tắt permissions hoặc artifact review.

AGY [tự compact context](https://antigravity.google/docs/cli/commands/context/) và [/goal tiếp tục qua các lượt](https://antigravity.google/docs/commands/goal). Producer đọc lại checkpoint sau compaction, không tự dừng vì context đang đầy nếu runtime còn tiếp tục được. [agy --continue và /resume](https://antigravity.google/docs/cli/commands/resume/) là cơ chế operator khôi phục phiên đã mất, không phải automatic session handoff. Không có cam kết chạy vượt quota hoặc tự khởi động lại process.

## Smoke test cần operator thực hiện

Đã thực hiện không AI: `agy --version`, `agy --help`, `agy agents`, mở TUI với flags trên, quan sát Producer active, mở `/agents`, quan sát skill completion rồi thoát. Không gửi natural-language prompt, không gọi model hoặc subagent. UI đã sử dụng cached sign-in và hiển thị model yêu cầu; việc đó không chứng minh model invocation, quota, credits hay billing readiness.

Để xác minh native delegation, operator mở lệnh trên và gửi:

> Chỉ làm smoke test discovery, không sản xuất bài học. Dùng native invoke_subagent gọi từng coursera-worker, coursera-auditor và coursera-repair trong context mới để đọc định nghĩa của chính nó và báo các input còn thiếu. Không gọi CLI/API khác, không sửa source, checkpoint hay baseline. Ghi lại nguyên bản native tool returns và các ID/model/usage thực sự có; thiếu trường nào ghi NOT_VERIFIED. Báo công cụ invoke_subagent có tồn tại và từng agent có được runtime tìm thấy không. Sau đó dừng.

Kết quả cần quan sát: ba named agents được runtime tìm thấy và nhận task, context riêng, không nguồn/baseline bị sửa; native returns được lưu nguyên bản. Một lỗi thiếu lesson packet vẫn có thể chứng minh runtime đã dispatch, nhưng không chứng minh pipeline sản xuất chạy thành công. Nếu runtime/tool không cung cấp `conversation_id`, phần kiểm chứng context sẽ giữ NOT_VERIFIED và tools không cho publication. Cần đối chiếu return shape thật trước khi thêm mapping, không tự chế envelope metadata.

Sau smoke test thành công, chạy một bài có kiểm soát trước batch năm bài. Không dùng Codex hoặc agent bên thứ ba để khởi động các lượt model qua AGY consumer account.

## Công cụ Python

```bash
course_harness/.venv/bin/python -m course_harness.native_tools --help
course_harness/.venv/bin/python -m course_harness.native_tools preflight --course Agile_Project_Management
course_harness/.venv/bin/python -m course_harness.native_tools list-lessons --course Agile_Project_Management --lessons M01-L01 M01-L02 M01-L03 M01-L04 M01-L05
```

Các lệnh trên không gọi model. Preflight kiểm tra định nghĩa agent, manifest và baseline; source checksum được kiểm tra khi list/prepare và mọi transition/resume. Các lệnh stateful dùng bởi Producer được mô tả tại [workflow skill](../.agents/skills/coursera-harness/references/workflow.md). Đây là lời gọi tool nội bộ, không phải quy trình bắt operator nhập từng stage.

Input CLI được validate bởi `native-request.schema.json`; JSON envelopes bởi `native-result.schema.json`; packet/checkpoint/batch bởi các schema `native-packet`, `native-checkpoint`, `native-batch`. Lỗi có code/message/fatal, exit 2 hoặc 3. Dữ liệu ghi trạng thái dùng atomic replacement dưới filesystem lock. Artifact/evidence dùng exclusive creation; khác byte thì từ chối ghi đè.

Công cụ gồm preflight, list-lessons, start-batch, prepare-lesson, record-attempt, process-visuals, validate-draft, validate-audit, record-failure, publish, report-batch, resume. Không có operation tự cấp human acceptance.

## Continuous mode, checkpoint và resume

Continuous là mặc định của start-batch, group size mặc định/tối đa 5, concurrency 1. Scope đầy đủ được lưu trên batch đầu và truyền nguyên vẹn cho successor. Sau report-batch, next_action advance-batch yêu cầu Producer tự gọi advance-batch ngay. Batch mới chọn các lesson đủ điều kiện còn lại từ manifest, bỏ qua PASS đã kiểm chứng, HUMAN_ACCEPTED và lỗi terminal. Producer không kết thúc lượt hoặc hỏi lại quyền chạy sau mỗi group. Chỉ --mode bounded theo yêu cầu dừng sau một group mới giữ giới hạn cũ 30 phút, 40 dispatches và 500.000 known tokens.

Continuous không có hard-stop thời gian, số dispatch hoặc known tokens của Harness. Tối đa 3 dispatch lỗi mỗi lesson và 2 educational Repair vẫn giữ nguyên. Thiếu usage được đếm unreported, không giả thành zero hoặc suy ra tiền. Quota, authentication, model/tool permission và process/session lifetime thực tế do AGY quản lý.

Stateful operations bổ sung:

```bash
course_harness/.venv/bin/python -m course_harness.native_tools start-batch --course COURSE --mode continuous --limit 5
course_harness/.venv/bin/python -m course_harness.native_tools advance-batch --course COURSE --batch BATCH
course_harness/.venv/bin/python -m course_harness.native_tools suspend --course COURSE --batch BATCH --category runtime --diagnostic 'Actual runtime failure'
```

Các lệnh này được Producer gọi nội bộ, không bắt operator điều phối. advance-batch lưu report hoàn tất, successor và liên kết phục hồi được khi process gián đoạn giữa các atomic writes. resume theo liên kết đến batch hiện hành kể cả khi operator chỉ nhớ batch ID đầu tiên. Runtime PAUSED có thể resume khi dịch vụ đã khôi phục; CANCELLED và HALTED không tự mở lại. Suspension không đánh lỗi lesson, xóa active invocation hoặc mất output đã ghi.

Resume request khi process thực sự bị mất:

> Dùng Coursera Producer khôi phục batch batch-4354c79d8f424ec3 của Agile_Project_Management từ checkpoint và tự tiếp tục toàn bộ phạm vi đã lưu. Không chạy lại M01-L01/M01-L02 đã PASS, không yêu cầu Tiếp tục sau mỗi batch.

Gọi resume để xác định stage tiếp. Worker/Repair output đã ghi nhận được dùng lại cho render/validation; Auditor output đã ghi nhận được validate lại, không gọi model lần nữa. Active dispatch cần recover invocation/output có sẵn trước khi phát lệnh mới. Khi invocation mất thật, ghi transient failure trước replacement. Lỗi không nghiêm trọng giữ BLOCKED/NEEDS_HUMAN_REVIEW cùng diagnostics rồi tiếp tục bài khác. Integrity/authentication/budget-critical error vẫn HALTED.

Nâng cấp batch đang dừng là thao tác deterministic một lần:

```bash
course_harness/.venv/bin/python -m course_harness.native_tools upgrade-continuous --course Agile_Project_Management --batch batch-4354c79d8f424ec3
```

Không sửa agent/skill/schema/tool contract trong lúc một Producer khác vẫn đang ghi batch. Hoàn tất hoặc tạm dừng lượt đang chạy, chốt mã rồi mới nâng cấp và nạp lại định nghĩa agent. Filesystem lock chỉ tuần tự hóa từng lệnh deterministic, không khóa toàn bộ phiên native hoặc ngăn chỉnh file trực tiếp. Contract mismatch vẫn phải giữ evidence và dừng để kiểm tra, không tự đổi policy SHA trong checkpoint/receipt.

Chỉ trạng thái đã kiểm tra và pin SHA trong evidence/continuous_execution/upgrade-snapshot.json được nâng cấp. Toàn bộ source, raw output, visuals, audit và publication được kiểm tra lại. Batch/checkpoint trước nâng cấp được lưu tại native_v2/migrations/continuous-v1/. M01-L01/M01-L02 PASS giữ nguyên từng byte checkpoint/publication và old policy SHA được chấp nhận chỉ khi checkpoint khớp snapshot. M01-L03 tiếp ở Auditor, không gọi lại Worker. Contract mismatch khác vẫn là lỗi integrity, không có reset checkpoint hoặc bỏ checksum.

## Chất lượng và provenance

Tám chiều Rubric 2.0, >=90, zero HIGH/BLOCKING, Source Fidelity, INCOMPLETE handling, student cleanliness và exact source/content/visual hashes giữ nguyên. Auditor bị giới hạn tool `view_file`, không sửa candidate. Chỉ audit có hash đúng mới được xét; re-render/normalization diễn ra trước Auditor. Visual checks chặn corrupt SVG, media nhúng, asset/path không được manifest bind. Static checks không chứng minh mọi likeness/layout đều an toàn; hình được xuất bản vẫn pending Human Visual Review. Không có ảnh giảng viên/tác giả, portrait/avatar/headshot/screenshot/thumbnail hoặc recognizable likeness.

Runtime evidence là dữ liệu Producer lưu từ AGY, không phải signed provider attestation. Recorder không chứng minh người cung cấp JSON là AGY. Mọi provenance chỉ là runtime-reported, trường thiếu là NOT_VERIFIED, local attempt ID không giả thành provider invocation ID. Không suy model thực tế từ CLI flag. Publication đòi distinct reported context IDs cho tất cả Worker/Repair/Auditor attempts. Các trust limits này được ghi rõ trong quality report.

Nguồn, approved baselines, checkpoint/acceptance v1 và mọi artifact lịch sử giữ nguyên. Publication v2 có exact candidate bytes, assets, raw audit, quality report và inventory hashes; resume phát hiện sửa đổi sau publication.

## Kiểm thử và xử lý lỗi

```bash
course_harness/.venv/bin/python -m pytest -q course_harness/tests/test_native_tools.py
course_harness/.venv/bin/python -m pytest -q
```

Tests dùng source/agent fixtures trong thư mục tạm và native returns giả có nhãn mock. Test API legacy vẫn chỉ dùng MockTransport. Không test nào cần AGY live hoặc API network. Kiểm thử format/discovery offline không chứng minh runtime invoke_subagent thành công.

- Không thấy Producer: mở đúng repo root, chạy `agy agents`, kiểm tra YAML ở `.agents/agents/coursera-producer/agent.md`, mở lại `/agents`.
- Không thấy skill: kiểm tra `.agents/skills/coursera-harness/SKILL.md` và mở session mới.
- Native tool/agent không tồn tại: dừng NATIVE_DELEGATION_UNAVAILABLE, không chuyển sang subprocess/API/manual prompt copying.
- Thiếu session/model/usage: lưu raw return, báo NOT_VERIFIED, không tự tạo giá trị. Thiếu context độc lập ngăn publication.
- Render/structure lỗi: giữ candidate/diagnostics, BLOCKED lesson. Không bỏ validator để tiếp tục.
- Sai hash/schema/audit score: giữ response gốc, phân loại lỗi; không sửa audit thành PASS.
- HALTED hoặc contract thay đổi ngoài migration đã kiểm tra: giữ state để operator review. Runtime hết quota không thể tiếp tục thì PAUSED; user hủy thì CANCELLED. Không reset checkpoint, đổi source hash hoặc tự khởi động AGY để né giới hạn.

Địa chỉ state/evidence và contract đầy đủ tại [evidence contract](../.agents/skills/coursera-harness/references/evidence-contract.md) và [recovery procedure](../.agents/skills/coursera-harness/references/recovery-procedure.md).
