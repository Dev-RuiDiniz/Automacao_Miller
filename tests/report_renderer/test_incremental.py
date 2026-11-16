import hashlib
import copy
import json
import os

import pytest
from fastapi.testclient import TestClient

from infra.report_renderer import analysis_checkpoint as storage, anvisa_pdf, anvisa_v8 as v, incremental as inc
from infra.report_renderer.app import app
from infra.report_renderer import migrate_checkpoint as migration
from infra.report_renderer import context_window as ctx, transport


def source(count=1):
    return "".join(f"## Página {n}\nEvento A{n}\nEvento B{n}\nEvento C{n}\n" for n in range(1, count + 1))


def record(page=1, suffix="A"):
    return {"id": f"ANV8-P{page}-{suffix}", "categoria": "outros", "destino": "excluido",
            "justificativa": "Caso sintético.", "paginas_origem": [page],
            "evidencias": [{"pagina": page, "trecho_literal": f"Evento {suffix}{page}"}]}


def response(targets, records=(), *, partial=False, ids=None):
    ids = [r["id"] for r in records] if ids is None else ids
    return {"paginas": [{"pagina": n, "estado": "pendente" if partial else "analisada",
                          "observacao": "Revisão sintética efetiva."} for n in targets],
            "registros": list(records), "reconciliacao_anexos": [
                {"estado_revisao": "pendente" if partial else "revisada",
                 "unidades_fonte": [{"ids_eventos": ids}], "pendencias": ["Continuar unidades."] if partial else []}]}


def checkpoint(text, scope="protocolo-sintetico"):
    count = text.count("## Página ")
    return storage.AnalysisCheckpoint(inc.identity(hashlib.sha256(text.encode()).hexdigest(), count), scope)


def analyze(text, scope="protocolo-sintetico"):
    with checkpoint(text, scope) as saved:
        return v.analyze(text, text.count("## Página "), hashlib.sha256(text.encode()).hexdigest(),
                         "chave-ficticia", 600, checkpoint_store=saved)


def request_data(messages):
    data = json.loads(messages[-1]["content"])
    return transport.expand(data, data.get("evidencias_compartilhadas", {}))


def full_record(page=1, suffix="A", *, pending=False):
    item = record(page, suffix)
    item.update(destino="incluido", justificativa_destino=item.pop("justificativa"),
                conferencia_integridade={"estado": "pendente" if pending else "revisada",
                                         "pendencias": ["Conferir a fonte contra a ficha."] if pending else []},
                campos_adicionais={})
    for key in v.FIELDS:
        item[key] = {"estado": "confirmado", "valor": f"Evento {suffix}{page}",
                     "evidencias": copy.deepcopy(item["evidencias"])}
    for key in v.ARRAYS:
        item[key] = []
    return item


def test_pending_units_continue_in_groups_with_original_ids_and_evidence(monkeypatch):
    calls = []
    records = [record(suffix=s) for s in "ABC"]

    def request(messages, *_):
        data = request_data(messages)
        calls.append(data)
        assert data["continuidade"]["limite_eventos_resposta"] == 8
        assert inc.CONTINUATION in [m["content"] for m in messages]
        i = len(calls) - 1
        if i:
            continuity = data["continuidade"]
            assert continuity["indice_registros_preservados"] == [ctx.record_index(r) for r in records[:i]]
            assert continuity["limite_novos_eventos"] == 8
            assert inc.CONTINUATION in [m["content"] for m in messages]
        return response([1], [records[i]], partial=i < 2, ids=[r["id"] for r in records[:min(i + 2, 3)]])

    monkeypatch.setattr(v, "_request", request)
    found, coverage = analyze(source())
    assert found == records and len(calls) == 3
    assert coverage["evidencias_literais_conferidas"] == 3
    assert coverage["paginas"][0]["estado"] == "analisada"
    with checkpoint(source()) as saved:
        state = saved.load()
    assert not state["pending"] and len(state["completed"]) == 1


def test_dense_source_uses_smaller_targets_without_cutting_page_text(monkeypatch):
    text = source(4)
    calls = []
    monkeypatch.setattr(inc, "MAX_TARGET_CHARS", 50)

    def request(messages, *_):
        data = request_data(messages)
        calls.append(data["paginas_alvo"])
        assert len(data["paginas_alvo"]) == 1
        for n in data["paginas_alvo"]:
            assert f"Evento A{n}\nEvento B{n}\nEvento C{n}\n" in data["markdown_documental"]
        return response(data["paginas_alvo"])

    monkeypatch.setattr(v, "_request", request)
    _, coverage = analyze(text)
    assert calls == [[1], [2], [3], [4]]
    assert len(coverage["paginas"]) == 4


def test_failure_resumes_only_unfinished_batches_and_completed_analysis_uses_no_ia(monkeypatch):
    text = source(10)
    calls = []

    def request(messages, *_):
        targets = request_data(messages)["paginas_alvo"]
        calls.append(targets)
        if targets[0] == 6:
            raise v.AnvisaError("IA: falha sintética após lote salvo.")
        return response(targets, [record(1)])

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.AnvisaError):
        analyze(text)
    with checkpoint(text) as saved:
        before = saved.load()
    assert before["completed"][0]["targets"] == list(range(1, 6))

    def resume(messages, *_):
        data = request_data(messages)
        assert data["paginas_alvo"] == list(range(6, 11))
        calls.append(data["paginas_alvo"])
        return response(data["paginas_alvo"], [record(6)])

    monkeypatch.setattr(v, "_request", resume)
    found, coverage = analyze(text)
    assert found == [record(1), record(6)]
    assert coverage["processamento_incremental"]["paginas_reutilizadas"] == list(range(1, 6))
    assert len(calls) == 3
    monkeypatch.setattr(v, "_request", lambda *_: pytest.fail("Lote concluído não deve consumir IA."))
    assert analyze(text)[0] == found


