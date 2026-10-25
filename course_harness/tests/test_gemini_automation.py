"""Exercise the real Google SDK over a mocked HTTP transport. No paid calls."""
import hashlib
import json
from pathlib import Path
import re
from unittest.mock import patch

import httpx
import pytest
import yaml
from google import genai
from google.genai import types

from course_harness.batch import BatchScheduler, ResourceLimits, BatchSchedulingError
from course_harness.gemini_adapter import (
    GeminiApiAdapter, ApiAuthenticationError, ApiResponseError, ApiTransientError,
    ApiIntegrityError, ApiBudgetError, ApiDisabledError, MODEL, sha256, verified_api_receipt,
)
from course_harness.run import CourseHarnessController, ManifestStaleError
from course_harness.visual import QUALITY_RUBRIC_VERSION, validate_automatic_visuals

SCHEMA = 'course_harness/schemas/audit.schema.json'
DRAFT = ('# Bài học\n\n## Tình huống và hướng dẫn\n' + 'Nhóm cùng kiểm tra công việc và phản hồi để cải thiện cách thực hiện. ' * 5).strip()
DIMS = ['SOURCE_FIDELITY', 'CONTENT_COMPLETENESS', 'PEDAGOGICAL_QUALITY', 'VISUAL_PEDAGOGY',
        'TERMINOLOGY_CONSISTENCY', 'SOURCE_TRACEABILITY', 'CLARITY_ORGANIZATION', 'FORMATTING']


def envelope(text, **overrides):
    data = {'candidates': [{'content': {'parts': [{'text': text}], 'role': 'model'}, 'finishReason': 'STOP'}],
            'modelVersion': MODEL, 'responseId': 'provider-response-id',
            'usageMetadata': {'promptTokenCount': 100, 'candidatesTokenCount': 50,
                              'thoughtsTokenCount': 30, 'totalTokenCount': 180}}
    data.update(overrides)
    return data


def audit(prompt, verdict='PASS'):
    lid = re.search(r'M\d+-L\d+', prompt).group()
    digest = re.search(r'Exact candidate SHA256: ([0-9a-f]{64})', prompt).group(1)
    return {'lesson_id': lid, 'verdict': verdict, 'summary': 'Independent source-based evaluation',
            'quality_rubric_version': QUALITY_RUBRIC_VERSION, 'quality_score': 100 if verdict == 'PASS' else 75,
            'content_quality_accepted': verdict == 'PASS',
            'dimension_scores': {dim: ('FAILED' if verdict == 'FAIL' and dim == 'SOURCE_FIDELITY' else 'MET') for dim in DIMS},
            'audited_final_sha256': digest, 'findings': [] if verdict == 'PASS' else [{
                'finding_id': 'F01', 'severity': 'HIGH', 'category': 'SOURCE_FIDELITY',
                'source_locator': 'source', 'draft_locator': 'lesson', 'description': 'Needs correction',
                'required_action': 'Correct against the original source'}],
            'limitations': ['Static visual inspection is not human acceptance.']}


def sdk_client(handler):
    return genai.Client(api_key='deterministic-test-key', vertexai=False, http_options=types.HttpOptions(
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
        retry_options=types.HttpRetryOptions(attempts=1), timeout=1000))


@pytest.fixture
def adapter(tmp_path):
    return GeminiApiAdapter(tmp_path / 'evidence', SCHEMA, max_retries=2)


