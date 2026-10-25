"""Offline native workflow simulation. Synthetic AGY returns are NOT live runtime evidence."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from unittest.mock import patch

import pytest
import yaml

from course_harness.native_tools import NativeTools, ToolError, main
from course_harness.visual import DEFINED_RUBRIC_2_0_DIMENSIONS, VisualAssetManager

REPO = Path(__file__).resolve().parents[2]
DRAFT = '# Bài học\n\n## Tình huống và hướng dẫn\n' + 'Nhóm kiểm tra công việc và phản hồi để cải thiện cách thực hiện. ' * 6
FIGURE = '''
<!-- FIGURE_START: F01 -->
#### Hình F01: Vòng phản hồi công việc
![Sơ đồ nhóm kiểm tra công việc và tiếp nhận phản hồi](assets/M01-L01/F01_wrong.svg)
<details>
<summary>Xem mã nguồn sơ đồ</summary>

```mermaid
flowchart LR
  A[Kiểm tra] --> B[Phản hồi]
```
</details>

*Hình F01: Nhóm kiểm tra công việc và ghi nhận phản hồi [00:01]*

**Giải thích trực quan:** Sơ đồ mô tả việc kiểm tra công việc trước khi nhóm ghi nhận phản hồi.
<!-- FIGURE_END: F01 -->
'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def call(tool, operation, **kwargs):
    return tool.execute({'operation': operation, 'course': tool.course, **kwargs})


@pytest.fixture
def tool(tmp_path):
    shutil.copytree(REPO / '.agents', tmp_path / '.agents')
    for name in ('schemas', 'prompts'):
        shutil.copytree(REPO / 'course_harness' / name, tmp_path / 'course_harness' / name)
    shutil.copy(REPO / 'course_harness/native_tools.py', tmp_path / 'course_harness/native_tools.py')
    source = tmp_path / 'output_course/TestCourse/Module_01_Practice'
    source.mkdir(parents=True)
    for n in range(1, 8):
        (source / f'{n:02d}_activity.md').write_text('# Activity: Team practice\nThe team inspects work and feedback. [00:01]')
    return NativeTools(tmp_path, 'TestCourse')


def start(tool, lessons=None, **kwargs):
    return call(tool, 'start-batch', **({'lessons': lessons} if lessons else {}), **kwargs)['batch_id']


def prepare(tool, batch, lesson='M01-L01'):
    return call(tool, 'prepare-lesson', batch=batch, lesson=lesson)


def record(tool, batch, prepared, output, runtime=None):
    packet = prepared['packet']
    artifact = tool.workspace / packet['artifact_output_path']
    artifact.write_text(output)
    payload = {'conversation_id': 'mock-' + packet['attempt_id'], 'model': 'gemini-3.8-flash-high',
               'invocation_id': 'mock-inv-' + packet['attempt_id'], 'usage': {'total_tokens': 150}, 'effort': 'high'}
    if runtime is not None:
        payload = runtime
    (tool.workspace / packet['runtime_evidence_output_path']).write_text(json.dumps(payload, indent=2) + '\n')
    return call(tool, 'record-attempt', batch=batch, lesson=packet['lesson_id'], attempt=packet['attempt_id'],
                artifact=packet['artifact_output_path'], runtime_evidence=packet['runtime_evidence_output_path'])


def draft(tool, batch, lesson='M01-L01', content=DRAFT):
    prepared = prepare(tool, batch, lesson)
    record(tool, batch, prepared, content)
    return call(tool, 'process-visuals', batch=batch, lesson=lesson)


def report(packet, verdict='PASS'):
    return {'lesson_id': packet['lesson_id'], 'verdict': verdict, 'summary': 'Independent source review',
            'quality_rubric_version': '2.0-visual-first', 'quality_score': 100 if verdict == 'PASS' else 75,
            'content_quality_accepted': verdict == 'PASS',
            'audited_final_sha256': packet['candidate']['sha256'], 'visual_figures_audited': 0,
            'dimension_scores': {d: 'FAILED' if verdict == 'FAIL' and d == 'SOURCE_FIDELITY' else 'MET'
                                 for d in DEFINED_RUBRIC_2_0_DIMENSIONS},
            'findings': [] if verdict == 'PASS' else [{'finding_id': 'F01', 'severity': 'HIGH', 'category': 'SOURCE_FIDELITY',
                'source_locator': 'source', 'draft_locator': 'lesson', 'description': 'Correct source fidelity',
                'required_action': 'Use the original meaning'}], 'limitations': ['Offline fixture, not actual AGY evidence']}


def audit(tool, batch, lesson='M01-L01', verdict='PASS', transform=None, runtime=None):
    prepared = prepare(tool, batch, lesson)
    payload = report(prepared['packet'], verdict)
    if transform:
        transform(payload)
    record(tool, batch, prepared, json.dumps(payload), runtime)
    return call(tool, 'validate-audit', batch=batch, lesson=lesson)


def test_agent_and_skill_definitions_match_supported_discovery_format():
    for role in ('producer', 'worker', 'auditor', 'repair'):
        p = REPO / '.agents/agents' / ('coursera-' + role) / 'agent.md'
        front, body = p.read_text().split('---', 2)[1:]
        meta = yaml.safe_load(front)
        assert meta['name'] == 'coursera-' + role
        assert meta['mainAgent'] is (role == 'producer')
        assert meta['subagent'] is (role != 'producer')
        assert meta['model'] == 'inherit'
        assert meta['skills'] == ['skills/coursera-harness']
        assert set(meta['tools']) <= {'view_file', 'run_command', 'invoke_subagent'}
        if role == 'auditor':
            assert meta['tools'] == ['view_file']
        assert body.strip()
    skill = REPO / '.agents/skills/coursera-harness/SKILL.md'
    assert yaml.safe_load(skill.read_text().split('---', 2)[1])['name'] == 'coursera-harness'
    for ref in ('workflow', 'quality-gates', 'evidence-contract', 'recovery-procedure'):
        assert (skill.parent / 'references' / (ref + '.md')).is_file()


def test_preflight_and_selection_are_read_only(tool):
    assert call(tool, 'preflight')['execution_boundary'] == 'AGY_NATIVE_ONLY'
    rows = call(tool, 'list-lessons', lessons=['M01-L03', 'M01-L01'])['lessons']
    assert [r['lesson_id'] for r in rows] == ['M01-L03', 'M01-L01']
    assert not tool.root.exists()
    with pytest.raises(ToolError, match='absent'):
        call(tool, 'list-lessons', lessons=['M99-L99'])


def test_worker_auditor_publication_automatic_contract(tool):
    with patch('subprocess.run', side_effect=AssertionError('No subprocess in nonvisual native workflow')):
        batch = start(tool, ['M01-L01'])
        draft_result = draft(tool, batch)
        assert draft_result['validation']['valid'] and draft_result['next_action'] == 'auditor'
        result = audit(tool, batch)
        assert result['validation']['production_eligible']
        published = call(tool, 'publish', batch=batch, lesson='M01-L01')
        chk = published['checkpoint']
        assert chk['status'] == 'PASS' and chk['final_sha256'] == sha(DRAFT.encode())
        assert published['quality']['human_acceptance'] == 'NOT_GRANTED'
        assert (tool.workspace / chk['publication_path'] / 'lesson.md').read_text() == DRAFT
        assert [a['role'] for a in chk['attempts']] == ['worker', 'auditor']
        assert call(tool, 'resume', batch=batch)['status'] == 'COMPLETED'
        assert call(tool, 'publish', batch=batch, lesson='M01-L01')['checkpoint']['status'] == 'PASS'


@pytest.mark.parametrize('verdicts,expected,repairs', [(['FAIL', 'PASS'], 'PASS', 1), (['FAIL'] * 3, 'NEEDS_HUMAN_REVIEW', 2)])
def test_repair_fresh_audit_and_limit(tool, verdicts, expected, repairs):
    batch = start(tool, ['M01-L01'])
    draft(tool, batch)
    for verdict in verdicts:
        result = audit(tool, batch, verdict=verdict)
        if result['next_action'] == 'repair':
            drafted = draft(tool, batch, content=DRAFT + '\nĐã đối chiếu lại nguồn.')
            assert drafted['next_action'] == 'auditor'
    chk = tool.checkpoint('M01-L01')
    assert chk['repair_rounds'] == repairs
    sessions = [a['provenance']['conversation_id'] for a in chk['attempts']]
    assert len(set(sessions)) == len(sessions)
    if expected == 'PASS':
        assert call(tool, 'publish', batch=batch, lesson='M01-L01')['checkpoint']['status'] == expected
    else:
        assert chk['status'] == expected
        assert prepare(tool, batch)['next_action'] == 'done'


def test_auditor_packet_excludes_worker_reasoning_and_prior_verdict(tool):
    batch = start(tool)
    draft(tool, batch)
    packet = prepare(tool, batch)['packet']
    assert packet['role'] == 'auditor' and packet['fresh_context_required'] and packet['read_only_candidate']
    assert packet['candidate']['sha256'] == sha(DRAFT.encode())
    assert not {'provenance', 'worker_reasoning', 'history', 'prior_verdict', 'attempts'} & packet.keys()


@pytest.mark.parametrize('runtime', [{}, {'conversation_id': 'same-context'}])
@pytest.mark.parametrize('verdict', ['PASS', 'FAIL'])
def test_missing_or_reused_context_never_publishes(tool, runtime, verdict):
    batch = start(tool)
    prepared = prepare(tool, batch)
    record(tool, batch, prepared, DRAFT, runtime)
    call(tool, 'process-visuals', batch=batch, lesson='M01-L01')
    result = audit(tool, batch, runtime=runtime, verdict=verdict)
    assert result['validation']['independent_context'] == 'NOT_VERIFIED'
    assert result['next_action'] == 'done'
    assert tool.checkpoint('M01-L01')['status'] == 'NEEDS_HUMAN_REVIEW'
    with pytest.raises(ToolError):
        call(tool, 'publish', batch=batch, lesson='M01-L01')


def test_audit_exact_hash_mismatch_halts_batch(tool):
    batch = start(tool)
    draft(tool, batch)
    with pytest.raises(ToolError) as error:
        audit(tool, batch, transform=lambda a: a.update(audited_final_sha256='0' * 64))
    assert error.value.code == 'AUDIT_HASH_MISMATCH' and error.value.fatal
    assert tool.batch(batch)['status'] == 'HALTED'
    assert not (tool.root / 'publications').exists()


def test_missing_audit_hash_is_saved_and_halts_without_repair(tool):
    batch = start(tool)
    draft(tool, batch)
    prepared = prepare(tool, batch)
    payload = report(prepared['packet'])
    payload.pop('audited_final_sha256')
    record(tool, batch, prepared, json.dumps(payload))
    with pytest.raises(ToolError):
        call(tool, 'validate-audit', batch=batch, lesson='M01-L01')
    assert len(list(tool.root.rglob('runtime.raw.json'))) == 2
    # A wrong/missing candidate hash is integrity-critical, so the batch stays halted.
    assert tool.batch(batch)['status'] == 'HALTED'


def test_schema_rejects_manufactured_pass_and_preserves_evidence(tool):
    batch = start(tool)
    draft(tool, batch)
    with pytest.raises(ValueError):
        audit(tool, batch, transform=lambda a: a.update(dimension_scores={'SOURCE_FIDELITY': 'MET'}))
    assert tool.checkpoint('M01-L01')['repair_rounds'] == 0
    assert len(list(tool.root.rglob('response.raw'))) == 2
    assert not (tool.root / 'publications').exists()


def test_missing_usage_and_model_stay_unverified(tool):
    batch = start(tool)
    prepared = prepare(tool, batch)
    result = record(tool, batch, prepared, DRAFT, {'conversation_id': 'actual-field-in-synthetic-fixture'})
    assert result['checkpoint']['attempts'][0]['provenance']['model'] == 'NOT_VERIFIED'
    usage = call(tool, 'report-batch', batch=batch)
    assert usage['known_total_tokens'] == 0 and usage['unreported_usage_attempts'] == 1
    assert usage['monetary_cost'] == 'NOT_VERIFIED'


def test_resume_does_not_repeat_worker_or_auditor(tool):
    batch = start(tool, ['M01-L01'])
    prepared = prepare(tool, batch)
    assert prepare(tool, batch)['packet']['attempt_id'] == prepared['packet']['attempt_id']
    record(tool, batch, prepared, DRAFT)
    tool = NativeTools(tool.workspace, tool.course)
    assert call(tool, 'resume', batch=batch)['lessons'][0]['next_action'] == 'process-visuals'
    call(tool, 'process-visuals', batch=batch, lesson='M01-L01')
    prepared = prepare(tool, batch)
    record(tool, batch, prepared, json.dumps(report(prepared['packet'])))
    tool = NativeTools(tool.workspace, tool.course)
    assert call(tool, 'resume', batch=batch)['lessons'][0]['next_action'] == 'validate-audit'
    call(tool, 'validate-audit', batch=batch, lesson='M01-L01')
    call(tool, 'publish', batch=batch, lesson='M01-L01')
    assert len(tool.checkpoint('M01-L01')['attempts']) == 2


def test_five_lesson_sequential_workflow_and_skip_verified(tool):
    batch = start(tool, mode='bounded')
    selected = call(tool, 'report-batch', batch=batch)['lessons']
    assert len(selected) == 5
    for row in selected:
        lesson = row['lesson_id']
        draft(tool, batch, lesson)
        audit(tool, batch, lesson)
        call(tool, 'publish', batch=batch, lesson=lesson)
    result = call(tool, 'resume', batch=batch)
    assert result['status'] == 'COMPLETED'
    assert all(row['status'] == 'PASS' for row in result['lessons'])
    assert result['known_total_tokens'] == 1500 and result['dispatches'] == 10
    assert len(list((tool.root / 'checkpoints').glob('M*.json'))) == 5
    assert not list(tool.root.rglob('*handoff*'))
    next_batch = start(tool)
    assert [r['lesson_id'] for r in call(tool, 'report-batch', batch=next_batch)['lessons']] == ['M01-L06', 'M01-L07']


def test_human_accepted_legacy_never_overwritten(tool):
    checkpoint = tool.output / 'evidence/checkpoints/M01-L01.json'
    checkpoint.parent.mkdir(parents=True)
    final = tool.output / 'modules/accepted.md'
    final.parent.mkdir(parents=True)
    final.write_text('Human-approved immutable lesson')
    chk = {'status': 'HUMAN_ACCEPTED', 'final_path': tool.ref(final), 'final_sha256': sha(final.read_bytes())}
    checkpoint.write_text(json.dumps(chk))
    before = {p: p.read_bytes() for p in (checkpoint, final)}
    batch = start(tool, ['M01-L01', 'M01-L02'])
    assert call(tool, 'report-batch', batch=batch)['lessons'][0]['lesson_id'] == 'M01-L02'
    with pytest.raises(ToolError):
        prepare(tool, batch, 'M01-L01')
    assert all(p.read_bytes() == data for p, data in before.items())


def test_source_checksum_mismatch_and_path_escape(tool):
    batch = start(tool)
    prepare(tool, batch)
    (tool.source_root / 'Module_01_Practice/01_activity.md').write_text('mutated')
    with pytest.raises(ToolError) as error:
        call(tool, 'resume', batch=batch)
    assert error.value.code == 'SOURCE_CHECKSUM_MISMATCH'
    assert tool.batch(batch)['status'] == 'HALTED'
    with pytest.raises(ToolError, match='escapes'):
        tool.path(tool.source_root / 'Module_01_Practice/01_activity.md')


def render(self, mmd_path, svg_path):
    Path(svg_path).write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>Kiểm tra và phản hồi</text></svg>')
    return True, 'RENDER_VERIFIED', sha(Path(svg_path).read_bytes())


def test_visual_binding_normalization_publication_and_pending_review(tool):
    batch = start(tool)
    with patch.object(VisualAssetManager, 'is_renderer_available', return_value=True), patch.object(VisualAssetManager, '_render_mermaid_file', render):
        result = draft(tool, batch, content=DRAFT + FIGURE)
    assert result['validation']['valid'], result
    assert result['validation']['human_visual_review'] == 'PENDING'
    prepared = prepare(tool, batch)
    packet = prepared['packet']
    text = (tool.workspace / packet['candidate']['path']).read_text()
    assert 'F01_wrong.svg' not in text
    payload = report(packet)
    payload.update(visual_figures_audited=1, visual_manifest_sha256=packet['visual_manifest']['sha256'])
    record(tool, batch, prepared, json.dumps(payload))
    call(tool, 'validate-audit', batch=batch, lesson='M01-L01')
    published = call(tool, 'publish', batch=batch, lesson='M01-L01')
    assert published['quality']['human_visual_review'] == 'PENDING'
    vm = tool.load(result['visual_manifest']['path'])
    asset = vm['figures'][0]['rendered_asset_path']
    assert (tool.workspace / published['checkpoint']['publication_path'] / asset).is_file()
    assert call(tool, 'resume', batch=batch)['lessons'][0]['status'] == 'PASS'


def test_invalid_svg_blocks_before_auditor(tool):
    def corrupt(self, mmd, svg):
        Path(svg).write_text('<svg><broken')
        return True, 'RENDER_VERIFIED', sha(Path(svg).read_bytes())
    batch = start(tool)
    with patch.object(VisualAssetManager, 'is_renderer_available', return_value=True), patch.object(VisualAssetManager, '_render_mermaid_file', corrupt):
        result = draft(tool, batch, content=DRAFT + FIGURE)
    assert not result['validation']['valid']
    assert tool.checkpoint('M01-L01')['status'] == 'BLOCKED'
    assert prepare(tool, batch)['next_action'] == 'done'
    assert len(tool.checkpoint('M01-L01')['attempts']) == 1


@pytest.mark.parametrize('image', ['![instructor portrait](innocent.svg)', '<img src="https://example.com/portrait.png">'])
def test_instructor_and_external_images_block(tool, image):
    batch = start(tool)
    result = draft(tool, batch, content=DRAFT + '\n' + image)
    assert not result['validation']['valid'] and tool.checkpoint('M01-L01')['status'] == 'BLOCKED'


def test_nonfatal_blocked_lesson_continues_and_concurrency_is_one(tool):
    batch = start(tool)
    prepare(tool, batch)
    with pytest.raises(ToolError) as error:
        prepare(tool, batch, 'M01-L02')
    assert error.value.code == 'CONCURRENCY_LIMIT'
    record(tool, batch, prepare(tool, batch), 'too short')
    call(tool, 'process-visuals', batch=batch, lesson='M01-L01')
    assert prepare(tool, batch, 'M01-L02')['packet']['role'] == 'worker'


def test_transient_retries_are_bounded_and_not_educational_repairs(tool):
    batch = start(tool)
    for _ in range(3):
        prepare(tool, batch)
        result = call(tool, 'record-failure', batch=batch, lesson='M01-L01', category='transient', diagnostic='Native timeout')
        assert result['checkpoint']['repair_rounds'] == 0
    assert result['checkpoint']['status'] == 'BLOCKED'
    assert len(list((tool.root / 'diagnostics').rglob('*.json'))) == 3


@pytest.mark.parametrize('category', ['authentication', 'budget', 'integrity'])
def test_critical_failure_halts_batch(tool, category):
    batch = start(tool)
    prepare(tool, batch)
    result = call(tool, 'record-failure', batch=batch, lesson='M01-L01', category=category, diagnostic='Actual reported native failure')
    assert result['fatal'] and tool.batch(batch)['status'] == 'HALTED'
    with pytest.raises(ToolError) as error:
        prepare(tool, batch, 'M01-L02')
    assert error.value.code == 'BATCH_HALTED'


def test_budget_boundary_no_new_dispatch_and_no_lost_result(tool):
    batch = start(tool, mode='bounded')
    prepared = prepare(tool, batch)
    state = tool.batch(batch)
    state['max_dispatches'] = 1
    tool.save_batch(state)
    record(tool, batch, prepared, DRAFT)
    call(tool, 'process-visuals', batch=batch, lesson='M01-L01')
    with pytest.raises(ToolError) as error:
        prepare(tool, batch)
    assert error.value.code == 'SAFE_BOUNDARY_LIMIT'
    assert len(tool.checkpoint('M01-L01')['attempts']) == 1


def test_raw_evidence_tamper_and_publication_tamper_fail_resume(tool):
    batch = start(tool)
    draft(tool, batch)
    audit(tool, batch)
    chk = call(tool, 'publish', batch=batch, lesson='M01-L01')['checkpoint']
    report_path = tool.workspace / chk['publication_path'] / 'quality-report.json'
    report_path.write_text('{}')
    with pytest.raises(ToolError) as error:
        call(tool, 'resume', batch=batch)
    assert error.value.code == 'PUBLICATION_INTEGRITY'


def test_cli_machine_readable_errors(tool, monkeypatch, capsys):
    monkeypatch.chdir(tool.workspace)
    assert main(['preflight', '--course', 'TestCourse']) == 0
    assert json.loads(capsys.readouterr().out)['ok']
    assert main(['publish', '--course', 'TestCourse']) == 2
    error = json.loads(capsys.readouterr().out)
    assert error['error']['code'] == 'SCHEMA_INVALID'
    assert main(['--imaginary']) == 2
    assert json.loads(capsys.readouterr().out)['error']['code'] == 'INVALID_ARGUMENTS'


def test_native_import_and_execution_do_not_load_any_provider(tool):
    code = '''
import sys, importlib.abc
class BlockProviders(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in ('course_harness.cli_adapter','course_harness.gemini_adapter','course_harness.run','course_harness.batch') or fullname == 'google' or fullname.startswith('google.'):
            raise AssertionError('Provider import forbidden: ' + fullname)
sys.meta_path.insert(0, BlockProviders())
from course_harness.native_tools import NativeTools
from pathlib import Path
print(NativeTools(Path(sys.argv[1]), 'TestCourse').execute({'operation':'preflight','course':'TestCourse'})['execution_boundary'])
'''
    result = subprocess.run([sys.executable, '-c', code, str(tool.workspace)], cwd=REPO, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == 'AGY_NATIVE_ONLY'


def test_record_is_idempotent_and_original_raw_bytes_cannot_change(tool):
    batch = start(tool)
    prepared = prepare(tool, batch)
    result = record(tool, batch, prepared, DRAFT)
    attempt = result['checkpoint']['attempts'][0]
    request = {'batch': batch, 'lesson': 'M01-L01', 'attempt': attempt['attempt_id'],
               'artifact': prepared['packet']['artifact_output_path'],
               'runtime_evidence': prepared['packet']['runtime_evidence_output_path']}
    assert call(tool, 'record-attempt', **request)['checkpoint']['attempts'][0] == attempt
    raw = tool.path(attempt['artifact']['path'])
    before = raw.read_bytes()
    tool.path(request['artifact']).write_text('Changed artifact')
    with pytest.raises(ToolError) as error:
        call(tool, 'record-attempt', **request)
    assert error.value.code == 'EVIDENCE_COLLISION'
    assert raw.read_bytes() == before


def test_atomic_checkpoint_interruption_keeps_prior_state_and_raw_evidence(tool):
    batch = start(tool)
    prepared = prepare(tool, batch)
    checkpoint = tool.root / 'checkpoints/M01-L01.json'
    before = checkpoint.read_bytes()
    with patch('course_harness.state.os.replace', side_effect=OSError('simulated interrupted checkpoint write')):
        with pytest.raises(OSError):
            record(tool, batch, prepared, DRAFT)
    assert checkpoint.read_bytes() == before
    assert list(tool.root.rglob('response.raw'))
    result = record(tool, batch, prepared, DRAFT)
    assert result['next_action'] == 'process-visuals'
    assert len(result['checkpoint']['attempts']) == 1


def test_raw_runtime_tamper_is_integrity_failure_on_resume(tool):
    batch = start(tool)
    prepared = prepare(tool, batch)
    result = record(tool, batch, prepared, DRAFT)
    tool.path(result['checkpoint']['attempts'][0]['runtime']['path']).write_text('{}')
    with pytest.raises(ToolError) as error:
        call(tool, 'resume', batch=batch)
    assert error.value.code == 'EVIDENCE_INTEGRITY'
    assert tool.batch(batch)['status'] == 'HALTED'


def test_source_mutation_after_pass_audit_blocks_publication(tool):
    batch = start(tool)
    draft(tool, batch)
    audit(tool, batch)
    source = tool.source_root / 'Module_01_Practice/01_activity.md'
    source.write_text('Changed original source')
    with pytest.raises(ToolError) as error:
        call(tool, 'publish', batch=batch, lesson='M01-L01')
    assert error.value.code == 'SOURCE_CHECKSUM_MISMATCH'
    assert not (tool.root / 'publications').exists()


@pytest.mark.parametrize('metadata,code', [({'model': 'other-model'}, 'MODEL_MISMATCH'), ({'effort': 'low'}, 'EFFORT_MISMATCH')])
def test_wrong_model_or_effort_records_raw_but_halts(tool, metadata, code):
    batch = start(tool)
    prepared = prepare(tool, batch)
    with pytest.raises(ToolError) as error:
        record(tool, batch, prepared, DRAFT, {**metadata, 'conversation_id': 'mock-context'})
    assert error.value.code == code
    assert list(tool.root.rglob('runtime.raw.json'))
    assert tool.batch(batch)['status'] == 'HALTED'


def test_noncanonical_rubric_and_low_score_are_not_publishable(tool):
    batch = start(tool)
    draft(tool, batch)
    with pytest.raises(ToolError) as error:
        audit(tool, batch, transform=lambda a: a.update(quality_score=80))
    assert error.value.code == 'AUDIT_SCHEMA_INVALID'
    assert tool.checkpoint('M01-L01')['repair_rounds'] == 0
    call(tool, 'record-failure', batch=batch, lesson='M01-L01', category='transient', diagnostic='Actual invalid native audit response')
    prepared = prepare(tool, batch)
    assert prepared['packet']['role'] == 'auditor'
    assert 'verified_findings_path' not in prepared['packet']
    assert tool.checkpoint('M01-L01')['repair_rounds'] == 0


def test_asset_hash_tamper_blocks_resume_and_publication(tool):
    batch = start(tool)
    with patch.object(VisualAssetManager, 'is_renderer_available', return_value=True), patch.object(VisualAssetManager, '_render_mermaid_file', render):
        result = draft(tool, batch, content=DRAFT + FIGURE)
    chk = tool.checkpoint('M01-L01')
    candidate = tool.latest_candidate(chk)
    vm = tool.load(result['visual_manifest']['path'])
    (tool.path(candidate['candidate_root']) / vm['figures'][0]['rendered_asset_path']).write_text('<svg/>')
    with pytest.raises(ToolError) as error:
        prepare(tool, batch)
    # Preparing an Auditor must not accept assets modified after visual processing.
    assert error.value.code in ('DRAFT_BLOCKED', 'EVIDENCE_INTEGRITY')


def test_unknown_and_locked_lesson_selection_is_explicit(tool):
    tool.manifest['lessons']['M01-L02']['status'] = 'LOCKED'
    tool.manifest['lessons']['M01-L03']['status'] = 'INCOMPLETE'
    batch = start(tool, ['M01-L02', 'M01-L03'])
    assert [r['lesson_id'] for r in call(tool, 'report-batch', batch=batch)['lessons']] == ['M01-L03']
    assert prepare(tool, batch, 'M01-L03')['packet']['source_status'] == 'INCOMPLETE'
    record(tool, batch, prepare(tool, batch, 'M01-L03'), DRAFT)
    result = call(tool, 'process-visuals', batch=batch, lesson='M01-L03')
    assert not result['validation']['valid']
    assert any('INCOMPLETE' in issue for issue in result['validation']['blocking'])


@pytest.mark.parametrize('output', ['not JSON', '[]', 'null', '{"findings": "invalid"}'])
def test_malformed_native_audit_is_machine_error_without_educational_repair(tool, output):
    batch = start(tool)
    draft(tool, batch)
    record(tool, batch, prepare(tool, batch), output)
    with pytest.raises(ToolError) as error:
        call(tool, 'validate-audit', batch=batch, lesson='M01-L01')
    assert error.value.code in ('AUDIT_JSON_INVALID', 'AUDIT_SCHEMA_INVALID')
    assert tool.checkpoint('M01-L01')['repair_rounds'] == 0
    assert len(list(tool.root.rglob('response.raw'))) == 2


def test_missing_native_response_is_nonfatal_and_raw_invalid_runtime_is_preserved(tool):
    batch = start(tool)
    prepared = prepare(tool, batch)
    packet = prepared['packet']
    kwargs = {'batch': batch, 'lesson': 'M01-L01', 'attempt': packet['attempt_id'],
              'artifact': packet['artifact_output_path'], 'runtime_evidence': packet['runtime_evidence_output_path']}
    with pytest.raises(ToolError) as error:
        call(tool, 'record-attempt', **kwargs)
    assert error.value.code == 'MISSING_NATIVE_RESPONSE' and not error.value.fatal
    tool.path(packet['artifact_output_path']).write_text(DRAFT)
    tool.path(packet['runtime_evidence_output_path']).write_text('invalid runtime return\n')
    with pytest.raises(ToolError) as error:
        call(tool, 'record-attempt', **kwargs)
    assert error.value.code == 'INVALID_RUNTIME_RETURN'
    assert list(tool.root.rglob('runtime.raw.json'))[0].read_text() == 'invalid runtime return\n'