def test_resume_preserves_validated_records_inside_pending_page(monkeypatch):
    calls = []

    def request(messages, *_):
        calls.append(request_data(messages))
        if len(calls) == 2:
            raise v.AnvisaError("IA: falha sintética durante a continuação.")
        return response([1], [record()], partial=True, ids=[record()["id"], record(suffix="B")["id"]])

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.AnvisaError):
        analyze(source())

    def resume(messages, *_):
        data = request_data(messages)
        assert data["continuidade"]["indice_registros_preservados"] == [ctx.record_index(r) for r in [record()]]
        return response([1], [record(suffix="B")], ids=[record()["id"], record(suffix="B")["id"]])

    monkeypatch.setattr(v, "_request", resume)
    assert analyze(source())[0] == [record(), record(suffix="B")]


@pytest.mark.parametrize("violation", ["change_id_record", "new_id_same_record", "drop_reserved_id"])
def test_continuation_cannot_rewrite_duplicate_or_drop_pending_units(monkeypatch, violation):
    calls = []

    def request(messages, *_):
        calls.append(request_data(messages))
        if len(calls) == 1:
            return response([1], [record()], partial=True, ids=[record()["id"], record(suffix="B")["id"]])
        if violation == "change_id_record":
            changed = dict(record(), justificativa="Valor diferente.")
            return response([1], [changed], ids=[record()["id"], record(suffix="B")["id"]])
        if violation == "new_id_same_record":
            return response([1], [dict(record(), id=record(suffix="B")["id"])], ids=[record()["id"], record(suffix="B")["id"]])
        return response([1], [], ids=[record()["id"]])

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.StructureValidationError):
        analyze(source())
    assert len(calls) == 3
    with checkpoint(source()) as saved:
        state = saved.load()
    assert state["pending"][0]["records"] == [record()]
    assert not state["completed"]


def test_no_progress_stops_and_keeps_pending_checkpoint(monkeypatch):
    calls = []

    def request(messages, *_):
        calls.append(request_data(messages))
        return response([1], [record()], partial=True)

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.AnvisaError, match="sem progresso"):
        analyze(source())
    assert len(calls) == 3
    with checkpoint(source()) as saved:
        assert saved.load()["pending"][0]["records"] == [record()]


def test_group_window_continues_automatically_with_preserved_progress(monkeypatch):
    monkeypatch.setattr(inc, "MAX_CONTINUATIONS", 1)
    calls = []

    def request(messages, *_):
        data = request_data(messages)
        calls.append(data)
        if len(calls) == 1:
            return response([1], [record()], partial=True)
        assert data["continuidade"]["indice_registros_preservados"] == [ctx.record_index(r) for r in [record()]]
        return response([1], [record(suffix="B")], ids=[record()["id"], record(suffix="B")["id"]])

    monkeypatch.setattr(v, "_request", request)
    found, coverage = analyze(source())
    assert found == [record(), record(suffix="B")] and len(calls) == 2
    assert coverage["processamento_incremental"]["continuacoes_automaticas"] == 1
    with checkpoint(source()) as saved:
        assert saved.load()["pending"] == []


@pytest.mark.parametrize("damage", ["json", "digest", "semantic", "missing"])
def test_corrupt_checkpoint_blocks_ia_instead_of_restarting_silently(monkeypatch, damage):
    monkeypatch.setattr(v, "_request", lambda *_: response([1], [record()]))
    analyze(source())
    with checkpoint(source()) as saved:
        if damage == "missing":
            saved.path.unlink()
        elif damage == "json":
            saved.path.write_text("incompleto")
        elif damage == "digest":
            data = json.loads(saved.path.read_text())
            data["state"]["completed"][0]["result"]["registros"][0]["justificativa"] = "Outro valor."
            saved.path.write_text(json.dumps(data))
        else:
            data = saved.load()
            data["completed"][0]["result"]["registros"][0]["evidencias"][0]["trecho_literal"] = "Texto ausente."
            saved.save(data)
    monkeypatch.setattr(v, "_request", lambda *_: pytest.fail("Checkpoint inválido não deve consumir IA."))
    with pytest.raises(storage.CheckpointStorageError):
        analyze(source())


def test_identity_and_scope_isolate_sources_models_and_protocols():
    text = source()
    first = checkpoint(text)
    with first as saved:
        saved.save({"teste": True})
    assert checkpoint(text, "outro-protocolo").key != first.key
    assert checkpoint(text + "Outro texto.").key != first.key
    identity = inc.identity(hashlib.sha256(text.encode()).hexdigest(), 1)
    identity["model"] = "modelo-diferente"
    with storage.AnalysisCheckpoint(identity, "protocolo-sintetico") as other:
        assert other.load() is None and other.key != first.key


def test_atomic_storage_failure_preserves_previous_state_and_private_permissions(monkeypatch):
    with checkpoint(source()) as saved:
        saved.save({"version": 1})
        original = saved.path.read_bytes()
        monkeypatch.setattr(os, "replace", lambda *_: (_ for _ in ()).throw(OSError("Falha sintética.")))
        with pytest.raises(storage.CheckpointStorageError):
            saved.save({"version": 2})
        assert saved.path.read_bytes() == original
        assert saved.path.stat().st_mode & 0o777 == 0o600
        assert saved.directory.stat().st_mode & 0o777 == 0o700
        assert not list(saved.directory.glob('.state-*'))


def test_lock_prevents_concurrent_access_and_releases_after_failure():
    with checkpoint(source()):
        with pytest.raises(storage.CheckpointBusyError):
            with checkpoint(source()):
                pytest.fail("A segunda execução deve aguardar nova tentativa autorizada.")
    with checkpoint(source()):
        pass


def test_http_storage_unavailable_prevents_paid_request(monkeypatch, tmp_path):
    root = tmp_path / "arquivo-em-vez-de-diretorio"
    root.write_text("Sintético.")
    monkeypatch.setattr(storage, "CHECKPOINTS_DIR", root)
    monkeypatch.setenv("INTERNAL_API_TOKEN", "token-ficticio")
    monkeypatch.setenv("OPENROUTER_API_KEY", "chave-ficticia")
    monkeypatch.setattr(v, "_request", lambda *_: pytest.fail("Falha de armazenamento deve preceder a chamada de IA."))
    text = source()
    result = TestClient(app).post('/v1/analyze-anvisa-v8', headers={'X-Internal-Token':'token-ficticio'}, json={
        'markdown':text,'page_count':1,'markdown_sha256':hashlib.sha256(text.encode()).hexdigest(),'source_filename':'sintetico.pdf'})
    assert result.status_code == 500 and 'ARMAZENAMENTO' in result.json()['detail']