@pytest.fixture
def controller(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    output = tmp_path / 'generated'
    manifest = {'course_id': 'TestCourse', 'lessons': {}, 'modules': {}, 'total_lessons': 7, 'total_modules': 1}
    for number in range(1, 8):
        lid = f'M01-L{number:02}'
        text = 'The team inspects work and feedback to improve how it works.'
        path = source / (lid + '.md')
        path.write_text(text)
        manifest['lessons'][lid] = {'lesson_id': lid, 'title': lid, 'module_id': 'M01',
            'relative_path': path.name, 'source_sha256': sha256(text), 'status': 'AVAILABLE', 'source_type': 'ACTIVITY'}
    manifest_path = tmp_path / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest))
    config = {'models': {role: {'model': MODEL, 'effort': 'high'} for role in ('worker', 'auditor', 'repair')},
              'execution': {'mode': 'gemini_api', 'max_retries': 2},
              'workflow': {'max_repair_rounds': 2},
              'resources': {'max_lessons': 10000, 'max_provider_invocations': 100, 'max_batch_tokens': 1000000},
              'paths': {'course_id': 'TestCourse', 'source_dir': str(source), 'output_dir': str(output),
                        'manifest_path': str(manifest_path), 'prompts_dir': 'course_harness/prompts', 'schema_path': SCHEMA}}
    config_path = tmp_path / 'api.yaml'
    config_path.write_text(yaml.safe_dump(config))
    return CourseHarnessController(str(config_path))


def automatic_client(controller, verdicts=None, draft=DRAFT):
    requests = []
    verdicts = iter(verdicts or [])
    def handler(request):
        payload = json.loads(request.content)
        prompt = payload['contents'][0]['parts'][0]['text']
        is_audit = payload['generationConfig'].get('responseMimeType') == 'application/json'
        role = 'auditor' if is_audit else ('repair' if 'AUDIT_FINDINGS' in prompt or 'PHÁT HIỆN CẦN SỬA' in prompt else 'worker')
        requests.append((role, prompt, payload))
        text = json.dumps(audit(prompt, next(verdicts, 'PASS'))) if is_audit else draft
        return httpx.Response(200, json=envelope(text), headers={'x-request-id': f'request-{len(requests)}'})
    controller.adapter.client = sdk_client(handler)
    return requests


def test_worker_auditor_fully_automatic_and_exact_provenance(controller):
    requests = automatic_client(controller)
    result = controller.process_lesson('M01-L01')
    assert result['status'] == 'PASS', result
    assert result['evidence_class'] == 'REAL_GEMINI_API_VERIFIED'
    assert result['human_review_required'] is True
    assert [r[0] for r in requests] == ['worker', 'auditor']
    assert Path(result['final_path']).read_text() == DRAFT
    receipt = controller.state_mgr.get_audit_receipt(result['audit_invocation_id'])
    assert verified_api_receipt(receipt)
    assert receipt['audited_final_sha256'] == sha256(DRAFT)
    assert receipt['request_id'] == 'request-2'
    assert receipt['usage']['thinking_tokens'] == 30
    assert receipt['response_id'] == 'provider-response-id'
    assert receipt['started_at'] and receipt['completed_at']
    audit_config = requests[1][2]['generationConfig']
    assert audit_config['responseMimeType'] == 'application/json'
    assert audit_config['thinkingConfig']['thinking_level'] == 'HIGH'
    assert set(DIMS) <= set(audit_config['responseJsonSchema']['properties']['dimension_scores']['required'])
    assert not list(Path(controller.evidence_dir).rglob('handoff*'))
    assert controller.state_mgr.is_resumable_pass('M01-L01', result['source_sha256'])
    assert controller.process_lesson('M01-L01')['status'] == 'PASS'
    assert len(requests) == 2


@pytest.mark.parametrize('verdicts,expected,calls,repairs', [
    (['FAIL', 'PASS'], 'PASS', 4, 1),
    (['FAIL', 'FAIL', 'FAIL'], 'NEEDS_HUMAN_REVIEW', 6, 2),
])
def test_quality_fail_bounded_repair_fresh_auditor(controller, verdicts, expected, calls, repairs):
    requests = automatic_client(controller, verdicts)
    result = controller.process_lesson('M01-L01')
    assert result['status'] == expected, result
    assert len(requests) == calls
    assert result['repair_attempts'] == repairs
    ids = [json.loads(p.read_text())['invocation_id'] for p in controller.adapter.evidence_dir.glob('*.try[1-6].json')]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize('data', [None, {}, {'candidates': []}, envelope(''), envelope('x', modelVersion=None),
    envelope('x', candidates=[{'content': {'parts': [{'text': 'truncated'}]}, 'finishReason': 'MAX_TOKENS'}])])
