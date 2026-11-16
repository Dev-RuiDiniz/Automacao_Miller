"""Regressão do crescimento de fichas completas em lotes ainda pendentes."""

import copy
import base64
import hashlib
import io
import json
import zipfile

import pytest
from fastapi.testclient import TestClient

from infra.report_renderer import anvisa_v8 as v, context_window as ctx, incremental as inc, transport
from infra.report_renderer import analysis_checkpoint as storage, migrate_checkpoint as migration
from infra.report_renderer.app import app
from tests.report_renderer.test_incremental import checkpoint, analyze, full_record, record, response, request_data


def dense_case():
    rows = [full_record(6, f"E{i}") for i in range(70)]
    for row in rows:
        row["justificativa_destino"] = "Justificativa sintética preservada integralmente. " * 200
    pages = {n: f"\nEvento A{n}\nEvento B{n}\n" for n in range(1, 11)}
    pages[6] += "".join(f"Evento E{i}6\n" for i in range(70))
    text = "".join(f"## Página {n}{body}" for n, body in pages.items())
    task = inc._tasks(list(range(6, 11)), pages)[0]
    task["records"] = rows
    task["continuation"] = {k: value for k, value in response(task["targets"], rows, partial=True).items() if k != "registros"}
    state = {"schema": inc.PROTOCOL_VERSION,
             "completed": [{"targets": list(range(1, 6)), "sent": list(range(1, 8)),
                            "result": response(list(range(1, 6)), [record()])}], "pending": [task]}
    inc._validated_state(state, pages)
    return text, pages, state


def test_oversized_completed_cards_use_index_without_mutating_checkpoint_or_cutting_pages():
    _, pages, state = dense_case()
    before = storage.encode(state)
    task = state["pending"][0]
    assert len(v._json(ctx.data(task, pages, set(), 4, {}))) > ctx.MAX_DATA_BYTES
    data, window = ctx.build(task, pages)
    assert len(v._json(data)) <= ctx.MAX_DATA_BYTES
    assert storage.encode(state) == before
    assert data["continuidade"]["registros_preservados"] == []
    index = data["continuidade"]["indice_registros_preservados"]
    assert [row["id"] for row in index] == [row["id"] for row in task["records"]]
    for reference, original in zip(index, task["records"]):
        assert reference["sha256"] == hashlib.sha256(storage.encode(original)).hexdigest()
        assert reference["paginas_origem"] == original["paginas_origem"]
        assert {"campo": "/ato", "valor": original["ato"]["valor"]} in reference["referencias_confirmadas"]
    assert data["markdown_documental"] == "".join(f"## Página {n}{pages[n]}" for n in sorted(window))
    assert set(task["targets"]) <= window


def test_indexed_analysis_saves_new_group_resumes_and_reuses_completed_lots(monkeypatch):
    text, _, state = dense_case()
    rows = state["pending"][0]["records"]
    with checkpoint(text) as saved:
        saved.save(state)
    calls = []

    def request(messages, *_):
        data = request_data(messages)
        calls.append(data)
        assert data["paginas_alvo"] == list(range(6, 11))
        assert data["continuidade"]["modo_registros_preservados"] == "indice"
        assert len(v._json(data)) <= ctx.MAX_DATA_BYTES
        if len(calls) == 2:
            raise v.AnvisaError("IA: interrupção sintética após novo grupo salvo.")
        return response(data["paginas_alvo"], [full_record(6)], partial=True,
                        ids=[r["id"] for r in rows] + [full_record(6)["id"]])

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.AnvisaError, match="interrupção sintética"):
        analyze(text)
    with checkpoint(text) as saved:
        partial = saved.load()
    assert partial["completed"] == state["completed"]
    assert partial["pending"][0]["records"] == rows + [full_record(6)]

    def resume(messages, *_):
        data = request_data(messages)
        assert len(data["continuidade"]["indice_registros_preservados"]) == 71
        return response(data["paginas_alvo"], ids=[r["id"] for r in rows] + [full_record(6)["id"]])

    monkeypatch.setattr(v, "_request", resume)
    found, coverage = analyze(text)
    assert found == [record()] + rows + [full_record(6)]
    assert coverage["processamento_incremental"]["paginas_reutilizadas"] == list(range(1, 6))
    monkeypatch.setattr(v, "_request", lambda *_: pytest.fail("Estado concluído não deve repetir IA."))
    assert analyze(text)[0] == found


@pytest.mark.parametrize("violation", ["changed", "duplicate", "missing_id"])
def test_index_does_not_weaken_immutable_records_duplicates_or_inventory(monkeypatch, violation):
    text, _, state = dense_case()
    rows = state["pending"][0]["records"]
    with checkpoint(text) as saved:
        saved.save(state)
    ids = [r["id"] for r in rows]
    changed = copy.deepcopy(rows[0])
    if violation == "changed":
        changed["justificativa_destino"] = "Alteração indevida de ficha concluída."
        result = response(list(range(6, 11)), [changed], ids=ids)
    elif violation == "duplicate":
        changed["id"] = "ANV8-P6-CLONE"
        result = response(list(range(6, 11)), [changed], ids=ids + [changed["id"]])
    else:
        result = response(list(range(6, 11)), ids=ids[1:])
    calls = []

    def request(messages, *_):
        data = request_data(messages)
        calls.append(data)
        assert data["continuidade"]["modo_registros_preservados"] == "indice"
        assert len(v._json(data)) <= ctx.MAX_DATA_BYTES
        if len(calls) == 2:
            assert data["resposta_anterior"] == result
            assert data["diagnostico_validacao"]
        return copy.deepcopy(result)

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.StructureValidationError):
        analyze(text)
    assert len(calls) == 2
    with checkpoint(text) as saved:
        preserved = saved.load()
    assert preserved["pending"][0]["records"] == rows
    assert preserved["completed"] == state["completed"]