def test_valid_result_arriving_after_deadline_is_saved_before_next_paid_call(monkeypatch):
    now = [0]
    calls = []
    monkeypatch.setattr(inc.time, "monotonic", lambda: now[0])

    def request(messages, *_):
        calls.append(request_data(messages)["paginas_alvo"])
        now[0] = 601
        return response(calls[-1], [record(1)])

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.AnvisaError, match="tempo total"):
        analyze(source(10))
    assert calls == [list(range(1, 6))]
    with checkpoint(source(10)) as saved:
        assert len(saved.load()["completed"]) == 1


def test_reserved_ids_must_belong_to_current_target_pages(monkeypatch):
    monkeypatch.setattr(v, "_request", lambda *_: response([1], [record()], partial=True, ids=[record()["id"], "ANV8-P2-RESERVADO"]))
    with pytest.raises(v.StructureValidationError) as failure:
        analyze(source())
    assert failure.value.diagnostic["motivo"] == "id_reservado_invalido"


def test_id_preservation_compares_json_types_exactly():
    before = dict(record(), ordem_documental=1)
    changed = dict(before, ordem_documental=True)
    with pytest.raises(v.StructureValidationError, match="id_preservado_alterado"):
        inc._merge([before], [changed])


def test_pdf_failure_can_retry_from_completed_checkpoint_without_repeating_ia(monkeypatch):
    monkeypatch.setenv("INTERNAL_API_TOKEN", "token-ficticio")
    monkeypatch.setenv("OPENROUTER_API_KEY", "chave-ficticia")
    calls = []

    def request(*_):
        calls.append(True)
        return response([1], [record()])

    monkeypatch.setattr(v, "_request", request)
    original = anvisa_pdf.render
    monkeypatch.setattr(anvisa_pdf, "render", lambda *_: (_ for _ in ()).throw(ValueError("Falha PDF sintética.")))
    text = source()
    payload = {'markdown':text,'page_count':1,'markdown_sha256':hashlib.sha256(text.encode()).hexdigest(),'source_filename':'sintetico.pdf'}
    client = TestClient(app)
    assert client.post('/v1/analyze-anvisa-v8',headers={'X-Internal-Token':'token-ficticio'},json=payload).status_code == 500
    monkeypatch.setattr(anvisa_pdf, "render", original)
    result = client.post('/v1/analyze-anvisa-v8',headers={'X-Internal-Token':'token-ficticio'},json=payload)
    assert result.status_code == 200 and len(calls) == 1
    assert result.json()['report_context']['analysis_checkpoint']['paginas_reutilizadas'] == [1]


def test_review_pending_does_not_block_saving_complete_siblings_or_require_false_page_success(monkeypatch):
    complete, draft = full_record(), full_record(suffix="B", pending=True)
    calls = []

    def request(messages, *_):
        data = request_data(messages)
        calls.append(data)
        assert data["continuidade"]["limite_eventos_resposta"] == 8
        if len(calls) == 1:
            assert data["continuidade"]["registros_preservados"] == []
            return response([1], [complete, draft])
        assert "ajuste_tecnico" not in data
        continuity = data["continuidade"]
        assert continuity["indice_registros_preservados"] == [ctx.record_index(r) for r in [complete]]
        assert continuity["registros_em_revisao"] == [draft]
        assert continuity["ids_para_revisar"] == [draft["id"]]
        assert continuity["limite_novos_eventos"] == 0
        with pytest.raises(v.StructureValidationError, match="conferencia_integridade_pendente"):
            v._validate_records([draft], [1], {1}, {1: source()})
        return response([1], [full_record(suffix="B")], ids=[complete["id"], draft["id"]])

    monkeypatch.setattr(v, "_request", request)
    found, coverage = analyze(source())
    assert found == [complete, full_record(suffix="B")] and len(calls) == 2
    with checkpoint(source()) as saved:
        state = saved.load()
    assert state["completed"][0]["review_history"] == [draft]
    assert coverage["paginas"][0]["estado"] == "analisada"


def test_failure_and_resume_preserve_complete_and_unfinished_review_separately(monkeypatch):
    complete, draft = full_record(), full_record(suffix="B", pending=True)
    calls = []

    def request(*_):
        calls.append(True)
        if len(calls) > 1:
            raise v.AnvisaError("IA: falha sintética durante a revisão.")
        return response([1], [complete, draft], partial=True)

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.AnvisaError):
        analyze(source())
    with checkpoint(source()) as saved:
        task = saved.load()["pending"][0]
    assert task["records"] == [complete] and task["drafts"] == [draft]

    def resume(messages, *_):
        data = request_data(messages)
        assert data["continuidade"]["indice_registros_preservados"] == [ctx.record_index(r) for r in [complete]]
        assert data["continuidade"]["registros_em_revisao"] == [draft]
        return response([1], [full_record(suffix="B")], ids=[complete["id"], draft["id"]])

    monkeypatch.setattr(v, "_request", resume)
    assert analyze(source())[0] == [complete, full_record(suffix="B")]


def test_review_can_add_source_data_but_keeps_evidence_and_previous_version(monkeypatch):
    draft = full_record(pending=True)
    revised = full_record()
    revised["campos_adicionais"] = {"dado_recuperado": {"estado": "confirmado", "valor": "Evento B1",
                                                       "evidencias": [{"pagina": 1, "trecho_literal": "Evento B1"}]}}
    responses = iter([response([1], [draft], partial=True), response([1], [revised])])
    monkeypatch.setattr(v, "_request", lambda *_: next(responses))
    assert analyze(source())[0] == [revised]
    with checkpoint(source()) as saved:
        assert saved.load()["completed"][0]["review_history"] == [draft]