def test_missing_invalid_response(adapter, data):
    adapter.client = sdk_client(lambda request: httpx.Response(200, json=data))
    with pytest.raises((ApiResponseError, ApiIntegrityError)):
        adapter.invoke('test', 'worker', 'M01-L01')
    assert len(list(adapter.evidence_dir.glob('*.try[1-6].json'))) == 1


def test_invalid_json_raw_evidence(adapter):
    raw = 'not valid JSON\n'
    adapter.client = sdk_client(lambda request: httpx.Response(200, text=raw))
    with pytest.raises(ApiResponseError):
        adapter.invoke('test', 'auditor', 'M01-L01')
    assert next(adapter.evidence_dir.glob('*.raw.json')).read_text() == raw


@pytest.mark.parametrize('code', [401, 403])
def test_authentication_failure_never_retried(adapter, code):
    requests = []
    def handler(request):
        requests.append(request)
        return httpx.Response(code, json={'error': {'message': 'key=SECRET', 'code': code}})
    adapter.client = sdk_client(handler)
    with pytest.raises(ApiAuthenticationError):
        adapter.invoke('test', 'worker', 'M01-L01')
    assert len(requests) == 1
    assert 'SECRET' not in ''.join(p.read_text() for p in adapter.evidence_dir.iterdir())


@pytest.mark.parametrize('failure', ['rate', 'timeout'])
def test_retry_transient_errors(adapter, failure):
    requests = []
    def handler(request):
        requests.append(request)
        if len(requests) < 3:
            if failure == 'timeout':
                raise httpx.ReadTimeout('secret key in transport URL', request=request)
            return httpx.Response(429, json={'error': {'code': 429, 'message': 'rate limited'}}, headers={'retry-after': '3'})
        return httpx.Response(200, json=envelope(DRAFT))
    adapter.client = sdk_client(handler)
    with patch('course_harness.gemini_adapter.time.sleep') as sleep:
        text, meta = adapter.invoke('test', 'worker', 'M01-L01')
    assert len(requests) == 3
    assert sleep.call_count == 2
    assert meta['api_attempt'] == 3 and text == DRAFT
    assert len(list(adapter.evidence_dir.glob('*.try[1-6].json'))) == 3


def test_rate_limit_bounded_and_retry_after(adapter):
    adapter.client = sdk_client(lambda request: httpx.Response(429, json={'error': {'code': 429}}, headers={'retry-after': '120'}))
    with patch('course_harness.gemini_adapter.time.sleep') as sleep, pytest.raises(ApiTransientError):
        adapter.invoke('test', 'worker', 'M01-L01')
    sleep.assert_not_called()


def test_five_lesson_sequential_token_accounting_and_resume(controller):
    requests = automatic_client(controller)
    scheduler = BatchScheduler(controller=controller)
    plan = scheduler.plan_batch(requested_ids=[f'M01-L{n:02}' for n in range(1, 6)])
    result = scheduler.execute_batch(plan)
    assert result['summary']['passed'] == 5, result
    assert len(requests) == 10
    assert [re.search(r'M\d+-L\d+', r[1]).group() for r in requests] == [f'M01-L{n:02}' for n in range(1, 6) for _ in range(2)]
    usage = result['budget_consumed']
    assert usage['input_tokens'] == 1000 and usage['output_tokens'] == 500
    assert usage['thinking_tokens'] == 300 and usage['total_tokens'] == 1800
    assert usage['monetary_cost'] is None
    saved_plan = scheduler.load_plan(plan.batch_id)
    result = scheduler.execute_batch(saved_plan, resume_batch_id=plan.batch_id)
    assert result['summary']['skipped'] == 5
    assert len(requests) == 10
    assert result['budget_consumed']['total_tokens'] == 1800


def test_source_checksum_mismatch_no_calls(controller):
    requests = automatic_client(controller)
    manifest = controller.get_manifest()
    Path(controller.source_dir, manifest['lessons']['M01-L01']['relative_path']).write_text('tampered')
    with pytest.raises(ManifestStaleError):
        controller.process_lesson('M01-L01')
    assert requests == []
    with pytest.raises(ManifestStaleError):
        BatchScheduler(controller=controller).plan_batch(requested_ids=['M01-L01'])


