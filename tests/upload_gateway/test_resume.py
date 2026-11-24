import base64
import hashlib
import io
import json
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi import HTTPException

from infra.upload_gateway import app as gateway
from tests.upload_gateway.test_api import make_client

AUTH = {"X-Landing-Token": "landing-test"}


def failed_document(tmp_path, monkeypatch):
    client = make_client(tmp_path)
    created = client.post('/api/v1/submissions', headers=AUTH,
                          files={'file': ('teste---sintetico.pdf', b'%PDF-1.7 synthetic', 'application/pdf')}).json()
    sid = created['submission_id']
    gateway.store.update(sid, status='erro', message='IA: OpenRouter retornou HTTP 402.')
    gateway.store.errors[sid] = [{'error_message': 'IA: OpenRouter retornou HTTP 402.'}]
    gateway.store.attempts[sid] = [{'attempt_number': 1, 'execution_id': 'original', 'status': 'erro'}]
    calls = []
    monkeypatch.setenv('N8N_SUBMISSION_WEBHOOK_URL', 'http://n8n/webhook/teste')
    monkeypatch.setattr(gateway, 'dispatch_webhook', lambda url, payload: calls.append(payload))
    return client, sid, calls


def artifact(tmp_path, sid, kind, filename, data, metadata=None, version=1):
    prefix = Path(gateway.store.get(sid).source_key).parent
    target = tmp_path / prefix / filename
    target.write_bytes(data)
    item = {'artifact_id': len(gateway.store.artifacts[sid]) + 1, 'artifact_type': kind,
            'version': version, 'storage_key': str(target.relative_to(tmp_path)),
            'sha256': hashlib.sha256(data).hexdigest(), 'size_bytes': len(data), 'metadata': metadata or {}}
    gateway.store.artifacts[sid].append(item)
    return item


def markdown_artifact(tmp_path, sid):
    item = gateway.store.get(sid)
    text = f'---\nconverter_version: 0.4.0\nsource_filename: teste---sintetico.pdf\nsource_sha256: {item.sha256}\npage_count: 1\nsource_document_id: {sid}\n---\n\n## Página 1\nDocumento sintético sem atos regulatórios.'
    return artifact(tmp_path, sid, 'markdown', 'markdown-v1.md', text.encode(), {'warnings': ['Aviso preservado.']})


def report_artifact(tmp_path, sid, markdown, prompt='regulatory-extraction-v5-full-document-batched', info=None):
    return artifact(tmp_path, sid, 'report_markdown', 'report-v1.md', b'# Relatorio sintetico\n',
                    {'prompt_version': prompt, 'source_markdown_sha256': markdown['sha256'], 'report_context': info or {}})


def test_resume_reuses_saved_markdown_without_reupload(tmp_path, monkeypatch):
    client, sid, calls = failed_document(tmp_path, monkeypatch)
    saved = markdown_artifact(tmp_path, sid)
    before = (tmp_path / saved['storage_key']).read_bytes()
    assert client.get(f'/api/v1/submissions/{sid}/resume', headers=AUTH).json()['stage'] == 'analysis'
    response = client.post(f'/api/v1/submissions/{sid}/reprocess', headers=AUTH,
                           json={'storage_key': '../../outro.md', 'resume_stage': 'report'})
    assert response.status_code == 202
    assert response.json()['resumed_from']['stage'] == 'analysis'
    assert calls == [{'submission_id': sid, 'source': 'processing_resume'}]
    assert gateway.store.get(sid).status == 'recebido'
    assert len(gateway.store.reviews[sid]) == 1
    assert gateway.store.reviews[sid][0]['decision'] == 'reprocessamento_autorizado'
    assert gateway.store.errors[sid][0]['error_message'].endswith('402.')
    assert (tmp_path / saved['storage_key']).read_bytes() == before


def test_resume_without_markdown_starts_at_conversion(tmp_path, monkeypatch):
    client, sid, calls = failed_document(tmp_path, monkeypatch)
    result = client.post(f'/api/v1/submissions/{sid}/reprocess', headers=AUTH)
    assert result.status_code == 202 and result.json()['resumed_from']['stage'] == 'conversion'
    assert len(calls) == 1


@pytest.mark.parametrize('state', ['recebido', 'em_processamento', 'aguardando_revisao', 'concluido'])
def test_resume_rejects_non_error_documents(tmp_path, monkeypatch, state):
    client, sid, calls = failed_document(tmp_path, monkeypatch)
    gateway.store.update(sid, status=state)
    assert client.post(f'/api/v1/submissions/{sid}/reprocess', headers=AUTH).status_code == 409
    assert not calls


