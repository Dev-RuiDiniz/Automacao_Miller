"""Releitura controlada, pedidos vazios e diagnóstico sem chamadas desnecessárias."""

import copy
import hashlib
import json

import pytest
from fastapi.testclient import TestClient

from infra.report_renderer import analysis_checkpoint as storage, migrate_checkpoint as migration
from infra.report_renderer import anvisa_v8 as v, incremental as inc, context_window as ctx
from infra.report_renderer import parallel_batches as parallel, diagnostics
from infra.report_renderer.app import app
from tests.report_renderer.test_incremental import source, record, response, analyze, checkpoint


def context_task():
    pages = {n: f'\nEvento A{n}\nEvento B{n}\nEvento C{n}\n' for n in range(1, 21)}
    task = inc._tasks([1], pages)[0]
    ctx.acknowledge(task, {1, 2, 3, 9, 10, 11, 12})
    ctx.acknowledge(task, {1, 2, 3})
    return task, pages


def test_historical_page_is_queued_and_delivered_without_erasing_delivery_history():
    task, pages = context_task()
    delivered = list(task['context']['delivered'])
    assert not ctx.request(task, {'contexto_necessario': [10]}, pages)
    assert ctx.pending(task['context']) == {10}
    assert 10 in parallel.scope(task, pages)
    assert parallel.scope(task, pages) & parallel.scope(inc._tasks([10], pages)[0], pages)
    assert not parallel.scope(task, pages) & parallel.scope(inc._tasks([19, 20], pages)[0], pages)
    packet, window = ctx.build(task, pages)
    assert 10 in window and 'Evento A10' in packet['markdown_documental']
    assert not ctx.acknowledge(task, window)  # Releitura não é avanço documental novo.
    assert not ctx.pending(task['context'])
    assert task['context']['delivered'] == delivered
    assert task['context']['reread']['requests'] == 1
    ctx.validate(task['context'], pages, task['sent'])
    assert 10 in parallel.scope(task, pages)


def test_cached_search_requeues_only_absent_pages_without_rescanning_source():
    task, pages = context_task()
    ctx.add_searches(task, ['Evento A10'], pages)

    class NoScan(dict):
        def items(self):
            pytest.fail('Busca conhecida não deve varrer o Markdown novamente.')

    cached_pages = NoScan(pages)
    ctx.request(task, {'buscas_necessarias': ['Evento A10']}, cached_pages)
    assert ctx.pending(task['context']) == {9, 10, 11}
    ctx.acknowledge(task, {1, 9, 10})
    ctx.request(task, {'buscas_necessarias': ['Evento A10']}, cached_pages)
    assert ctx.pending(task['context']) == {11}
    assert task['context']['reread']['requests'] == 1
    ctx.acknowledge(task, {1, 11})
    with pytest.raises(ctx.ContextRequestError, match='sem nova busca ou página pendente'):
        ctx.request(task, {'buscas_necessarias': ['Evento A10']}, cached_pages)


def test_three_rereads_do_not_reset_on_delivery_but_validated_progress_releases_budget():
    task, pages = context_task()
    for n in [10, 11, 10]:
        ctx.request(task, {'contexto_necessario': [n]}, pages)
        ctx.acknowledge(task, {1, n})
    assert task['context']['reread']['requests'] == 3
    with pytest.raises(ctx.ContextRequestError, match='limite de releituras'):
        ctx.request(copy.deepcopy(task), {'contexto_necessario': [11]}, pages)
    ctx.progress(task)
    ctx.request(task, {'contexto_necessario': [11]}, pages)
    assert task['context']['reread']['requests'] == 1


def test_extra_reread_queues_only_pages_new_to_the_cycle():
    task, pages = context_task()
    for page in (10, 11, 10):
        ctx.request(task, {'contexto_necessario': [page]}, pages)
        ctx.acknowledge(task, {1, page})

    assert not ctx.request(task, {'contexto_necessario': [11, 12]}, pages)
    assert ctx.pending(task['context']) == {12}
    assert task['context']['reread']['requests'] == 4
    _, window = ctx.build(task, pages)
    assert 12 in window and 11 not in window
    ctx.acknowledge(task, window)
    ctx.validate(task['context'], pages, task['sent'])

    with pytest.raises(ctx.ContextRequestError, match='limite de releituras'):
        ctx.request(task, {'contexto_necessario': [9]}, pages)
    ctx.progress(task)
    assert not ctx.request(task, {'contexto_necessario': [9]}, pages)
    assert task['context']['reread']['requests'] == 1


@pytest.mark.parametrize('extra_pages, made_progress', [([16], True), ([16], False), ([16, 17, 19], True)],
                         ids=['com-avanco', 'sem-avanco', 'varias-janelas'])