def test_interruption_after_worker_resumes_without_repeating_worker(controller):
    requests = automatic_client(controller)
    original = controller._run_auditor
    with patch.object(controller, '_run_auditor', side_effect=KeyboardInterrupt):
        with pytest.raises(KeyboardInterrupt):
            controller.process_lesson('M01-L01')
    assert len(requests) == 1
    controller._run_auditor = original
    assert controller.process_lesson('M01-L01')['status'] == 'PASS'
    assert len(requests) == 2


def test_interruption_after_audit_resumes_without_repeating_audit(controller):
    requests = automatic_client(controller)
    with patch.object(controller.state_mgr, 'record_audit_verdict', side_effect=KeyboardInterrupt):
        with pytest.raises(KeyboardInterrupt):
            controller.process_lesson('M01-L01')
    assert len(requests) == 2
    assert controller.process_lesson('M01-L01')['status'] == 'PASS'
    assert len(requests) == 2


def test_auditor_must_attest_hash(controller):
    requests = automatic_client(controller)
    original = controller.adapter.client.models.generate_content
    def changed(**kwargs):
        if kwargs['config'].response_mime_type == 'application/json':
            bad = audit(kwargs['contents'])
            bad['audited_final_sha256'] = '0' * 64
            return types.GenerateContentResponse(sdk_http_response=types.HttpResponse(body=json.dumps(envelope(json.dumps(bad)))))
        return original(**kwargs)
    with patch.object(controller.adapter.client.models, 'generate_content', side_effect=changed):
        with pytest.raises(ApiIntegrityError):
            controller.process_lesson('M01-L01')
    assert not list(Path(controller.modules_dir).rglob('*.md'))


def test_invalid_audit_does_not_publish(controller):
    def handler(request):
        body = json.loads(request.content)
        text = '{"verdict":"PASS"}' if body['generationConfig'].get('responseMimeType') else DRAFT
        return httpx.Response(200, json=envelope(text))
    controller.adapter.client = sdk_client(handler)
    result = controller.process_lesson('M01-L01')
    assert result['status'] == 'NEEDS_HUMAN_REVIEW'
    assert 'AUDIT_VALIDATION_ERROR' in result['error_category']
    assert not list(Path(controller.modules_dir).rglob('*.md'))


def test_unknown_usage_stops_spending(controller):
    controller.adapter.client = sdk_client(lambda request: httpx.Response(200, json=envelope(DRAFT, usageMetadata=None)))
    scheduler = BatchScheduler(controller=controller)
    with pytest.raises(ApiBudgetError):
        scheduler.execute_batch(scheduler.plan_batch(requested_ids=['M01-L01', 'M01-L02']))
    assert len(list(controller.adapter.evidence_dir.glob('*.try[1-6].json'))) == 1


def test_authentication_halts_batch(controller):
    controller.adapter.client = sdk_client(lambda request: httpx.Response(403, json={'error': {'code': 403}}))
    scheduler = BatchScheduler(controller=controller)
    with pytest.raises(ApiAuthenticationError):
        scheduler.execute_batch(scheduler.plan_batch(requested_ids=['M01-L01', 'M01-L02']))
    assert len(list(controller.adapter.evidence_dir.glob('*.try[1-6].json'))) == 1
    assert controller.state_mgr.load_checkpoint('M01-L01')['status'] == 'BLOCKED'


def test_nonfatal_lesson_failure_continues(controller):
    requests = automatic_client(controller)
    original = controller.process_lesson
    def process(lid):
        if lid == 'M01-L01':
            raise ApiResponseError('Empty provider response')
        return original(lid)
    scheduler = BatchScheduler(controller=controller)
    with patch.object(controller, 'process_lesson', side_effect=process):
        result = scheduler.execute_batch(scheduler.plan_batch(requested_ids=['M01-L01', 'M01-L02']))
    assert result['lessons']['M01-L01']['status'] == 'FAILED'
    assert result['lessons']['M01-L02']['status'] == 'PASS'
    assert len(requests) == 2