def test_resume_requires_authentication_and_existing_protocol(tmp_path, monkeypatch):
    client, sid, calls = failed_document(tmp_path, monkeypatch)
    assert client.post(f'/api/v1/submissions/{sid}/reprocess').status_code == 403
    assert client.post('/api/v1/submissions/inexistente/reprocess', headers=AUTH).status_code == 404
    assert not calls


def test_concurrent_resume_requests_dispatch_only_once(tmp_path, monkeypatch):
    client, sid, calls = failed_document(tmp_path, monkeypatch)
    markdown_artifact(tmp_path, sid)
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: client.post(f'/api/v1/submissions/{sid}/reprocess', headers=AUTH), range(2)))
    assert sorted(r.status_code for r in responses) == [202, 409]
    assert len(calls) == len(gateway.store.reviews[sid]) == 1


def test_request_does_not_repeat_a_fast_failure_after_preview(tmp_path, monkeypatch):
    client, sid, calls = failed_document(tmp_path, monkeypatch)
    original = gateway.store.request_processing_resume
    def changed_state(submission_id, actor, stage, expected_updated_at):
        gateway.store.update(sid, status='em_processamento')
        gateway.store.update(sid, status='erro', message='Outra tentativa já executou e falhou.')
        return original(submission_id, actor, stage, expected_updated_at)
    monkeypatch.setattr(gateway.store, 'request_processing_resume', changed_state)
    assert client.post(f'/api/v1/submissions/{sid}/reprocess', headers=AUTH).status_code == 409
    assert not calls and not gateway.store.reviews.get(sid)


@pytest.mark.parametrize('corruption', ['content', 'missing', 'foreign_path', 'pages', 'source'])
def test_resume_rejects_damaged_or_unrelated_markdown(tmp_path, monkeypatch, corruption):
    client, sid, calls = failed_document(tmp_path, monkeypatch)
    saved = markdown_artifact(tmp_path, sid)
    path = tmp_path / saved['storage_key']
    if corruption == 'content': path.write_bytes(path.read_bytes() + b'ALTERADO')
    elif corruption == 'missing': path.unlink()
    elif corruption == 'foreign_path': saved['storage_key'] = '../fora.md'
    else:
        data = path.read_text().replace('page_count: 1', 'page_count: 2') if corruption == 'pages' else path.read_text().replace(gateway.store.get(sid).sha256, 'a' * 64)
        path.write_text(data)
        saved.update(sha256=hashlib.sha256(path.read_bytes()).hexdigest(), size_bytes=path.stat().st_size)
    assert client.post(f'/api/v1/submissions/{sid}/reprocess', headers=AUTH).status_code == 409
    assert gateway.store.get(sid).status == 'erro'
    assert not calls and not gateway.store.reviews.get(sid)


def test_dispatch_failure_allows_new_explicit_attempt(tmp_path, monkeypatch):
    client, sid, calls = failed_document(tmp_path, monkeypatch)
    markdown_artifact(tmp_path, sid)
    def failed(*_): raise HTTPException(503, 'Falha de despacho')
    monkeypatch.setattr(gateway, 'dispatch_webhook', failed)
    assert client.post(f'/api/v1/submissions/{sid}/reprocess', headers=AUTH).status_code == 503
    assert gateway.store.get(sid).status == 'erro'
    monkeypatch.setattr(gateway, 'dispatch_webhook', lambda *_: None)
    assert client.post(f'/api/v1/submissions/{sid}/reprocess', headers=AUTH).status_code == 202


def test_dispatch_timeout_does_not_reset_already_claimed_document(tmp_path, monkeypatch):
    client, sid, _ = failed_document(tmp_path, monkeypatch)
    def claimed(*_):
        gateway.store.update(sid, status='em_processamento')
        raise HTTPException(503, 'Timeout depois do recebimento')
    monkeypatch.setattr(gateway, 'dispatch_webhook', claimed)
    assert client.post(f'/api/v1/submissions/{sid}/reprocess', headers=AUTH).status_code == 202
    assert gateway.store.get(sid).status == 'em_processamento'


def test_internal_resume_requires_matching_active_attempt(tmp_path, monkeypatch):
    client, sid, _ = failed_document(tmp_path, monkeypatch)
    source = markdown_artifact(tmp_path, sid)
    path = f'/internal/submissions/{sid}/resume-context'
    payload = {'attempt_number': 2, 'execution_id': 'nova'}
    assert client.post(path, json=payload).status_code == 403
    assert client.post(path, headers={'X-Internal-Token': 'internal-test'}, json=payload).status_code == 409
    gateway.store.update(sid, status='em_processamento')
    gateway.store.attempts[sid].append({'attempt_number': 2, 'execution_id': 'nova', 'status': 'em_processamento'})
    result = client.post(path, headers={'X-Internal-Token': 'internal-test'}, json=payload)
    assert result.status_code == 200
    assert result.json()['metadata']['markdown_sha256'] == source['sha256']
    assert result.json()['warnings'] == ['Aviso preservado.']
    assert result.json()['attempt_number'] == 2


