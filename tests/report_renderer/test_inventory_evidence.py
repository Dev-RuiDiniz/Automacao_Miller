"""Refinamento de limites conserva evidências exatas e mantém as validações."""

import copy

import pytest

from infra.report_renderer import anvisa_v8 as v, transport as wire
from tests.report_renderer.test_incremental import source, record, response, analyze, checkpoint, request_data
from tests.report_renderer.test_transport import task_with_inventory, delta


def refinement(scope='block'):
    previous = wire.inventory(task_with_inventory())
    target = previous[0] if scope == 'block' else previous[0]['unidades_fonte'][0]
    start = {'pagina': 1, 'trecho_literal': 'Evento A1', 'localizador': 'Início original.'}
    end = {'pagina': 1, 'trecho_literal': 'Evento A1', 'localizador': 'Fim original.'}
    existing = {'pagina': 1, 'trecho_literal': 'Evento B1'}
    target.update(limites={'inicio': start, 'fim': end}, evidencias=[existing])
    new = {**end, 'trecho_literal': 'Evento A1\nEvento B1'}
    change = {'id': 'B1' if scope == 'block' else 'B1-U1',
              'campos': {'limites': {'inicio': copy.deepcopy(start), 'fim': new}}}
    changes = [change] if scope == 'block' else [{'id': 'B1', 'campos': {}, 'unidades': [change]}]
    return previous, delta(previous, changes), change, end, existing


def target(rows, scope):
    return rows[0] if scope == 'block' else rows[0]['unidades_fonte'][0]


@pytest.mark.parametrize('scope', ['block', 'unit'])
def test_refinement_archives_exact_old_evidence_and_keeps_new_limits(scope):
    previous, patch, change, end, existing = refinement(scope)
    before, original_patch = copy.deepcopy(previous), copy.deepcopy(patch)
    merged = wire.merge_inventory(previous, patch)
    current = target(merged, scope)
    assert current['limites'] == change['campos']['limites']
    assert current['evidencias'] == [existing, end]
    assert target(previous, scope)['limites']['fim'] == end
    assert previous == before and patch == original_patch
    assert previous[0]['unidades_fonte'][0]['ids_eventos'] == merged[0]['unidades_fonte'][0]['ids_eventos']
    assert wire.merge_inventory(merged, delta(merged, patch['blocos'])) == merged


@pytest.mark.parametrize('scope', ['block', 'unit'])
@pytest.mark.parametrize('form', ['adicionar_evidencias', 'campos'])
def test_explicit_additions_and_archive_preserve_order_without_duplicates(scope, form):
    previous, patch, change, end, existing = refinement(scope)
    added = {'pagina': 1, 'trecho_literal': 'Evento C1'}
    if form == 'campos': change['campos']['evidencias'] = [added, end, added]
    else: change['adicionar_evidencias'] = [added, end, added]
    merged = wire.merge_inventory(previous, patch)
    assert target(merged, scope)['evidencias'] == [existing, added, end]


def test_evidence_retained_in_another_local_field_is_not_archived_again():
    previous, patch, _, end, existing = refinement()
    previous[0]['outra_referencia'] = copy.deepcopy(end)
    patch['base_sha256'] = wire.inventory_view(previous)['base_sha256']
    merged = wire.merge_inventory(previous, patch)
    assert merged[0]['evidencias'] == [existing]


def test_different_literal_is_preserved_without_resolving_review_automatically():
    previous, patch, change, end, existing = refinement()
    change['campos']['limites']['fim']['trecho_literal'] = 'Evento C1'
    merged = wire.merge_inventory(previous, patch)
    assert merged[0]['evidencias'] == [existing, end]
    assert merged[0]['limites']['fim']['trecho_literal'] == 'Evento C1'
    assert merged[0]['estado_revisao'] == previous[0]['estado_revisao'] == 'pendente'
    assert merged[0]['pendencias'] == previous[0]['pendencias']


@pytest.mark.parametrize('scope', ['block', 'unit'])
@pytest.mark.parametrize('limits', [None, {}, {'inicio': None, 'fim': None}])
def test_refinement_cannot_erase_or_malform_existing_limits(scope, limits):
    previous, patch, change, _, _ = refinement(scope)
    change['campos']['limites'] = limits
    before = copy.deepcopy(previous)
    with pytest.raises(v.StructureValidationError, match='delta_limites_invalidos'):
        wire.merge_inventory(previous, patch)
    assert previous == before