def test_dry_run_no_manual_steps_or_provider_calls(controller):
    requests = automatic_client(controller)
    scheduler = BatchScheduler(controller=controller)
    result = scheduler.execute_batch(scheduler.plan_batch(requested_ids=['M01-L01']), dry_run=True)
    assert requests == []
    assert result['manual_steps'] == [] and result['provider_calls'] == 0
    assert 'PUBLISH' in result['workflow']


def test_human_accepted_and_pilot_baselines_never_overwritten(controller):
    requests = automatic_client(controller)
    controller.state_mgr.transition('M01-L01', 'HUMAN_ACCEPTED', {'final_sha256': 'preserve'})
    before = Path(controller.state_mgr._get_checkpoint_path('M01-L01')).read_bytes()
    assert controller.process_lesson('M01-L01', reset=True)['status'] == 'HUMAN_ACCEPTED'
    assert Path(controller.state_mgr._get_checkpoint_path('M01-L01')).read_bytes() == before
    for lid in ('M02-L11', 'M03-L08'):
        controller.manifest = {'lessons': {lid: {'lesson_id': lid}}}
        assert controller.process_lesson(lid, reset=True)['status'] == 'SKIPPED'
    assert requests == []


def test_large_selection_and_concurrency_gate(controller):
    scheduler = BatchScheduler(controller=controller)
    plan = scheduler.plan_batch(requested_ids=[f'M01-L{n:02}' for n in range(1, 8)], limit=7)
    assert len(plan.candidate_lessons) == 7
    scheduler.limits.max_concurrency = 2
    with pytest.raises(BatchSchedulingError, match='sequential'):
        scheduler.execute_batch(plan)


def test_no_photos_even_with_innocent_filename():
    issues = validate_automatic_visuals('# Bài\n![Sơ đồ minh họa](assets/innocent.png)', {'figures': []}, '.')
    assert any('PROHIBITED_INSTRUCTOR_IMAGE' in i for i in issues)


def test_visual_manifest_binding_and_pending_review(controller):
    fixture = Path('course_harness/fixtures/M01_L07_lesson_draft.md').read_text()
    requests = automatic_client(controller, draft=fixture)
    def render(mmd, svg):
        data = '<svg xmlns="http://www.w3.org/2000/svg"><text>Diagram</text></svg>'
        Path(svg).write_text(data)
        return True, 'RENDER_VERIFIED', sha256(data)
    with patch.object(controller.visual_asset_mgr, 'is_renderer_available', return_value=True), patch.object(
        controller.visual_asset_mgr, '_render_mermaid_file', side_effect=render):
        draft, path, meta = controller._run_worker_draft(controller.get_manifest()['lessons']['M01-L01'], 'source')
    visual = controller._last_lesson_visuals['M01-L01']
    assert visual['figures']
    for fig in visual['figures']:
        assert fig['rendered_asset_path'] in draft
        assert fig['visual_review_status'] == 'VISUAL_LAYOUT_NOT_VERIFIED'
    assert validate_automatic_visuals(draft, visual, controller.output_dir) == []
    asset = Path(controller.output_dir, visual['figures'][0]['rendered_asset_path'])
    asset.write_text('<svg><image href="portrait.png"/></svg>')
    assert validate_automatic_visuals(draft, visual, controller.output_dir)


def test_tampered_raw_response_invalidates_resume(controller):
    automatic_client(controller)
    result = controller.process_lesson('M01-L01')
    receipt = controller.state_mgr.get_audit_receipt(result['audit_invocation_id'])
    Path(receipt['raw_response_path']).write_text('{}')
    assert not controller.state_mgr.is_resumable_pass('M01-L01', result['source_sha256'])