@pytest.mark.parametrize("change", ["complete", "evidence", "drop_id"])
def test_review_cannot_rewrite_completed_event_remove_evidence_or_drop_id(monkeypatch, change):
    complete, draft = full_record(), full_record(suffix="B", pending=True)
    calls = []

    def request(*_):
        calls.append(True)
        if len(calls) == 1:
            return response([1], [complete, draft], partial=True)
        if change == "complete":
            return response([1], [dict(complete, justificativa_destino="Outro valor.")],
                            ids=[complete["id"], draft["id"]])
        if change == "evidence":
            changed = full_record(suffix="A")
            changed["id"] = draft["id"]
            return response([1], [changed], ids=[complete["id"], draft["id"]])
        return response([1], [], ids=[complete["id"]])

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.StructureValidationError):
        analyze(source())
    with checkpoint(source()) as saved:
        assert saved.load()["pending"][0]["drafts"] == [draft]
        assert saved.load()["pending"][0]["records"] == [complete]


def test_review_stall_stops_with_no_final_pdf(monkeypatch):
    monkeypatch.setenv("INTERNAL_API_TOKEN", "token-ficticio")
    monkeypatch.setenv("OPENROUTER_API_KEY", "chave-ficticia")
    monkeypatch.setattr(v, "_request", lambda *_: response([1], [full_record(pending=True)], partial=True))
    monkeypatch.setattr(anvisa_pdf, "render", lambda *_: pytest.fail("Revisão pendente não pode gerar PDF final."))
    text = source()
    result = TestClient(app).post('/v1/analyze-anvisa-v8', headers={'X-Internal-Token': 'token-ficticio'}, json={
        'markdown': text, 'page_count': 1, 'markdown_sha256': hashlib.sha256(text.encode()).hexdigest(), 'source_filename': 'sintetico.pdf'})
    assert result.status_code == 502 and 'sem progresso' in result.json()['detail']


def test_correction_receives_all_record_failures_and_the_small_group_limit(monkeypatch):
    calls = []
    broken = [record(suffix=s) for s in "AB"]
    for row in broken:
        row["evidencias"][0]["trecho_literal"] = "Trecho inexistente."

    def request(messages, *_):
        data = request_data(messages)
        calls.append(data)
        assert data["continuidade"]["limite_eventos_resposta"] == 8
        if len(calls) == 1:
            return response([1], broken)
        errors = data["diagnostico_validacao"]["falhas_registros"]
        assert len(errors) == 2
        assert errors[0]["campo"].startswith('/registros/0/')
        assert errors[1]["campo"].startswith('/registros/1/')
        return response([1], [record(suffix=s) for s in "AB"])

    monkeypatch.setattr(v, "_request", request)
    assert len(analyze(source())[0]) == 2


@pytest.mark.parametrize("damage", ["draft", "history"])
def test_semantically_corrupt_review_checkpoint_blocks_ia(monkeypatch, damage):
    calls = []

    def request(*_):
        calls.append(True)
        if len(calls) > 1:
            raise v.AnvisaError("IA: falha sintética.")
        return response([1], [full_record(pending=True)], partial=True)

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.AnvisaError):
        analyze(source())
    with checkpoint(source()) as saved:
        state = saved.load()
        task = state['pending'][0]
        if damage == 'draft':
            task['drafts'][0]['evidencias'][0]['trecho_literal'] = 'Ausente.'
        else:
            task['review_history'] = [full_record(suffix="B", pending=True)]
        saved.save(state)
    monkeypatch.setattr(v, '_request', lambda *_: pytest.fail('Não consumir IA com estado inválido.'))
    with pytest.raises(storage.CheckpointStorageError):
        analyze(source())


def legacy_checkpoint(text, scope='protocolo-sintetico'):
    count = text.count('## Página ')
    old = storage.AnalysisCheckpoint(migration.legacy_identity(hashlib.sha256(text.encode()).hexdigest(), count), scope)
    pages = {n: 'Texto sintético.' for n in range(1, count + 1)}
    pending = inc._tasks(list(range(6, count + 1)), pages)
    for task in pending:
        task.pop('drafts')
        task.pop('review_history')
        task.pop('context')
    state = {'schema': 1, 'completed': [{'targets': list(range(1, 6)), 'sent': list(range(1, 8)),
                                       'result': response(list(range(1, 6)), [record()])}], 'pending': pending}
    with old:
        old.save(state)
    return old, state


def test_explicit_migration_revalidates_preserves_old_state_and_is_idempotent(monkeypatch):
    text = source(10)
    old, state = legacy_checkpoint(text)
    before = old.path.read_bytes()
    result = migration.migrate(text, 'protocolo-sintetico', old.key)
    assert result['completed_pages'] == list(range(1, 6)) and result['status'] == 'migrado'
    assert old.path.read_bytes() == before
    with checkpoint(text) as current:
        converted = current.load()
    assert converted['completed'] == state['completed']
    assert converted['pending'][0]['drafts'] == []
    assert converted['migration']['source_key'] == old.key
    assert migration.migrate(text, 'protocolo-sintetico', old.key)['status'] == 'ja_migrado'

    def resume(messages, *_):
        data = request_data(messages)
        assert data['paginas_alvo'] == list(range(6, 11))
        return response(data['paginas_alvo'], [record(6)])

    monkeypatch.setattr(v, '_request', resume)
    assert analyze(text)[0] == [record(), record(6)]
    # Nova migração não pode apagar progresso posterior à primeira migração.
    assert migration.migrate(text, 'protocolo-sintetico', old.key)['completed_pages'] == list(range(1, 11))
    assert old.path.read_bytes() == before