def test_report_checkpoint_skips_ia_and_reuses_matching_pdf(tmp_path, monkeypatch):
    client, sid, _ = failed_document(tmp_path, monkeypatch)
    source = markdown_artifact(tmp_path, sid)
    report = report_artifact(tmp_path, sid, source)
    pdf = b'%PDF-1.7 synthetic report'
    artifact(tmp_path, sid, 'report_pdf', 'report-v1.pdf', pdf, {'source_report_sha256': report['sha256']})
    context = gateway.processing_checkpoint(sid)
    assert context['resume_stage'] == 'report'
    assert base64.b64decode(context['resume_report']['prepared_pdf_base64']) == pdf
    assert client.post(f'/api/v1/submissions/{sid}/reprocess', headers=AUTH).json()['resumed_from']['stage'] == 'report'


def test_report_without_safe_source_link_restarts_only_analysis(tmp_path, monkeypatch):
    _, sid, _ = failed_document(tmp_path, monkeypatch)
    source = markdown_artifact(tmp_path, sid)
    report = report_artifact(tmp_path, sid, source)
    report['metadata']['source_markdown_sha256'] = '0' * 64
    assert gateway.processing_checkpoint(sid)['resume_stage'] == 'analysis'


def test_report_before_new_conversion_is_not_reused_even_with_same_source_hash(tmp_path, monkeypatch):
    _, sid, _ = failed_document(tmp_path, monkeypatch)
    source = markdown_artifact(tmp_path, sid)
    report_artifact(tmp_path, sid, source)
    source['version'] = 2
    assert gateway.processing_checkpoint(sid)['resume_stage'] == 'analysis'


def test_resume_rejects_active_attempt(tmp_path, monkeypatch):
    client, sid, calls = failed_document(tmp_path, monkeypatch)
    gateway.store.attempts[sid][0]['status'] = 'em_processamento'
    assert client.post(f'/api/v1/submissions/{sid}/reprocess', headers=AUTH).status_code == 409
    assert not calls


def test_resume_requires_configured_processing_webhook(tmp_path, monkeypatch):
    client, sid, calls = failed_document(tmp_path, monkeypatch)
    monkeypatch.delenv('N8N_SUBMISSION_WEBHOOK_URL')
    assert client.post(f'/api/v1/submissions/{sid}/reprocess', headers=AUTH).status_code == 503
    assert gateway.store.get(sid).status == 'erro'
    assert not calls


def test_v8_checkpoint_reuses_pdf_from_verified_bundle(tmp_path, monkeypatch):
    client, sid, _ = failed_document(tmp_path, monkeypatch)
    source = markdown_artifact(tmp_path, sid)
    pdf = b'%PDF-1.7 V8 synthetic'
    coverage = {'fonte': {'sha256': source['sha256']}, 'situacao_da_entrega': 'COMPLETA',
                'pendencias_integridade': [], 'artefatos_finais_pdf_jsonl': {
                    'relatorio_anvisa_v8.pdf': {'sha256': hashlib.sha256(pdf).hexdigest(), 'bytes': len(pdf)}}}
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as archive:
        archive.writestr('relatorio_anvisa_v8.pdf', pdf)
        archive.writestr('cobertura_anvisa_v8.json', json.dumps(coverage))
        archive.writestr('dados_anvisa_v8.jsonl', '')
        archive.writestr('verificacao_anvisa_v8.txt', 'Teste sintético')
    bundle = artifact(tmp_path, sid, 'private_bundle', 'report-v1-anvisa-v8.zip', output.getvalue())
    report_artifact(tmp_path, sid, source, 'V8-autossuficiente', {
        'verification_bundle_storage_key': bundle['storage_key'], 'verification_bundle_sha256': bundle['sha256']})
    result = gateway.processing_checkpoint(sid)
    assert result['resume_stage'] == 'report'
    assert base64.b64decode(result['resume_report']['prepared_pdf_base64']) == pdf
    (tmp_path / bundle['storage_key']).write_bytes(b'corrompido')
    assert client.post(f'/api/v1/submissions/{sid}/reprocess', headers=AUTH).status_code == 409