@pytest.mark.parametrize('scope', ['block', 'unit'])
def test_removal_outside_limits_is_rejected_with_exact_missing_object(scope):
    previous, patch, change, _, _ = refinement(scope)
    original = {'pagina': 1, 'trecho_literal': 'Evento C1', 'localizador': 'Outra evidência.'}
    target(previous, scope)['fundamento'] = original
    change['campos']['fundamento'] = None
    patch['base_sha256'] = wire.inventory_view(previous)['base_sha256']
    with pytest.raises(v.StructureValidationError, match='delta_evidencia_removida') as failure:
        wire.merge_inventory(previous, patch)
    missing = failure.value.diagnostic['evidencias_ausentes']
    assert missing[0]['evidencia'] == original
    assert missing[0]['campo_anterior'].endswith('/campos/fundamento')
    assert 'Evento C1' not in str(failure.value)


@pytest.mark.parametrize('violation', ['quote', 'page', 'old_quote'])
def test_refinement_never_bypasses_literal_and_page_validation(violation):
    task = task_with_inventory()
    previous, patch, change, _, _ = refinement()
    if violation == 'quote': change['campos']['limites']['fim']['trecho_literal'] = 'Inventado.'
    if violation == 'page': change['campos']['limites']['fim']['pagina'] = 2
    if violation == 'old_quote': previous[0]['limites']['fim']['trecho_literal'] = 'Inválido anterior.'
    task['continuation']['reconciliacao_anexos'] = previous
    patch['base_sha256'] = wire.inventory_view(previous)['base_sha256']
    raw = {**response([1], [record()], partial=True), 'reconciliacao_delta': patch}
    raw.pop('reconciliacao_anexos')
    # A decodificação consolida; a orquestração sempre confere o inventário inteiro.
    pages = {1: 'Evento A1\nEvento B1\nEvento C1'}
    with pytest.raises(v.EvidenceValidationError):
        result = wire.decode(raw, task, {}, pages, {1})
        v._validate_block(result, [1], {1}, pages, allow_pending=True)


def test_budget_includes_server_preserved_evidence_and_rejects_atomically(monkeypatch):
    previous, patch, _, _, _ = refinement()
    before = copy.deepcopy(previous)
    monkeypatch.setattr(wire, 'MAX_EXPANDED_BYTES', len(wire.encode(previous)))
    with pytest.raises(v.StructureValidationError, match='expansao_excessiva'):
        wire.merge_inventory(previous, patch)
    assert previous == before


def test_refinement_survives_checkpoint_resume_and_final_validation(monkeypatch):
    previous, _, change, end, existing = refinement()
    text = source()
    task = task_with_inventory()
    task['continuation']['reconciliacao_anexos'] = previous
    with checkpoint(text) as saved:
        saved.save({'schema': 3, 'completed': [], 'pending': [task]})
    calls = []

    def request(messages, *_):
        data = request_data(messages); calls.append(data)
        change['campos'].update(estado_revisao='revisada', pendencias=[])
        return {'paginas': response([1])['paginas'], 'registros': [],
                'reconciliacao_delta': {'base_sha256': data['continuidade']['inventario_preservado']['base_sha256'], 'blocos': [change]}}

    monkeypatch.setattr(v, '_request', request)
    assert analyze(text)[0] == [record()] and len(calls) == 1
    with checkpoint(text) as saved:
        row = saved.load()['completed'][0]['result']['reconciliacao_anexos'][0]
        assert row['evidencias'] == [existing, end]
    monkeypatch.setattr(v, '_request', lambda *_: pytest.fail('Checkpoint fechado não pode chamar IA.'))
    assert analyze(text)[0] == [record()]


def test_exact_missing_evidence_reaches_the_single_correction(monkeypatch):
    text = source()
    task = task_with_inventory()
    quote = {'pagina': 1, 'trecho_literal': 'Evento B1', 'localizador': 'Preservar o objeto.'}
    task['continuation']['reconciliacao_anexos'][0]['fundamento'] = quote
    with checkpoint(text) as saved:
        saved.save({'schema': 3, 'completed': [], 'pending': [task]})
    calls = []

    def request(messages, *_):
        data = request_data(messages); calls.append(data)
        if len(calls) == 2:
            assert data['diagnostico_validacao']['evidencias_ausentes'][0]['evidencia'] == quote
        return {'paginas': response([1])['paginas'], 'registros': [],
                'reconciliacao_delta': {'base_sha256': data['continuidade']['inventario_preservado']['base_sha256'],
                 'blocos': [{'id': 'B1', 'campos': {'fundamento': None}}]}}

    monkeypatch.setattr(v, '_request', request)
    with pytest.raises(v.StructureValidationError, match='delta_evidencia_removida'):
        analyze(text)
    assert len(calls) == 2
    with checkpoint(text) as saved:
        assert saved.load()['pending'][0]['continuation']['reconciliacao_anexos'][0]['fundamento'] == quote


def test_shared_fields_checkpoint_migration_preserves_full_state():
    from tests.report_renderer.test_transport import test_recovery_checkpoint_migration_preserves_every_complete_and_pending_value
    test_recovery_checkpoint_migration_preserves_every_complete_and_pending_value(13)