@pytest.mark.parametrize('damage', ['digest', 'semantic', 'source', 'scope', 'version', 'destination'])
def test_migration_rejects_corruption_different_identity_or_overwrite(damage):
    text = source(10)
    old, state = legacy_checkpoint(text)
    scope = 'protocolo-sintetico'
    key = old.key
    if damage == 'digest':
        data = json.loads(old.path.read_bytes())
        data['state']['completed'][0]['result']['registros'][0]['justificativa'] = 'Outro valor.'
        old.path.write_text(json.dumps(data))
    elif damage == 'semantic':
        state['completed'][0]['result']['registros'][0]['evidencias'][0]['trecho_literal'] = 'Ausente.'
        with old:
            old.save(state)
    elif damage == 'source':
        text += 'Outra fonte.'
    elif damage == 'scope':
        scope = 'outro-protocolo'
    elif damage == 'version':
        wrong = dict(migration.legacy_identity(hashlib.sha256(text.encode()).hexdigest(), 10), implementation_sha256='a' * 64)
        with storage.AnalysisCheckpoint(wrong, scope) as other:
            other.save(state)
        key = other.key
    elif damage == 'destination':
        with checkpoint(text) as current:
            converted = copy.deepcopy(state)
            converted['schema'] = inc.PROTOCOL_VERSION
            converted['pending'][0].update(drafts=[], review_history=[])
            current.save(converted)
        before = current.path.read_bytes()
    with pytest.raises(storage.CheckpointStorageError):
        migration.migrate(text, scope, key)
    if damage == 'destination':
        assert current.path.read_bytes() == before


def test_migration_respects_old_checkpoint_lock():
    text = source(10)
    old, _ = legacy_checkpoint(text)
    with old:
        with pytest.raises(storage.CheckpointBusyError):
            migration.migrate(text, 'protocolo-sintetico', old.key)


@pytest.mark.parametrize('where', ['record', 'inventory'])
def test_reviewed_label_with_explicit_pending_work_cannot_close_analysis(monkeypatch, where):
    first = response([1], [full_record()])
    if where == 'record':
        first['registros'][0]['conferencia_integridade']['pendencias'] = ['Conferência inversa ainda não feita.']
    else:
        first['reconciliacao_anexos'][0]['pendencias'] = ['Conferir as unidades restantes.']
    calls = []

    def request(messages, *_):
        data = request_data(messages)
        calls.append(data)
        if len(calls) == 1:
            return copy.deepcopy(first)
        assert 'ajuste_tecnico' not in data
        if where == 'record':
            assert data['continuidade']['registros_em_revisao'] == first['registros']
            return response([1], [full_record()])
        assert data['continuidade']["indice_registros_preservados"] == [ctx.record_index(r) for r in first['registros']]
        return response([1], [], ids=[first['registros'][0]['id']])

    monkeypatch.setattr(v, '_request', request)
    assert analyze(source())[0] == [full_record()]
    assert len(calls) == 2
    with pytest.raises(v.StructureValidationError):
        v._validate_block(first, [1], {1}, {1: source()})


@pytest.mark.parametrize('review', [{'estado': [], 'pendencias': []}, {'estado': 'pendente', 'pendencias': 'Texto inválido.'}])
def test_draft_review_requires_a_valid_structure(review):
    row = full_record(pending=True)
    row['conferencia_integridade'] = review
    with pytest.raises(v.StructureValidationError):
        v._validate_records([row], [1], {1}, {1: source()}, allow_pending_review=True)


def context_source(count=14):
    return ''.join(f'## Página {n}\nEvento A{n}\nEvento B{n}\n' +
                   ('Trecho sintético "com aspas".\n' * 110) + f'Fim da página {n}.\n'
                   for n in range(1, count + 1))


def test_large_context_request_is_delivered_in_bounded_whole_page_windows(monkeypatch):
    monkeypatch.setattr(inc, 'MAX_TARGET_CHARS', 1000)
    monkeypatch.setattr(ctx, 'MAX_DATA_BYTES', 10000)
    calls = []
    seen = set()
    first_calls = []

    def request(messages, *_):
        data = request_data(messages)
        assert len(v._json(data)) <= ctx.MAX_DATA_BYTES
        assert ctx.INSTRUCTIONS in [m['content'] for m in messages]
        window = data['contexto_recuperado']['paginas_nesta_chamada']
        for n in window:
            assert f'Fim da página {n}.\n' in data['markdown_documental']
        calls.append(data)
        if data['paginas_alvo'] != [1]:
            assert seen == set(range(1, 15)), 'Não fechar o lote antes de entregar o contexto pedido.'
            return response(data['paginas_alvo'])
        seen.update(window)
        first_calls.append(data)
        if len(first_calls) == 1:
            return response([1], [record()], partial=True)
        if len(first_calls) == 2:
            return {'contexto_necessario': list(range(2, 15))}
        # Mesmo uma declaração prematura de sucesso não elimina páginas da fila.
        return response([1], [], ids=[record()['id']])

    monkeypatch.setattr(v, '_request', request)
    found, coverage = analyze(context_source())
    assert found == [record()] and len(coverage['paginas']) == 14
    assert max(len(d['contexto_recuperado']['paginas_nesta_chamada']) for d in first_calls) < 14
    with checkpoint(context_source()) as saved:
        state = saved.load()
    context = state['completed'][0]['context']
    assert context['requested'] == context['delivered'] == list(range(1, 15))
    assert context['review_required'] is False


def test_context_queue_survives_failure_and_resume_without_resending_delivered_context(monkeypatch):
    monkeypatch.setattr(inc, 'MAX_TARGET_CHARS', 1000)
    monkeypatch.setattr(ctx, 'MAX_DATA_BYTES', 10000)
    calls = []

    def request(messages, *_):
        data = request_data(messages)
        calls.append(data)
        if len(calls) == 1:
            return response([1], [record()], partial=True)
        if len(calls) == 2:
            return {'contexto_necessario': list(range(2, 15))}
        if len(calls) == 4:
            raise v.AnvisaError('IA: falha sintética após uma janela de contexto.')
        return response([1], [], ids=[record()['id']])

    monkeypatch.setattr(v, '_request', request)
    with pytest.raises(v.AnvisaError, match='falha sintética'):
        analyze(context_source())
    with checkpoint(context_source()) as saved:
        task = saved.load()['pending'][0]
    delivered = set(task['context']['delivered'])
    assert ctx.pending(task['context']) and task['records'] == [record()]
    resumed_first = []

    def resume(messages, *_):
        data = request_data(messages)
        assert len(v._json(data)) <= ctx.MAX_DATA_BYTES
        if data['paginas_alvo'] == [1]:
            window = set(data['contexto_recuperado']['paginas_nesta_chamada'])
            if not resumed_first:
                resumed_first.append(window)
                assert not (window - {1}) & delivered
            return response([1], [], ids=[record()['id']])
        return response(data['paginas_alvo'])

    monkeypatch.setattr(v, '_request', resume)
    assert analyze(context_source())[0] == [record()]


