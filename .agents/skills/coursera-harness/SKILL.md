---
name: coursera-harness
description: Produces Vietnamese Coursera lessons continuously within AGY until the assigned scope is complete, in checkpoint/report groups using independent Worker, Auditor and Repair agents with deterministic Course Harness validation and resumable evidence.
---

# Coursera Harness

Use this skill for course-level production and resume requests inside AGY. The Coursera Producer coordinates native subagents. Python tools only read sources, render diagrams, validate, hash, checkpoint and publish. No provider adapter or nested AGY invocation belongs in this path.

Read [workflow.md](references/workflow.md) when starting a batch, [quality-gates.md](references/quality-gates.md) before drafting/auditing, [evidence-contract.md](references/evidence-contract.md) when recording native returns, and [recovery-procedure.md](references/recovery-procedure.md) when resuming or handling errors.

Run `course_harness/.venv/bin/python -m course_harness.native_tools --help` from the repository root. Inputs, JSON results and checkpoints have schemas in `course_harness/schemas/native-*.schema.json`. Inspect `ok` and `next_action`; never infer success from process completion alone.

Default to Continuous Execution for course requests. Keep checkpoint/report batches at 5 lessons by default, maximum 5 per group, concurrency 1. After each group, follow advance-batch automatically until the saved scope is complete. Never wait for the user to say Continue. Only an explicit request to stop after one batch uses --mode bounded. Persist progress after every stage. Use AGY goal continuation when active and allow automatic context compaction; reread disk state after compaction. Suspend only when the runtime actually cannot continue, the user cancels, or a serious unrecoverable failure requires intervention. See the recovery reference for exact stop/resume handling.

Never overwrite historical evidence, mutate raw sources or accepted baselines, create automatic HUMAN_ACCEPTED, invent missing Coursera data or model metadata, or include any instructor/author image or likeness. An automatic production PASS retains pending human visual review.