def test_extra_reread_from_existing_checkpoint(monkeypatch, extra_pages, made_progress):
    text = source(20)
    for page in extra_pages:
        marker = f'Evento C{page}\n'
        text = text.replace(marker, marker + 'texto sintético ' * 260 + '\n')
    source_hash = hashlib.sha256(text.encode()).hexdigest()
    scope = 'protocolo-sintetico'
    previous = storage.AnalysisCheckpoint({
        **inc.identity(source_hash, 20),
        # Identidade do renderizador anterior à rodada extra, implantado em b006b7f.
        'implementation_sha256': '2d82eb1598f6eab4db3e1baecd49aed88b5686f6f9c80fcd0865e4fdaa1c2cf5',
        'instructions_sha256': '1c26ea5b1e7ad1f0eb152da397f1a69741a00a1e8b492633f25f161dac11c250',
    }, scope)
    initial_requests = iter([[10, 14, 16, 17, 19], [18], [10], [14], [10]])

    def interrupted_request(*_):
        pages = next(initial_requests, None)
        if pages is None:
            raise v.AnvisaError('IA: interrupção sintética.')
        return {'contexto_necessario': pages}

    monkeypatch.setattr(v, '_request', interrupted_request)
    with previous:
        with pytest.raises(v.AnvisaError, match='interrupção sintética'):
            v.analyze(text, 20, source_hash, 'chave-ficticia', 600, checkpoint_store=previous)
        previous_state = previous.load()
    assert previous_state['pending'][0]['context']['reread']['requests'] == 3
    original_bytes = previous.path.read_bytes()

    assert migration.migrate(text, scope, previous.key)['status'] == 'migrado'
    assert previous.path.read_bytes() == original_bytes
    with checkpoint(text) as saved:
        assert saved.load()['pending'] == previous_state['pending']

    first_batch_calls = []

    def request_after_resume(messages, *_):
        data = json.loads(messages[-1]['content'])
        targets = data['paginas_alvo']
        if targets[0] != 1:
            return response(targets)
        window = data['contexto_recuperado']['paginas_nesta_chamada']
        first_batch_calls.append(window)
        if len(first_batch_calls) == 1:
            assert 10 in window and 14 not in window and 16 not in window
            monkeypatch.setattr(ctx, 'MAX_DATA_BYTES', 6000)
            return {'contexto_necessario': [14, *extra_pages]}
        assert len(first_batch_calls) <= len(extra_pages) + 1
        assert extra_pages[len(first_batch_calls) - 2] in window and 14 not in window
        assert len(set(extra_pages) & set(window)) == 1
        if len(first_batch_calls) <= len(extra_pages):
            return response(targets, partial=True)
        if made_progress:
            return response(targets, [record()])
        return response(targets, partial=True)

    monkeypatch.setattr(v, '_request', request_after_resume)
    if made_progress:
        assert analyze(text)[0] == [record()]
        with checkpoint(text) as saved:
            assert 'reread' not in saved.load()['completed'][0]['context']
    else:
        with pytest.raises(ctx.ContextRequestError, match='limite de releituras'):
            analyze(text)
        assert len(first_batch_calls) == 2
        with checkpoint(text) as saved:
            context = saved.load()['pending'][0]['context']
            assert context['reread']['requests'] == 4
            assert 16 in context['last_window']

        monkeypatch.setattr(v, '_request', lambda *_: {'contexto_necessario': [17]})
        with pytest.raises(ctx.ContextRequestError, match='limite de releituras'):
            analyze(text)


@pytest.mark.parametrize('empty', [{'contexto_necessario': []}, {'buscas_necessarias': []},
                                 {'contexto_necessario': [], 'buscas_necessarias': []}])
def test_empty_optional_requests_validate_cards_in_the_same_call(monkeypatch, empty):
    calls = []

    def request(*_):
        calls.append(True)
        return {**response([1], [record()]), **empty}

    monkeypatch.setattr(v, '_request', request)
    assert analyze(source())[0] == [record()]
    assert len(calls) == 1


def test_only_empty_fields_do_not_create_an_unbounded_context_loop(monkeypatch):
    calls = []

    def request(*_):
        calls.append(True)
        return {'contexto_necessario': [], 'buscas_necessarias': []}

    monkeypatch.setattr(v, '_request', request)
    with pytest.raises(v.StructureValidationError):
        analyze(source())
    assert len(calls) == 2  # Resposta incompleta usa somente a correção já prevista.


def test_reread_budget_survives_automatic_windows_and_manual_resume(monkeypatch):
    monkeypatch.setattr(inc, 'MAX_CONTINUATIONS', 1)
    requested = iter([10, 14, 10, 14, 10, 14])
    calls = []

    def request(*_):
        calls.append(True)
        return {'contexto_necessario': [next(requested)]}

    monkeypatch.setattr(v, '_request', request)
    text = source(20)
    with pytest.raises(ctx.ContextRequestError, match='limite de releituras'):
        analyze(text)
    assert len(calls) == 6
    with checkpoint(text) as saved:
        assert saved.load()['pending'][0]['context']['reread']['requests'] == 3
    monkeypatch.setattr(v, '_request', lambda *_: {'contexto_necessario': [14]})
    with pytest.raises(ctx.ContextRequestError, match='limite de releituras'):
        analyze(text)