def test_local_literal_search_scans_full_source_and_returns_only_relevant_extra_pages(monkeypatch):
    text = source(12).replace('Evento A3', 'Evento A3\n25351.000001/2026-00').replace('Evento A10', 'Evento A10\n25351.000001/2026-00')
    first_calls = []

    def request(messages, *_):
        data = request_data(messages)
        if data['paginas_alvo'] != list(range(1, 6)):
            return response(data['paginas_alvo'])
        first_calls.append(data)
        if len(first_calls) == 1:
            return {'buscas_necessarias': ['25351.000001/2026-00', 'Identificador ausente']}
        context = data['contexto_recuperado']
        assert context['buscas_locais'] == [
            {'termo_literal': '25351.000001/2026-00', 'metodo': 'substring_literal_exata', 'paginas_examinadas': 12, 'paginas_com_ocorrencias': [3, 10]},
            {'termo_literal': 'Identificador ausente', 'metodo': 'substring_literal_exata', 'paginas_examinadas': 12, 'paginas_com_ocorrencias': []}]
        assert 10 in context['paginas_nesta_chamada'] and 8 not in context['paginas_nesta_chamada'] and 12 not in context['paginas_nesta_chamada']
        return response(data['paginas_alvo'], [record()])

    monkeypatch.setattr(v, '_request', request)
    assert analyze(text)[0] == [record()]
    assert len(first_calls) == 2


def test_identifiers_in_pending_reviews_trigger_local_search_before_next_call(monkeypatch):
    term = '25351.000001/2026-00'
    text = source(20).replace('Evento A1\n', 'Evento A1\n' + term + '\n').replace('Evento A18\n', 'Evento A18\n' + term + '\n')
    draft = full_record(pending=True)
    draft['processos'] = [{'estado': 'confirmado', 'valor': term, 'evidencias': [{'pagina': 1, 'trecho_literal': term}]}]
    closed = copy.deepcopy(draft)
    closed['conferencia_integridade'] = {'estado': 'revisada', 'pendencias': []}
    calls = []

    def request(messages, *_):
        data = request_data(messages)
        if data['paginas_alvo'] != list(range(1, 6)):
            return response(data['paginas_alvo'])
        calls.append(data)
        if len(calls) == 1:
            return response(data['paginas_alvo'], [draft], partial=True)
        assert data['contexto_recuperado']['buscas_locais'][0]['paginas_com_ocorrencias'] == [1, 18]
        assert 18 in data['contexto_recuperado']['paginas_nesta_chamada']
        assert 15 not in data['contexto_recuperado']['paginas_nesta_chamada']
        return response(data['paginas_alvo'], [closed])

    monkeypatch.setattr(v, '_request', request)
    assert analyze(text)[0] == [closed]


@pytest.mark.parametrize('bad', [{'contexto_necessario': [True]}, {'contexto_necessario': [999]},
                                 {'buscas_necessarias': ['']}, {'buscas_necessarias': ['x' * 257]}])
def test_invalid_context_request_preserves_last_accepted_group(monkeypatch, bad):
    calls = []

    def request(*_):
        calls.append(True)
        return response([1], [record()], partial=True) if len(calls) == 1 else bad

    monkeypatch.setattr(v, '_request', request)
    with pytest.raises(v.AnvisaError):
        analyze(source())
    with checkpoint(source()) as saved:
        assert saved.load()['pending'][0]['records'] == [record()]


@pytest.mark.parametrize('damage', ['requested', 'delivered', 'searches', 'review_required'])
def test_corrupt_context_queue_blocks_ia(monkeypatch, damage):
    calls = []

    def request(*_):
        calls.append(True)
        if len(calls) > 1:
            raise v.AnvisaError('IA: falha sintética.')
        return response([1], [record()], partial=True)

    monkeypatch.setattr(v, '_request', request)
    with pytest.raises(v.AnvisaError):
        analyze(source())
    with checkpoint(source()) as saved:
        state = saved.load()
        context = state['pending'][0]['context']
        context[damage] = {'requested': [999], 'delivered': [999], 'searches': [{'term': 'Inexistente', 'matches': [1]}], 'review_required': 'sim'}[damage]
        saved.save(state)
    monkeypatch.setattr(v, '_request', lambda *_: pytest.fail('Fila inválida não pode consumir IA.'))
    with pytest.raises(storage.CheckpointStorageError):
        analyze(source())


def test_budget_includes_utf8_correction_and_prior_response_without_cutting_pages(monkeypatch):
    pages = {n: ('Conteúdo "literal" áéç\n' * 1000) for n in range(1, 20)}
    task = inc._tasks([1], pages)[0]
    task['context']['requested'] = list(pages)
    extra = {'resposta_anterior': {'valor': '漢字' * 40000}, 'diagnostico_validacao': {'motivo': 'Caso sintético.'}}
    data, window = ctx.build(task, pages, 4, extra)
    assert len(v._json(data)) <= ctx.MAX_DATA_BYTES and len(window) < len(pages)
    assert data['resposta_anterior'] == extra['resposta_anterior']
    for n in window:
        assert f'## Página {n}' + pages[n] in data['markdown_documental']
    monkeypatch.setattr(ctx, 'MAX_DATA_BYTES', 100)
    with pytest.raises(v.AnvisaOutputLimit):
        ctx.build(task, pages, 4, extra)