def test_index_keeps_drafts_rejected_response_evidence_pages_and_pending_context_complete():
    _, pages, state = dense_case()
    task = state["pending"][0]
    draft = full_record(6, pending=True)
    draft["paginas_origem"].append(2)
    draft["evidencias"].append({"pagina": 2, "trecho_literal": "Evento A2"})
    task["drafts"] = [draft]
    task["review_history"] = [copy.deepcopy(draft)]
    task["context"]["requested"] = [1]
    task["context"]["review_required"] = True
    rejected = response(task["targets"], [full_record(4)])
    extra = {"resposta_anterior": rejected, "diagnostico_validacao": {"motivo": "Falha sintética."}}
    before = storage.encode(task)
    data, window = ctx.build(task, pages, extra=extra)
    assert len(v._json(data)) <= ctx.MAX_DATA_BYTES
    assert {1, 2, 4, *task["targets"]} <= window
    data = transport.expand(data, data.get("evidencias_compartilhadas", {}))
    assert data["continuidade"]["registros_em_revisao"] == [draft]
    assert data["continuidade"]["ids_para_revisar"] == [draft["id"]]
    assert data["continuidade"]["limite_novos_eventos"] == 0
    assert data["resposta_anterior"] == rejected and data["diagnostico_validacao"] == extra["diagnostico_validacao"]
    assert storage.encode(task) == before and ctx.pending(task["context"]) == {1}


def test_index_does_not_hide_mandatory_content_that_still_exceeds_budget(monkeypatch):
    _, pages, state = dense_case()
    task = state["pending"][0]
    task["drafts"] = [full_record(6, pending=True)]
    task["drafts"][0]["justificativa_destino"] = "Texto sintético em revisão. " * 10000
    monkeypatch.setattr(ctx, "MAX_DATA_BYTES", 10000)
    before = storage.encode(task)
    with pytest.raises(v.AnvisaOutputLimit, match="continuidade obrigatória"):
        ctx.build(task, pages)
    assert storage.encode(task) == before


def test_explicit_migration_of_oversized_previous_implementation_is_lossless_and_idempotent():
    text, pages, state = dense_case()
    old = storage.AnalysisCheckpoint(migration.legacy_identity(hashlib.sha256(text.encode()).hexdigest(), 10, 4), "protocolo-sintetico")
    with old:
        old.save(state)
    original = old.path.read_bytes()
    result = migration.migrate(text, "protocolo-sintetico", old.key)
    assert result["status"] == "migrado" and old.path.read_bytes() == original
    with checkpoint(text) as saved:
        migrated = saved.load()
    assert migrated["completed"] == state["completed"] and migrated["pending"] == state["pending"]
    assert len(v._json(ctx.build(migrated["pending"][0], pages)[0])) <= ctx.MAX_DATA_BYTES
    assert migration.migrate(text, "protocolo-sintetico", old.key)["status"] == "ja_migrado"
    assert old.path.read_bytes() == original


def test_http_report_bundle_contains_complete_cards_after_indexed_resume(monkeypatch):
    text, _, state = dense_case()
    rows = state["pending"][0]["records"]
    with checkpoint(text) as saved:
        saved.save(state)
    monkeypatch.setenv("INTERNAL_API_TOKEN", "token-ficticio")
    monkeypatch.setenv("OPENROUTER_API_KEY", "chave-ficticia")
    calls = []

    def request(messages, *_):
        data = request_data(messages)
        calls.append(data)
        assert data["continuidade"]["modo_registros_preservados"] == "indice"
        assert len(v._json(data)) <= ctx.MAX_DATA_BYTES
        return response(data["paginas_alvo"], ids=[r["id"] for r in rows])

    monkeypatch.setattr(v, "_request", request)
    result = TestClient(app).post("/v1/analyze-anvisa-v8", headers={"X-Internal-Token": "token-ficticio"}, json={
        "markdown": text, "page_count": 10, "markdown_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "source_filename": "sintetico.pdf", "diagnostic_context": {
            "submission_id": "protocolo-sintetico", "attempt_number": 1, "execution_id": "execucao-sintetica"}})
    assert result.status_code == 200, result.json().get("detail")
    body = result.json()
    assert len(calls) == 1 and base64.b64decode(body["report_pdf_base64"]).startswith(b"%PDF-")
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(body["bundle_base64"]))) as archive:
        found = [json.loads(line) for line in archive.read("dados_anvisa_v8.jsonl").splitlines()]
    assert found == [record()] + rows
