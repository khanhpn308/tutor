"""Offline checks of documented AGY command mechanics, not consumer wrapper approval."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest
import yaml

from course_harness.batch import BatchScheduler, main as batch_main
from course_harness.cli_adapter import CliExecutionError, ModelUnavailableError
from course_harness.gemini_adapter import ApiDisabledError, GeminiApiAdapter
from course_harness.provider_policy import provider_readiness
from course_harness.run import BlockedExecutionError, CourseHarnessController, main as run_main

MODEL = "gemini-3.8-flash-high"
DRAFT = "# Bài học\n\n## Tình huống và hướng dẫn\n" + "Nhóm kiểm tra công việc và phản hồi để cải thiện cách thực hiện. " * 6
DIMENSIONS = ["SOURCE_FIDELITY", "CONTENT_COMPLETENESS", "PEDAGOGICAL_QUALITY", "VISUAL_PEDAGOGY",
              "TERMINOLOGY_CONSISTENCY", "SOURCE_TRACEABILITY", "CLARITY_ORGANIZATION", "FORMATTING"]


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def audit(verdict="PASS"):
    return {"lesson_id": "M01-L01", "verdict": verdict, "summary": "Independent evaluation",
            "quality_rubric_version": "2.0-visual-first", "quality_score": 100 if verdict == "PASS" else 75,
            "content_quality_accepted": verdict == "PASS",
            "dimension_scores": {dim: "FAILED" if verdict == "FAIL" and dim == "SOURCE_FIDELITY" else "MET" for dim in DIMENSIONS},
            "findings": [] if verdict == "PASS" else [{
                "finding_id": "F01", "severity": "HIGH", "category": "SOURCE_FIDELITY",
                "source_locator": "source", "draft_locator": "lesson", "description": "Correct the explanation",
                "required_action": "Use the supplied source"}], "limitations": []}


def transport(response, index=1, **extra):
    body = {"status": "SUCCESS", "response": response, "model": MODEL,
            "conversation_id": f"provider-session-{index}",
            "usage": {"input_tokens": 100, "output_tokens": 50, "thinking_tokens": 30, "total_tokens": 150}}
    body.update(extra)
    return subprocess.CompletedProcess([], 0, json.dumps(body, indent=2) + "\n", "")


@pytest.fixture
def controller(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    text = "The team inspects work and feedback to improve its work."
    (source / "lesson.md").write_text(text)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"course_id": "TestCourse", "lessons": {"M01-L01": {
        "lesson_id": "M01-L01", "module_id": "M01", "title": "Team practice", "status": "AVAILABLE",
        "source_type": "ACTIVITY", "relative_path": "lesson.md", "source_sha256": digest(text)}},
        "modules": {}, "total_lessons": 1, "total_modules": 1}))
    config = {"execution": {"mode": "automated_cli"},
              "models": {role: {"model": MODEL, "effort": "high"} for role in ("worker", "auditor", "repair")},
              "workflow": {"max_repair_rounds": 2}, "paths": {
                  "course_id": "TestCourse", "source_dir": str(source), "output_dir": str(tmp_path / "generated"),
                  "manifest_path": str(manifest), "prompts_dir": "course_harness/prompts",
                  "schema_path": "course_harness/schemas/audit.schema.json"}}
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(config))
    result = CourseHarnessController(str(path))
    result.adapter.resolved_binary = "/mock/agy"
    return result


def test_existing_agy_worker_and_independent_auditor_are_automatic(controller):
    replies = [transport(DRAFT), transport(json.dumps(audit()), 2)]
    with patch("course_harness.cli_adapter.subprocess.run", side_effect=replies) as invoke:
        result = controller.process_lesson("M01-L01")
    assert result["status"] == "PASS", result
    assert result["status"] != "HUMAN_ACCEPTED"
    assert invoke.call_count == 2
    prompts = [call.args[0][2] for call in invoke.call_args_list]
    assert "INDEPENDENT AUDITOR" in prompts[1] and DRAFT.strip() in prompts[1]
    receipt = controller.state_mgr.get_audit_receipt(result["audit_invocation_id"])
    assert receipt["conversation_id"] == "provider-session-2"
    assert receipt["audited_final_sha256"] == digest(Path(result["final_path"]).read_text())
    assert receipt["raw_response_sha256"] == digest(replies[1].stdout)
    assert receipt["usage"]["total_tokens"] == 150
    assert not list(Path(controller.evidence_dir).glob("handoff*"))
    with patch("course_harness.cli_adapter.subprocess.run") as invoke:
        assert controller.process_lesson("M01-L01")["status"] == "PASS"
        invoke.assert_not_called()


@pytest.mark.parametrize("verdicts,expected,repairs", [
    (["FAIL", "PASS"], "PASS", 1), (["FAIL", "FAIL", "FAIL"], "NEEDS_HUMAN_REVIEW", 2)])
def test_agy_bounded_repair_requires_fresh_auditor(controller, verdicts, expected, repairs):
    replies = [transport(DRAFT)]
    for index, verdict in enumerate(verdicts):
        if index:
            replies.append(transport(DRAFT + "\n\nBản giải thích đã được chỉnh sửa.", len(replies) + 1))
        replies.append(transport(json.dumps(audit(verdict)), len(replies) + 1))
    with patch("course_harness.cli_adapter.subprocess.run", side_effect=replies) as invoke:
        result = controller.process_lesson("M01-L01")
    assert result["status"] == expected, result
    assert result["repair_attempts"] == repairs
    assert invoke.call_count == 2 + 2 * repairs
    sessions = []
    for call in invoke.call_args_list:
        command = call.args[0]
        assert command[0] == "/mock/agy"
        assert command[command.index("--model") + 1] == MODEL
        assert command[command.index("--effort") + 1] == "high"
        assert command[command.index("--output-format") + 1] == "json"
        assert not {"--continue", "--conversation", "--dangerously-skip-permissions"} & set(command)
        assert call.kwargs["check"] and call.kwargs["timeout"] > 0
    for path in Path(controller.evidence_dir).glob("inv-*.json"):
        if not path.name.endswith(".raw.json"):
            sessions.append(json.loads(path.read_text())["conversation_id"])
    assert len(sessions) == len(set(sessions)) == len(replies)


def test_missing_model_session_and_usage_are_not_invented(controller):
    reply = transport("Lesson", model=None, conversation_id=None, usage=None)
    with patch("course_harness.cli_adapter.subprocess.run", return_value=reply):
        _, meta = controller.adapter.invoke("prompt", "worker", "M01-L01")
    assert meta["model_reported"] is None and meta["model_verified"] == "NOT_VERIFIED"
    assert meta["conversation_id"] is None and meta["usage"] is None
    assert meta["request_id"] is None and meta["response_id"] is None


def test_interrupted_agy_lesson_reuses_worker_evidence_without_new_worker(controller):
    with patch("course_harness.cli_adapter.subprocess.run", side_effect=[transport(DRAFT), KeyboardInterrupt]):
        with pytest.raises(KeyboardInterrupt):
            controller.process_lesson("M01-L01")
    checkpoint = controller.state_mgr.load_checkpoint("M01-L01")
    assert Path(checkpoint["worker_evidence_path"]).is_file()
    with patch("course_harness.cli_adapter.subprocess.run", return_value=transport(json.dumps(audit()), 3)) as invoke:
        result = controller.process_lesson("M01-L01")
    assert result["status"] == "PASS", result
    assert invoke.call_count == 1
    assert "INDEPENDENT AUDITOR" in invoke.call_args.args[0][2]


def test_raw_agy_json_is_preserved_before_validation(controller):
    with patch("course_harness.cli_adapter.subprocess.run", return_value=transport({"not": "text"})):
        with pytest.raises(CliExecutionError, match="must be text"):
            controller.adapter.invoke("prompt", "worker", "M01-L01")
    assert len(list(Path(controller.evidence_dir).glob("*.raw.json"))) == 1


@pytest.mark.parametrize("effort,fresh,error", [("low", True, ModelUnavailableError), ("high", False, CliExecutionError)])
def test_pin_effort_and_fresh_session(controller, effort, fresh, error):
    controller.adapter.effort = effort
    with patch("course_harness.cli_adapter.subprocess.run") as invoke:
        with pytest.raises(error):
            controller.adapter.invoke("prompt", "auditor", "M01-L01", fresh_session=fresh)
        invoke.assert_not_called()


def test_repeated_invocation_does_not_overwrite_evidence(controller):
    with patch("course_harness.cli_adapter.subprocess.run", return_value=transport("Lesson")) as invoke:
        controller.adapter.invoke("prompt", "worker", "M01-L01", invocation_id="same-invocation")
        original = {p: p.read_bytes() for p in Path(controller.evidence_dir).iterdir() if p.is_file()}
        with pytest.raises((FileExistsError, CliExecutionError)):
            controller.adapter.invoke("different", "worker", "M01-L01", invocation_id="same-invocation")
        assert invoke.call_count == 1
    assert all(p.read_bytes() == content for p, content in original.items())


def test_batch_dry_run_reports_policy_block_without_provider_calls(controller):
    scheduler = BatchScheduler(controller=controller)
    plan = scheduler.plan_batch(requested_ids=["M01-L01"])
    with patch("course_harness.cli_adapter.subprocess.run") as invoke:
        preview = scheduler.execute_batch(plan, dry_run=True)
        assert preview["provider_readiness"]["status"] == "POLICY_CLARIFICATION_REQUIRED"
        assert preview["provider_calls"] == 0 and preview["manual_steps"] == []
        with pytest.raises(BlockedExecutionError, match="POLICY_CLARIFICATION_REQUIRED"):
            scheduler.execute_batch(plan)
        invoke.assert_not_called()
    assert not list(Path(scheduler.batch_checkpoints_dir).glob("*.json"))


def test_five_prompt_direct_scripting_primitive_is_sequential(controller):
    """Documented CLI mechanics only; this does not enable the Course Harness batch wrapper."""
    replies = [transport(f"Response for lesson {index}", index) for index in range(1, 6)]
    with patch("course_harness.cli_adapter.subprocess.run", side_effect=replies) as invoke:
        metadata = []
        for index in range(1, 6):
            text, meta = controller.adapter.invoke(f"Source and prompt {index}", "worker", f"M01-L{index:02}")
            assert text == f"Response for lesson {index}"
            metadata.append(meta)
            assert invoke.call_count == index
    assert len({meta["conversation_id"] for meta in metadata}) == 5
    assert sum(meta["usage"]["total_tokens"] for meta in metadata) == 750
    assert len(list(Path(controller.evidence_dir).glob("*.raw.json"))) == 5
    assert not list(Path(controller.evidence_dir).glob("handoff*"))


def test_pilot_method_obeys_same_batch_policy_guard(controller):
    with patch("course_harness.cli_adapter.subprocess.run") as invoke:
        with pytest.raises(BlockedExecutionError, match="POLICY_CLARIFICATION_REQUIRED"):
            controller.run_pilot()
        invoke.assert_not_called()


@pytest.mark.parametrize("arguments", [["--batch"], ["--pilot"], ["--module", "M01"]])
def test_all_bulk_entrypoints_stop_before_verification(controller, arguments, capsys):
    with patch.object(sys, "argv", ["run", "--config", controller.config_path] + arguments), \
         patch("course_harness.cli_adapter.subprocess.run") as invoke:
        assert run_main() == 3
        invoke.assert_not_called()
    assert "POLICY_CLARIFICATION_REQUIRED" in capsys.readouterr().err


def test_readiness_never_constructs_controller_or_calls_provider(capsys):
    with patch("course_harness.batch.CourseHarnessController") as controller, \
         patch("course_harness.cli_adapter.subprocess.run") as invoke:
        assert batch_main(["--readiness"]) == 0
        controller.assert_not_called()
        invoke.assert_not_called()
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "POLICY_CLARIFICATION_REQUIRED"
    assert result["model_requested"] == MODEL and result["effort_requested"] == "high"


def test_api_config_cannot_become_active(tmp_path):
    with patch("course_harness.run.GeminiApiAdapter") as adapter:
        with pytest.raises(ApiDisabledError, match="NOT_AUTHORIZED"):
            CourseHarnessController("course_harness/gemini_api.yaml")
        adapter.assert_not_called()
    api = GeminiApiAdapter(tmp_path, "course_harness/schemas/audit.schema.json")
    with patch.dict("os.environ", {"GEMINI_API_KEY": "do-not-use-this"}), patch("google.genai.Client") as client:
        with pytest.raises(ApiDisabledError):
            api.invoke("prompt", "worker", "M01-L01")
        client.assert_not_called()
    assert provider_readiness(config_path="course_harness/gemini_api.yaml")["status"] == "PROVIDER_DISABLED"