def test_correction_keeps_whole_pages_cited_by_rejected_group():
    pages = {n: f'\nEvento A{n}\nFim da página {n}.\n' for n in range(1, 21)}
    task = inc._tasks([10], pages)[0]
    rejected = record(10)
    rejected['evidencias'] = [{'pagina': 1, 'trecho_literal': 'Trecho incorreto.'}]
    data, window = ctx.build(task, pages, extra={'resposta_anterior': {'registros': [rejected]}})
    assert window == {1, 8, 9, 10, 11, 12}
    assert '## Página 1' + pages[1] in data['markdown_documental']


def test_output_limit_after_context_request_keeps_queue_before_any_record(monkeypatch):
    calls = []

    def request(messages, *_):
        calls.append(request_data(messages))
        if len(calls) == 1:
            return {'contexto_necessario': list(range(1, 21))}
        raise v.AnvisaOutputLimit('IA: limite sintético após solicitar contexto.')

    monkeypatch.setattr(v, '_request', request)
    with pytest.raises(v.AnvisaOutputLimit, match='limite sintético'):
        analyze(source(20))
    with checkpoint(source(20)) as saved:
        task = saved.load()['pending'][0]
    assert len(calls) == 2 and task['targets'] == list(range(1, 6))
    assert task['context']['requested'] == list(range(1, 21))
    assert ctx.pending(task['context']) and task['context']['review_required'] is True


def test_resume_replays_context_window_after_rejected_response(monkeypatch):
    calls = []
    rejected = record()
    rejected['evidencias'] = [{'pagina': 10, 'trecho_literal': 'Literal que não existe.'}]

    def request(messages, *_):
        data = request_data(messages)
        calls.append(data)
        if len(calls) == 1:
            return {'contexto_necessario': [10]}
        assert 10 in data['contexto_recuperado']['paginas_nesta_chamada']
        return response(list(range(1, 6)), [rejected])

    monkeypatch.setattr(v, '_request', request)
    with pytest.raises(v.AnvisaError):
        analyze(source(12))
    with checkpoint(source(12)) as saved:
        assert 10 in saved.load()['pending'][0]['context']['last_window']
    resumed = []

    def resume(messages, *_):
        data = request_data(messages)
        if not resumed:
            assert 10 in data['contexto_recuperado']['paginas_nesta_chamada']
        resumed.append(data)
        return response(data['paginas_alvo'])

    monkeypatch.setattr(v, '_request', resume)
    analyze(source(12))


def test_v2_migration_preserves_drafts_and_turns_poisoned_context_into_pending_queue(monkeypatch):
    text = context_source(20)
    markers = list(v.PAGE.finditer(text))
    pages = {i+1: text[m.end():markers[i+1].start() if i+1 < len(markers) else len(text)] for i,m in enumerate(markers)}
    pending = [task for start in range(6, 21, 5) for task in inc._tasks(list(range(start, start+5)), pages)]
    for task in pending:
        task.pop('context')
    pending[0].update(sent=list(pages), records=[full_record(6)], drafts=[full_record(6, 'B', pending=True)])
    pending[0]['continuation'] = {k: value for k, value in response(list(range(6, 11)), pending[0]['records'] + pending[0]['drafts'], partial=True).items() if k != 'registros'}
    state = {'schema': 2, 'completed': [{'targets': list(range(1, 6)), 'sent': list(range(1, 8)),
                                      'result': response(list(range(1, 6)), [record()])}], 'pending': pending}
    old = storage.AnalysisCheckpoint(migration.legacy_identity(hashlib.sha256(text.encode()).hexdigest(), 20, 2), 'protocolo-sintetico')
    with old:
        old.save(state)
    before = old.path.read_bytes()
    monkeypatch.setattr(ctx, 'MAX_DATA_BYTES', 60000)
    migrated = migration.migrate(text, 'protocolo-sintetico', old.key)
    assert migrated['completed_pages'] == list(range(1, 6)) and old.path.read_bytes() == before
    with checkpoint(text) as current:
        converted = current.load()
    task = converted['pending'][0]
    assert task['records'] == pending[0]['records'] and task['drafts'] == pending[0]['drafts']
    assert task['context']['requested'] == list(pages) and task['context']['delivered'] == []
    assert len(v._json(ctx.data(task, pages, set(pages), 4, {}))) > 60000
    packets = []

    def resume(messages, *_):
        data = request_data(messages)
        packets.append(data)
        assert data['paginas_alvo'][0] >= 6 and len(v._json(data)) <= ctx.MAX_DATA_BYTES
        if data['paginas_alvo'] == list(range(6, 11)):
            return response(data['paginas_alvo'], [full_record(6, 'B')], ids=[full_record(6)['id'], full_record(6, 'B')['id']])
        return response(data['paginas_alvo'])

    monkeypatch.setattr(v, '_request', resume)
    assert analyze(text)[0] == [record(), full_record(6), full_record(6, 'B')]
    assert old.path.read_bytes() == before and len(packets) > 3


def test_more_than_three_local_search_groups_preserve_event_progress(monkeypatch):
    text = source(25)
    rows = [record(n) for n in range(1, 6)] + [record(1, 'B')]
    calls = []

    def request(messages, *_):
        data = request_data(messages)
        assert len(v._json(data)) <= ctx.MAX_DATA_BYTES and 'ajuste_tecnico' not in data
        if data['paginas_alvo'] != list(range(1, 6)):
            return response(data['paginas_alvo'])
        calls.append(data)
        index = (len(calls) - 1) // 2
        assert data['continuidade']["indice_registros_preservados"] == [ctx.record_index(r) for r in rows[:index]]
        if len(calls) % 2:
            return {'buscas_necessarias': [f'Evento A{index + 10}']}
        assert data['contexto_recuperado']['buscas_locais'][-1]['paginas_com_ocorrencias'] == [index + 10]
        return response(data['paginas_alvo'], [rows[index]], partial=index < 5,
                        ids=[row['id'] for row in rows[:index + 1]])

    monkeypatch.setattr(v, '_request', request)
    assert analyze(text)[0] == rows
    assert len(calls) == 12
    with checkpoint(text) as saved:
        context = saved.load()['completed'][0]['context']
    assert len(context['searches']) == 6 and not ctx.pending(context)


