"""Continuous AGY scheduling, simulated offline. No live inference or provider calls."""

import json
from unittest.mock import patch

import pytest

from course_harness.native_tools import NativeTools, ToolError
from course_harness.tests.test_native_tools import (
    DRAFT, audit, call, draft, prepare, record, sha, start, tool,
)


def complete(t, batch, lesson):
    draft(t, batch, lesson)
    audit(t, batch, lesson)
    call(t, 'publish', batch=batch, lesson=lesson)


def add_lessons(t, count):
    for n in range(8, count + 1):
        (t.source_root / 'Module_01_Practice' / f'{n:02d}_activity.md').write_text(
            '# Activity: Team practice\nThe team inspects work and feedback. [00:01]')
    return NativeTools(t.workspace, t.course)


def test_continuous_ignores_old_time_call_and_token_bounds(tool):
    batch = start(tool, ['M01-L01'])
    state = tool.batch(batch)
    assert state['mode'] == 'continuous'
    assert all(state[k] is None for k in ('max_runtime_seconds', 'max_dispatches', 'max_known_tokens'))
    state['dispatches'] = 40
    tool.save_batch(state)
    with patch('course_harness.native_tools.time.time', return_value=state['started_epoch'] + 86400 * 10):
        prepared = prepare(tool, batch)
        record(tool, batch, prepared, DRAFT, {
            'conversation_id': 'mock-long-worker', 'usage': {'total_tokens': 600000}})
        call(tool, 'process-visuals', batch=batch, lesson='M01-L01')
        assert prepare(tool, batch)['packet']['role'] == 'auditor'
    result = call(tool, 'report-batch', batch=batch)
    assert result['known_total_tokens'] == 600000
    assert result['monetary_cost'] == 'NOT_VERIFIED'
    assert result['dispatches'] == 42


def test_three_groups_run_without_manual_continuation_and_keep_failures(tool):
    tool = add_lessons(tool, 12)
    root_batch = batch = start(tool)
    groups = []
    with patch('subprocess.run', side_effect=AssertionError('No provider subprocess')):
        while True:
            progress = call(tool, 'report-batch', batch=batch)
            lesson = progress['next_lesson']
            if lesson:
                if lesson == 'M01-L02':
                    draft(tool, batch, lesson, 'Invalid short draft')
                elif lesson == 'M01-L06':
                    for _ in range(3):
                        prepare(tool, batch, lesson)
                        call(tool, 'record-failure', batch=batch, lesson=lesson,
                             category='transient', diagnostic='Mock native timeout')
                else:
                    draft(tool, batch, lesson)
                    if lesson == 'M01-L07':
                        assert audit(tool, batch, lesson, verdict='FAIL')['next_action'] == 'repair'
                        draft(tool, batch, lesson, DRAFT + '\nĐã đối chiếu lại nguồn.')
                    audit(tool, batch, lesson)
                    call(tool, 'publish', batch=batch, lesson=lesson)
            elif progress['next_action'] == 'advance-batch':
                groups.append(progress)
                progress = call(tool, 'advance-batch', batch=batch)
                batch = progress['batch_id']
                tool = NativeTools(tool.workspace, tool.course)  # Reconstruct after native context compaction.
            else:
                groups.append(progress)
                break
    assert [len(g['lessons']) for g in groups] == [5, 5, 2]
    assert progress['scope_status'] == 'COMPLETED_WITH_FAILURES'
    assert progress['next_action'] == 'done'
    assert progress['scope_summary'] == {'PASS': 10, 'BLOCKED': 2}
    assert len(list((tool.root / 'batches').glob('batch-*.json'))) == 3
    assert len(list((tool.root / 'reports').rglob('completed.json'))) == 2
    assert len(tool.checkpoint('M01-L02')['attempts']) == 1
    assert tool.checkpoint('M01-L06')['repair_rounds'] == 0
    assert tool.checkpoint('M01-L07')['repair_rounds'] == 1
    recovered = call(NativeTools(tool.workspace, tool.course), 'resume', batch=root_batch)
    assert recovered['batch_id'] == batch and recovered['next_action'] == 'done'
    assert recovered['scope_summary'] == progress['scope_summary']
    assert not list(tool.root.rglob('*handoff*'))