def test_bounded_concurrency_after_successful_sequential_batch(controller):
    requests = automatic_client(controller)
    scheduler = BatchScheduler(controller=controller)
    scheduler.execute_batch(scheduler.plan_batch(requested_ids=['M01-L01']))
    scheduler.limits.max_concurrency = 2
    plan = scheduler.plan_batch(requested_ids=['M01-L02', 'M01-L03', 'M01-L04'])
    shared_client = controller.adapter.client
    with patch.object(GeminiApiAdapter, '_get_client', return_value=shared_client), patch.object(GeminiApiAdapter, 'close'):
        result = scheduler.execute_batch(plan)
    assert result['summary']['passed'] == 3, result
    assert len(requests) == 8
    assert len(list(Path(controller.checkpoints_dir).glob('M01-L*.json'))) == 4


def test_repair_then_interruption_requires_fresh_auditor(controller):
    requests = automatic_client(controller, ['FAIL', 'PASS'])
    original = controller._run_auditor
    calls = 0
    def interrupted(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise KeyboardInterrupt
        return original(*args, **kwargs)
    with patch.object(controller, '_run_auditor', side_effect=interrupted):
        with pytest.raises(KeyboardInterrupt):
            controller.process_lesson('M01-L01')
    assert len(requests) == 3
    result = controller.process_lesson('M01-L01')
    assert result['status'] == 'PASS', result
    assert result['repair_attempts'] == 1
    assert len(requests) == 4


def test_structural_failure_repairs_before_auditing(controller):
    requests = automatic_client(controller, draft='broken')
    result = controller.process_lesson('M01-L01')
    assert result['status'] == 'NEEDS_HUMAN_REVIEW'
    assert result['repair_attempts'] == 2
    assert len(requests) == 3
    assert all(role != 'auditor' for role, _, _ in requests)
    assert not list(Path(controller.modules_dir).rglob('*.md'))


def test_timeout_and_retry_exhaustion(adapter):
    requests = []
    def handler(request):
        requests.append(request)
        raise httpx.ReadTimeout('timeout', request=request)
    adapter.client = sdk_client(handler)
    with patch('course_harness.gemini_adapter.time.sleep'), pytest.raises(ApiTransientError):
        adapter.invoke('test', 'worker', 'M01-L01')
    assert len(requests) == 3


def test_model_mismatch_halts_before_publication(controller):
    controller.adapter.client = sdk_client(lambda request: httpx.Response(200, json=envelope(DRAFT, modelVersion='other-model')))
    scheduler = BatchScheduler(controller=controller)
    with pytest.raises(ApiIntegrityError):
        scheduler.execute_batch(scheduler.plan_batch(requested_ids=['M01-L01', 'M01-L02']))
    assert len(list(controller.adapter.evidence_dir.glob('*.try[1-6].json'))) == 1


def test_api_invocation_budget_stops_at_request_boundary(controller):
    requests = automatic_client(controller, ['FAIL', 'PASS'])
    scheduler = BatchScheduler(controller=controller, limits=ResourceLimits(max_provider_invocations=2))
    with pytest.raises(ApiBudgetError):
        scheduler.execute_batch(scheduler.plan_batch(requested_ids=['M01-L01']))
    assert len(requests) == 2
    assert not list(Path(controller.modules_dir).rglob('*.md'))


def test_live_sdk_disabled_and_local_readiness(adapter, monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY', 'never-log-this-key')
    with patch('google.genai.Client') as client:
        with pytest.raises(ApiDisabledError, match='GEMINI_API_NOT_AUTHORIZED'):
            adapter._get_client()
        client.assert_not_called()
    info = adapter.verify_environment()
    assert info['authentication'] == 'NOT_CHECKED' and info['billing'] == 'NOT_CHECKED'
    assert info['status'] == 'PROVIDER_DISABLED'
    assert 'never-log-this-key' not in json.dumps(info)


def test_durable_unknown_inflight_usage_blocks_resume(controller):
    scheduler = BatchScheduler(controller=controller)
    plan = scheduler.plan_batch(requested_ids=['M01-L01'])
    automatic_client(controller)
    scheduler.execute_batch(plan)
    path = next(controller.adapter.evidence_dir.glob('*.try[1-6].json'))
    metadata = json.loads(path.read_text())
    metadata['terminal_status'] = 'STARTED'
    path.write_text(json.dumps(metadata))
    with pytest.raises(ApiBudgetError, match='unknown usage'):
        scheduler.execute_batch(plan, resume_batch_id=plan.batch_id)


def test_complete_visual_pipeline_binds_published_assets(controller):
    fixture = Path('course_harness/fixtures/M01_L07_lesson_draft.md').read_text().replace('M01-L07', 'M01-L01')
    requests = automatic_client(controller, draft=fixture)
    def render(mmd, svg):
        data = '<svg xmlns="http://www.w3.org/2000/svg"><text>Diagram</text></svg>'
        Path(svg).write_text(data)
        return True, 'RENDER_VERIFIED', sha256(data)
    with patch.object(controller.visual_asset_mgr, 'is_renderer_available', return_value=True), patch.object(
        controller.visual_asset_mgr, '_render_mermaid_file', side_effect=render):
        result = controller.process_lesson('M01-L01')
    assert result['status'] == 'PASS', result
    assert len(requests) == 2
    assert result['visual_review_required'] is True
    assert result['visual_manifest_sha256'] == hashlib.sha256(Path(result['visual_manifest_path']).read_bytes()).hexdigest()
    assert 'Rendered SVG evidence:' in requests[1][1]
    for figure in result['visual_figures']:
        asset = Path(result['final_path']).parent / figure['rendered_asset_path']
        assert asset.is_file()
        assert hashlib.sha256(asset.read_bytes()).hexdigest() == figure['rendered_asset_sha256']
    assert controller.state_mgr.is_resumable_pass('M01-L01', result['source_sha256'])


@pytest.mark.parametrize('version', ['gemini-3.8-flash-lite', 'gemini-3.8-flash-preview'])
def test_no_fallback_model_versions(adapter, version):
    adapter.client = sdk_client(lambda request: httpx.Response(200, json=envelope(DRAFT, modelVersion=version)))
    with pytest.raises(ApiIntegrityError):
        adapter.invoke('test', 'worker', 'M01-L01')


@pytest.mark.parametrize('markup', ['![diagram][picture]\n[picture]: https://example.com/photo.png',
                                   '<img src=portrait.png>', '<style>body{background:url(photo.png)}</style>'])
def test_alternative_image_embedding_is_blocked(markup):
    assert validate_automatic_visuals(markup, {'figures': []}, '.')


def test_machine_metadata_is_blocked_before_audit(controller):
    requests = automatic_client(controller, draft=DRAFT + '\nREAL_GEMINI_API_VERIFIED')
    result = controller.process_lesson('M01-L01')
    assert result['status'] == 'NEEDS_HUMAN_REVIEW'
    assert len(requests) == 3
    assert all(role != 'auditor' for role, _, _ in requests)


def test_billing_failure_halts_without_retry(adapter):
    adapter.client = sdk_client(lambda request: httpx.Response(402, json={'error': {'code': 402}}))
    with pytest.raises(ApiBudgetError):
        adapter.invoke('test', 'worker', 'M01-L01')
    assert len(list(adapter.evidence_dir.glob('*.try[1-6].json'))) == 1


def test_api_runtime_boundary_includes_rendering_and_backoff(controller):
    scheduler = BatchScheduler(controller=controller, limits=ResourceLimits(max_batch_runtime_seconds=1))
    scheduler._runtime_started = 0
    scheduler._runtime_before_resume = 0
    with patch('course_harness.batch.time.monotonic', return_value=2), pytest.raises(ApiBudgetError, match='runtime'):
        scheduler._before_api_attempt()


def test_transient_repair_failure_does_not_consume_educational_round(controller):
    requests = automatic_client(controller, ['FAIL', 'PASS'])
    with patch.object(controller, '_run_repair', side_effect=ApiTransientError('temporary outage')):
        with pytest.raises(ApiTransientError):
            controller.process_lesson('M01-L01')
    assert controller.state_mgr.load_checkpoint('M01-L01')['repair_attempts'] == 0
    result = controller.process_lesson('M01-L01')
    assert result['status'] == 'PASS', result
    assert result['repair_attempts'] == 1
    assert len(requests) == 4