def test_analysis_finishes_after_controlled_reread_without_reprocessing_closed_batches(monkeypatch):
    calls = []
    first_calls = []

    def request(messages, *_):
        data = json.loads(messages[-1]['content']); calls.append(data)
        targets = data['paginas_alvo']
        if targets[0] == 1:
            first_calls.append(data)
            if len(first_calls) <= 3:
                return {'contexto_necessario': [[10], [14], [10]][len(first_calls) - 1]}
            assert 10 in data['contexto_recuperado']['paginas_nesta_chamada']
            return response(targets, [record()])
        return response(targets)

    monkeypatch.setattr(v, '_request', request)
    text = source(20)
    assert analyze(text)[0] == [record()]
    assert len(first_calls) == 4 and len(calls) == 7
    with checkpoint(text) as saved:
        state = saved.load()
        assert not state['pending']
        context = state['completed'][0]['context']
        assert {10, 14} <= set(context['delivered'])
        assert 'reread' not in context
    monkeypatch.setattr(v, '_request', lambda *_: pytest.fail('Retomada concluída não chama IA.'))
    assert analyze(text)[0] == [record()]


@pytest.mark.parametrize('violation', ['boolean', 'unknown_page', 'duplicates', 'limit', 'pending_in_window', 'unseen'])
def test_corrupt_reread_metadata_is_rejected(violation):
    task, pages = context_task()
    ctx.request(task, {'contexto_necessario': [10]}, pages)
    data = task['context']['reread']
    if violation == 'boolean': data['requests'] = True
    if violation == 'unknown_page': data['seen'].append(999)
    if violation == 'duplicates': data['pending'].append(10)
    if violation == 'limit': data['requests'] = 5
    if violation == 'pending_in_window': data['pending'] = [1]; data['seen'] = [1, 10]
    if violation == 'unseen': data['seen'] = []
    with pytest.raises(ValueError): ctx.validate(task['context'], pages, task['sent'])


@pytest.mark.parametrize('storage_failure', [False, True])
def test_context_failure_preserves_private_response_and_is_not_infrastructure(monkeypatch, diagnostics_root, storage_failure):
    monkeypatch.setenv('INTERNAL_API_TOKEN', 'token-ficticio')
    monkeypatch.setenv('OPENROUTER_API_KEY', 'chave-ficticia')
    raw = {'contexto_necessario': [1], 'registros': [record()]}
    calls = []

    def request(*_):
        calls.append(True)
        return copy.deepcopy(raw)

    monkeypatch.setattr(v, '_request', request)
    if storage_failure:
        def fail(*_): raise diagnostics.DiagnosticStorageError('Falha sintética de persistência.')
        monkeypatch.setattr(diagnostics.DiagnosticWriter, '__call__', fail)
    text = source()
    result = TestClient(app).post('/v1/analyze-anvisa-v8', headers={'X-Internal-Token': 'token-ficticio'}, json={
        'markdown': text, 'page_count': 1, 'markdown_sha256': hashlib.sha256(text.encode()).hexdigest(),
        'source_filename': 'sintetico.pdf', 'diagnostic_context': {
            'submission_id': 'protocolo-sintetico', 'attempt_number': 1, 'execution_id': 'execucao-sintetica'}})
    assert len(calls) == 1
    assert result.status_code == (500 if storage_failure else 422)
    if storage_failure:
        assert 'ARMAZENAMENTO' in result.json()['detail']
    else:
        assert 'ANV8D-' in result.json()['detail']
        assert 'Evento A1' not in result.json()['detail']
        files = list(diagnostics_root.rglob('ANV8D-*.json'))
        assert len(files) == 1
        saved = json.loads(files[0].read_text())
        assert saved['transporte_recebido'] == saved['resposta_rejeitada'] == raw
        assert saved['contexto']['pedido'] == {'contexto_necessario': [1]}
        assert saved['contexto']['janela_atual'] == [1]
        assert saved['falha']['motivo'] == 'contexto_sem_avanco'
        assert saved['context']['execution_id'] == 'execucao-sintetica'
    with checkpoint(text) as saved:
        assert saved.load()['pending'][0]['records'] == []


def test_previous_checkpoint_migration_preserves_all_values():
    from tests.report_renderer.test_transport import test_recovery_checkpoint_migration_preserves_every_complete_and_pending_value
    test_recovery_checkpoint_migration_preserves_every_complete_and_pending_value(14)