def test_scope_is_explicit_and_group_size_is_not_scope_limit(tool):
    scope = ['M01-L02', 'M01-L04', 'M01-L07']
    batch = start(tool, scope, limit=2)
    for lesson in scope[:2]:
        complete(tool, batch, lesson)
    progress = call(tool, 'report-batch', batch=batch)
    assert progress['next_action'] == 'advance-batch'
    second = call(tool, 'advance-batch', batch=batch)
    assert second['scope'] == scope
    assert [r['lesson_id'] for r in second['lessons']] == scope[2:]
    complete(tool, second['batch_id'], scope[2])
    end = call(tool, 'resume', batch=batch)
    assert end['scope_status'] == 'COMPLETED' and end['next_action'] == 'done'
    assert tool.checkpoint('M01-L01') is None
    assert len(list((tool.root / 'batches').glob('*.json'))) == 2


@pytest.mark.parametrize('crash_site', ['successor_pointer', 'parent_link'])
def test_successor_creation_interruption_is_idempotent(tool, crash_site):
    batch = start(tool, limit=1)
    complete(tool, batch, 'M01-L01')
    before = (tool.root / 'checkpoints/M01-L01.json').read_bytes()
    original_save = tool.save_batch
    from course_harness.native_tools import atomic_json

    def save(value):
        if crash_site == 'parent_link' and value['batch_id'] == batch and value.get('next_batch_id'):
            raise OSError('Crash while linking successor')
        original_save(value)

    def write(path, value):
        if crash_site == 'successor_pointer' and path.name == 'active_batch.json':
            raise OSError('Crash after successor was created')
        atomic_json(path, value)

    with patch.object(tool, 'save_batch', side_effect=save), patch('course_harness.native_tools.atomic_json', side_effect=write):
        with pytest.raises(OSError):
            call(tool, 'advance-batch', batch=batch)
    recovered = call(NativeTools(tool.workspace, tool.course), 'resume', batch=batch)
    again = call(tool, 'advance-batch', batch=batch)
    assert recovered['batch_id'] == again['batch_id'] != batch
    assert recovered['next_lesson'] == 'M01-L02'
    assert len(list((tool.root / 'batches').glob('*.json'))) == 2
    assert before == (tool.root / 'checkpoints/M01-L01.json').read_bytes()
    assert not tool.checkpoint('M01-L02')


def test_actual_runtime_pause_keeps_inflight_and_resume_never_redrafts(tool):
    batch = start(tool)
    prepared = prepare(tool, batch)
    before = (tool.root / 'checkpoints/M01-L01.json').read_bytes()
    suspended = call(tool, 'suspend', batch=batch, category='runtime', diagnostic='Actual runtime quota exhausted')
    assert suspended['status'] == 'PAUSED' and suspended['next_action'] == 'stop'
    assert before == (tool.root / 'checkpoints/M01-L01.json').read_bytes()
    with pytest.raises(ToolError) as error:
        prepare(tool, batch)
    assert error.value.code == 'BATCH_HALTED'
    # An already completed native invocation can still be recorded after runtime suspension.
    record(tool, batch, prepared, DRAFT)
    result = call(NativeTools(tool.workspace, tool.course), 'resume', batch=batch)
    assert result['status'] == 'ACTIVE' and result['lessons'][0]['next_action'] == 'process-visuals'
    assert len(tool.checkpoint('M01-L01')['attempts']) == 1
    call(tool, 'process-visuals', batch=batch, lesson='M01-L01')
    assert prepare(tool, batch)['packet']['role'] == 'auditor'


