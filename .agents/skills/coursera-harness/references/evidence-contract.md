# Evidence contract

Schemas: `course_harness/schemas/native-request.schema.json`, `native-result.schema.json`, `native-checkpoint.schema.json` and the unchanged `audit.schema.json`. CLI arguments map directly to request keys, replacing hyphens with underscores. Every tool prints one JSON envelope with schema_version, ok, operation and result or error. A fatal error requires Producer to halt the batch. Exit 2 indicates a nonfatal rejected request; exit 3 indicates a fatal integrity/input failure.

Disk state is under `generated_course/COURSE/native_v2/`:

- `checkpoints/LESSON.json`: one atomic checkpoint per lesson, with stage, attempts, hashes, repair count and history.
- `attempts/LESSON/ATTEMPT/packet.json`: immutable dispatch inputs written before the native invocation.
- `output.md` or `output.json` and `runtime-return.json`: AGY-owned output slots. Create once; never overwrite.
- `response.raw` and `runtime.raw.json`: tool-archived byte-for-byte artifact and native return evidence. A returned object is not proof of provider authentication.
- `processed-*/`: rendered visual files, authoritative visual manifest, normalized candidate and structural validation. Interrupted rendering directories remain diagnostic evidence.
- `batches/BATCH.json` and `active_batch.json`: the full assigned scope, 1–5 lesson checkpoint groups, continuous/bounded mode and successor links. PAUSED records a real runtime limitation; CANCELLED records a user stop; HALTED preserves critical errors. Commands serialize state writes using a filesystem lock.
- `publications/LESSON/ATTEMPT/`: exact audited Markdown, relative assets, audit and quality report. Existing publications are never overwritten.
- `diagnostics/LESSON/`: immutable failures.

Producer must preserve the ACTUAL native tool return without manufacturing a wrapper with model/session fields. The recorder recognizes model, conversation_id, invocation_id, usage and effort only when present in that original JSON. All missing fields are NOT_VERIFIED. If AGY uses a different return shape, preserve it as-is and report that metadata extraction is unsupported; do not guess mappings. Tool-created attempt IDs are local correlation IDs, never represented as provider invocation IDs. Recorded timestamps are local capture times, not provider timestamps.

The native return contract is intentionally conservative until a real runtime invocation can be observed by the operator. The recorder does not authenticate user-supplied JSON and labels it RUNTIME_RETURN_RECORDED_NOT_INDEPENDENTLY_AUTHENTICATED. Distinct actual conversation IDs for Worker/Repair/Auditor are required before a production publication can claim context separation. If AGY does not expose these, record NOT_VERIFIED and route to human review. A model name in requested CLI settings is not observed model provenance. Tokens are taken only from returned usage.total_tokens when it is a nonnegative integer. Missing usage is never zero, and tokens are never converted into invented money.

Auditor output must explicitly carry audited_final_sha256 matching the frozen candidate. For visuals it must also carry visual_figures_audited and visual_manifest_sha256. The deterministic tools never fill in these claims on Auditor's behalf. No automatic human acceptance operation exists.

The local tool boundary trusts the AGY Producer to preserve actual native returns. It is not an OS sandbox or a signed provider attestation. Agent tool restrictions reduce accidental candidate edits; shared-storage permissions do not prove filesystem isolation. Source, candidate, packet, raw output and manifest hashes are checked at every subsequent transition and on resume/publication.

A reviewed scheduling migration is recorded in migrations/continuous-v1/. The prior batch and checkpoint snapshots are immutable. Previously verified PASS checkpoints keep their original bytes and contract SHA; only checkpoints pinned by the reviewed upgrade snapshot are grandfathered, and all source/artifact/audit/publication hashes are still checked. Continuous mode has no artificial wall-time, call-count or known-token halt; actual quota and bounded lesson retries still apply.