def test_new_local_searches_do_not_spend_explicit_page_expansions(monkeypatch):
    calls = []

    def request(messages, *_):
        data = request_data(messages)
        if data['paginas_alvo'] != list(range(1, 6)):
            return response(data['paginas_alvo'])
        calls.append(data)
        if len(calls) <= 5:
            return {'buscas_necessarias': [f'Evento A{len(calls) + 10}']}
        return response(data['paginas_alvo'], [record()])

    monkeypatch.setattr(v, '_request', request)
    assert analyze(source(25))[0] == [record()]
    assert len(calls) == 6


def test_page_expansion_budget_reopens_after_validated_group_progress(monkeypatch):
    rows = [record(1, suffix) for suffix in 'ABC']
    actions = [response(list(range(1, 6)), [rows[0]], partial=True),
               *({'contexto_necessario': [n]} for n in [8, 10, 12]),
               response(list(range(1, 6)), [rows[1]], partial=True, ids=[row['id'] for row in rows[:2]]),
               *({'contexto_necessario': [n]} for n in [14, 16, 18]),
               response(list(range(1, 6)), [rows[2]], ids=[row['id'] for row in rows])]
    calls = []

    def request(messages, *_):
        data = request_data(messages)
        assert 'ajuste_tecnico' not in data
        if data['paginas_alvo'] != list(range(1, 6)):
            return response(data['paginas_alvo'])
        calls.append(data)
        return copy.deepcopy(actions[len(calls) - 1])

    monkeypatch.setattr(v, '_request', request)
    assert analyze(source(20))[0] == rows
    assert len(calls) == 9


def test_fourth_expansion_without_group_progress_is_saved_before_stop_and_resumes(monkeypatch):
    text = source(20)
    targets = list(range(1, 6))
    actions = [response(targets, [record()], partial=True),
               *({'contexto_necessario': [n]} for n in [8, 10, 12]),
               response(targets, [], partial=True, ids=[record()['id']]),
               {'contexto_necessario': [14]}]
    calls = []

    def request(messages, *_):
        calls.append(request_data(messages))
        return copy.deepcopy(actions[len(calls) - 1])

    monkeypatch.setattr(v, '_request', request)
    with pytest.raises(v.AnvisaError, match='ampliações de páginas sem avanço'):
        analyze(text)
    with checkpoint(text) as saved:
        task = saved.load()['pending'][0]
    assert task['records'] == [record()] and 14 in ctx.pending(task['context'])
    assert len(calls) == 6

    def resume(messages, *_):
        data = request_data(messages)
        if data['paginas_alvo'] == targets:
            assert 14 in data['contexto_recuperado']['paginas_nesta_chamada']
            assert data['continuidade']["indice_registros_preservados"] == [ctx.record_index(r) for r in [record()]]
            return response(targets, [], ids=[record()['id']])
        return response(data['paginas_alvo'])

    monkeypatch.setattr(v, '_request', resume)
    assert analyze(text)[0] == [record()]


def test_cached_search_repetition_without_pending_pages_stops(monkeypatch):
    calls = []

    def request(*_):
        calls.append(True)
        return {'buscas_necessarias': ['Evento A1']}

    monkeypatch.setattr(v, '_request', request)
    with pytest.raises(v.AnvisaError, match='sem nova busca ou página pendente'):
        analyze(source())
    assert len(calls) == 2


def test_novel_search_only_loop_keeps_search_budget_across_automatic_windows(monkeypatch):
    monkeypatch.setattr(inc, 'MAX_CONTINUATIONS', 3)
    monkeypatch.setattr(ctx, 'MAX_SEARCHES', 6)
    calls = []

    def request(*_):
        calls.append(True)
        return {'buscas_necessarias': [f'Termo sintético ausente {len(calls)}']}

    monkeypatch.setattr(v, '_request', request)
    with pytest.raises(v.AnvisaError, match='limite de buscas locais'):
        analyze(source())
    assert len(calls) == 7
    with checkpoint(source()) as saved:
        assert len(saved.load()['pending'][0]['context']['searches']) == 6


@pytest.mark.parametrize('corrupt', [False, True])
def test_v3_migration_preserves_delivered_context_searches_drafts_and_history(corrupt):
    text = source(10)
    pages = {n: f'\nEvento A{n}\nEvento B{n}\nEvento C{n}\n' for n in range(1, 11)}
    task = inc._tasks(list(range(6, 11)), pages)[0]
    task.update(records=[full_record(6)], drafts=[full_record(6, 'B', pending=True)])
    task['continuation'] = {k: value for k, value in response(task['targets'], task['records'] + task['drafts'], partial=True).items() if k != 'registros'}
    task['context'] = {'requested': list(range(1, 11)), 'delivered': list(range(4, 11)),
                       'last_window': list(range(4, 11)), 'review_required': True,
                       'searches': [{'term': 'Evento B1', 'matches': [1, 10]}]}
    if corrupt:
        task['context']['delivered'].append(999)
    state = {'schema': 3, 'completed': [{'targets': list(range(1, 6)), 'sent': list(range(1, 8)),
                                       'result': response(list(range(1, 6)), [record()])}], 'pending': [task]}
    old = storage.AnalysisCheckpoint(migration.legacy_identity(hashlib.sha256(text.encode()).hexdigest(), 10, 3), 'protocolo-sintetico')
    with old:
        old.save(state)
    before = old.path.read_bytes()
    if corrupt:
        with pytest.raises(storage.CheckpointStorageError):
            migration.migrate(text, 'protocolo-sintetico', old.key)
        assert old.path.read_bytes() == before
        return
    result = migration.migrate(text, 'protocolo-sintetico', old.key)
    assert result['completed_pages'] == list(range(1, 6)) and old.path.read_bytes() == before
    with checkpoint(text) as current:
        converted = current.load()
    assert converted['completed'] == state['completed'] and converted['pending'] == state['pending']
    assert converted['migration']['source_key'] == old.key
    assert migration.migrate(text, 'protocolo-sintetico', old.key)['status'] == 'ja_migrado'