def test_unfinished_native_invocation_recovers_after_runtime_pause(tool):
    batch = start(tool)
    original = prepare(tool, batch)
    call(tool, 'suspend', batch=batch, category='runtime', diagnostic='Native session interrupted')
    call(tool, 'resume', batch=batch)
    recovered = prepare(tool, batch)
    assert recovered['next_action'] == 'recover_existing_native_invocation'
    assert recovered['packet']['attempt_id'] == original['packet']['attempt_id']
    assert tool.batch(batch)['dispatches'] == 1


@pytest.mark.parametrize('pause_first', [False, True])
def test_user_cancel_never_auto_restarts(tool, pause_first):
    batch = start(tool)
    prepared = prepare(tool, batch)
    if pause_first:
        call(tool, 'suspend', batch=batch, category='runtime', diagnostic='Actual quota exhaustion')
    call(tool, 'suspend', batch=batch, category='cancelled', diagnostic='User explicitly cancelled')
    result = call(tool, 'resume', batch=batch)
    assert result['status'] == 'CANCELLED' and result['next_action'] == 'stop'
    assert tool.checkpoint('M01-L01')['active_attempt'] == prepared['packet']['attempt_id']
    with pytest.raises(ToolError):
        prepare(tool, batch)
    with pytest.raises(ToolError) as error:
        start(tool)
    assert error.value.code == 'BATCH_ACTIVE'


def test_bounded_mode_retains_its_timer_and_does_not_advance(tool):
    batch = start(tool, mode='bounded')
    state = tool.batch(batch)
    with patch('course_harness.native_tools.time.time', return_value=state['started_epoch'] + 1801):
        with pytest.raises(ToolError) as error:
            prepare(tool, batch)
    assert error.value.code == 'SAFE_BOUNDARY_LIMIT'
    with pytest.raises(ToolError) as error:
        call(tool, 'advance-batch', batch=batch)
    assert error.value.code == 'BOUNDED_SCOPE'
    assert not list((tool.root / 'attempts').glob('**/packet.json'))


def test_continuous_skips_human_accepted_and_unavailable_sources(tool):
    final = tool.output / 'modules/approved.md'
    final.parent.mkdir(parents=True)
    final.write_text('Approved lesson, do not replace')
    acceptance = tool.output / 'evidence/checkpoints/M01-L02.json'
    acceptance.parent.mkdir(parents=True)
    acceptance.write_text(json.dumps({'status': 'HUMAN_ACCEPTED', 'final_path': tool.ref(final),
                                      'final_sha256': sha(final.read_bytes())}))
    before = {p: p.read_bytes() for p in (final, acceptance)}
    tool.manifest['lessons']['M01-L03']['status'] = 'LOCKED'
    tool.manifest_sha = sha(json.dumps(tool.manifest, sort_keys=True, ensure_ascii=False).encode())
    first = start(tool, limit=2)
    assert tool.batch(first)['lessons'] == ['M01-L01', 'M01-L04']
    for lesson in tool.batch(first)['lessons']:
        complete(tool, first, lesson)
    second = call(tool, 'advance-batch', batch=first)
    assert [r['lesson_id'] for r in second['lessons']] == ['M01-L05', 'M01-L06']
    assert all(p.read_bytes() == data for p, data in before.items())
    assert tool.checkpoint('M01-L02') is None and tool.checkpoint('M01-L03') is None


def test_integrity_failure_before_next_group_halts_and_cannot_resume(tool):
    batch = start(tool, limit=1)
    complete(tool, batch, 'M01-L01')
    (tool.source_root / 'Module_01_Practice/02_activity.md').write_text('Changed source')
    with pytest.raises(ToolError) as error:
        call(tool, 'advance-batch', batch=batch)
    assert error.value.code == 'SOURCE_CHECKSUM_MISMATCH' and error.value.fatal
    assert tool.batch(batch)['status'] == 'HALTED'
    resumed = call(tool, 'resume', batch=batch)
    assert resumed['status'] == 'HALTED' and resumed['next_action'] == 'stop'
    assert len(list((tool.root / 'batches').glob('*.json'))) == 1
    assert tool.checkpoint('M01-L02') is None


def legacy_snapshot(tool, monkeypatch):
    """Simulate a reviewed pre-upgrade state; nothing here is live AGY evidence."""
    batch = start(tool)
    for lesson in ('M01-L01', 'M01-L02'):
        complete(tool, batch, lesson)
    draft(tool, batch, 'M01-L03')
    state = tool.batch(batch)
    for field in ('mode', 'scope', 'batch_size'):
        state.pop(field)
    state.update(max_runtime_seconds=1800, max_dispatches=40, max_known_tokens=500000)
    tool.save_batch(state)
    snapshot = {'course_id': tool.course, 'batch_id': batch, 'policy_sha256': tool.policy_sha,
                'manifest_sha256': tool.manifest_sha,
                'files': {tool.ref(p): sha(p.read_bytes()) for p in tool.root.rglob('*')
                          if p.is_file() and p.name != '.lock'}}
    path = tool.workspace / 'course_harness/evidence/continuous_execution/upgrade-snapshot.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(snapshot, indent=2))
    monkeypatch.setattr('course_harness.native_tools.UPGRADE_SNAPSHOT_SHA256', sha(path.read_bytes()))
    agent = tool.workspace / '.agents/agents/coursera-producer/agent.md'
    agent.write_text(agent.read_text() + '\nReviewed continuous scheduling change\n')
    return NativeTools(tool.workspace, tool.course), batch, path


def test_reviewed_upgrade_preserves_pass_bytes_and_resumes_existing_draft(tool, monkeypatch):
    tool, batch, _ = legacy_snapshot(tool, monkeypatch)
    passed = {p: p.read_bytes() for p in (tool.root / 'checkpoints').glob('M01-L0[12].json')}
    with pytest.raises(ToolError) as error:
        tool.batch(batch)
    assert error.value.code == 'BATCH_INTEGRITY'
    upgraded = call(tool, 'upgrade-continuous', batch=batch)
    assert upgraded['mode'] == 'continuous' and upgraded['next_lesson'] == 'M01-L03'
    assert len(upgraded['scope']) == 7
    assert all(p.read_bytes() == data for p, data in passed.items())
    assert call(tool, 'upgrade-continuous', batch=batch)['next_lesson'] == 'M01-L03'
    prepared = prepare(tool, batch, 'M01-L03')
    assert prepared['packet']['role'] == 'auditor'
    chk = tool.checkpoint('M01-L03')
    assert [a['role'] for a in chk['attempts']] == ['worker', 'auditor']
    assert chk['policy_sha256'] == tool.policy_sha
    assert len(list((tool.root / 'migrations/continuous-v1').glob('M*.json'))) == 3
    assert all(p.read_bytes() == data for p, data in passed.items())


@pytest.mark.parametrize('tamper', ['snapshot', 'checkpoint', 'raw', 'halted'])
def test_upgrade_rejects_unreviewed_or_changed_evidence(tool, monkeypatch, tamper):
    tool, batch, snapshot = legacy_snapshot(tool, monkeypatch)
    if tamper == 'snapshot':
        snapshot.write_text(snapshot.read_text() + '\n')
    elif tamper == 'checkpoint':
        p = tool.root / 'checkpoints/M01-L01.json'
        p.write_text(p.read_text() + '\n')
    elif tamper == 'raw':
        next(tool.root.rglob('response.raw')).write_text('Changed historical evidence')
    else:
        state = tool.load(tool.root / 'batches' / (batch + '.json'))
        state['status'] = 'HALTED'
        tool.save_batch(state)
    with pytest.raises(ToolError) as error:
        call(tool, 'upgrade-continuous', batch=batch)
    assert error.value.fatal and error.value.code == 'UPGRADE_INTEGRITY'
    assert not (tool.root / 'migrations/continuous-v1/receipt.json').exists()
