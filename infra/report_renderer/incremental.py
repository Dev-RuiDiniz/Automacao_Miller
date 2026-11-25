"""Orquestração V8 em lotes e grupos de eventos completos, com retomada privada."""

from __future__ import annotations

import copy
import hashlib
import time
from pathlib import Path

from . import anvisa_v8 as v
from .analysis_checkpoint import CheckpointStorageError, encode
from . import context_window as ctx
from . import transport, parallel_batches as parallel, adaptive_groups as adaptive

PROTOCOL_VERSION = 3
MAX_TARGET_CHARS = 32000
MAX_CONTINUATIONS = 32  # Chamadas por janela técnica; o lote continua pelo checkpoint.
TRANSPORT_RETRY_DELAYS = (5, 15)
GROUP_SIZE = 8
MAX_PARALLEL_BATCHES = 2
MAX_PAGE_EXPANSIONS = 3
CONTINUATION = """Análise incremental desde a primeira chamada, com dados anteriores não confiáveis.
registros_preservados contém eventos já conferidos mecanicamente. Preserve seus IDs, conteúdo
e evidências; não os recrie, renumere, substitua ou apague. Na lista registros devolva somente
um grupo de até limite_eventos_resposta eventos, entre novos e revisões. Esse limite vale
também para a primeira resposta e para correções. Se repetir um ID já concluído,
seu objeto deve ser idêntico ao preservado. Não divida produto, petição, célula ou evento.
registros_em_revisao contém fichas ainda não concluídas, separadas das preservadas. Quando
houver fichas em revisão, priorize ids_para_revisar e não extraia novos eventos nessa chamada.
Conclua a conferência inversa de cada ficha contra a fonte antes de avançar. Preserve seus
IDs e evidências literais já recuperadas. Acrescente dados fundamentados e corrija a ficha
quando a releitura exigir; o aplicativo guarda as versões anteriores em histórico privado.
Não repita fichas em revisão fora do grupo solicitado; elas já permanecem guardadas.
Se ainda não puder concluir uma ficha, mantenha conferencia_integridade pendente com os
motivos reais. Não declare revisão feita sem executá-la. Solicite contexto_necessario para
páginas reais faltantes; pesquisar o documento integral não exige afirmar acesso a páginas
que não recebeu. Não transforme ausência de pesquisa em ausência documental.
Reveja as páginas-alvo e suas continuações na fonte, recuperando contexto quando necessário.
Devolva paginas com a cobertura acumulada dos alvos e reconciliacao_anexos acumulada deste
lote, incluindo os IDs preservados, em revisão e novos. Unidades ainda não processadas permanecem
pendentes; seus IDs reservados só podem aparecer em blocos pendentes do inventário. Não
inclua unidades que começam fora dos alvos. Se o lote foi reduzido, refaça o inventário para
esse recorte sem perder eventos preservados. Não marque página ou inventário como revisado
até terminar suas unidades. Informe impedimento somente se o lote permanecer parcial.
Uma ficha ou inventário com pendencias não está concluído, mesmo que o estado recebido
diga revisada. Resolva as pendências e confira a fonte; não apague notas só para fechar.
Mesmo sem novos eventos, confirme a revisão do restante da fonte antes de fechar o lote.
"""


def identity(source_hash, page_count):
    instructions = v.TRANSPORT + v.CORRECTION_INSTRUCTIONS + CONTINUATION + ctx.INSTRUCTIONS + transport.INSTRUCTIONS + adaptive.INSTRUCTIONS
    return {"schema": PROTOCOL_VERSION, "source_sha256": source_hash, "pages": page_count,
            "model": v.MODEL, "prompt_sha256": v.PROMPT_HASH,
            "instructions_sha256": hashlib.sha256(instructions.encode()).hexdigest(),
            "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes() + Path(v.__file__).read_bytes()
                                                        + Path(ctx.__file__).read_bytes() + Path(transport.__file__).read_bytes()
                                                        + Path(parallel.__file__).read_bytes() + Path(adaptive.__file__).read_bytes()).hexdigest()}


def _partial(result):
    return (bool(result.get("impedimento"))
            or any(row["estado"] == "pendente" for row in result["paginas"])
            or any(block["estado_revisao"] == "pendente" or block.get("pendencias") for block in result["reconciliacao_anexos"])
            or any(_needs_review(record) for record in result["registros"]))


def _needs_review(record):
    return (record["destino"] in {"incluido", "pendente"}
            and (record.get("conferencia_integridade", {}).get("estado") == "pendente"
                 or bool(record.get("conferencia_integridade", {}).get("pendencias"))))


def _tasks(targets, pages, records=()):
    if len(targets) > 1 and sum(len(pages[n]) for n in targets) > MAX_TARGET_CHARS:
        middle = len(targets) // 2
        return _tasks(targets[:middle], pages, records) + _tasks(targets[middle:], pages, records)
    kept = [r for r in records if int(r["id"].split("-")[1][1:]) in targets]
    sent = set(range(max(1, targets[0] - 2), min(targets[-1] + 2, len(pages)) + 1))
    sent.update(n for r in kept for n in r["paginas_origem"])
    return [{"targets": targets, "sent": sorted(sent), "records": kept, "drafts": [],
             "review_history": [], "continuation": None, "context": ctx.empty()}]


def _merge(previous, incoming):
    records = list(previous)
    by_id = {r["id"]: r for r in records}
    fingerprint = lambda r: encode({key: value for key, value in r.items() if key != "id"})
    by_content = {fingerprint(r): r["id"] for r in records}
    for index, record in enumerate(incoming):
        rid = record["id"]
        if rid in by_id:
            if encode(record) != encode(by_id[rid]):
                raise v.StructureValidationError("id_preservado_alterado", f"/registros/{index}", record,
                                                  "Preserve o evento e suas evidências exatamente como recebidos em registros_preservados.", rid)
            continue
        content = fingerprint(record)
        if content in by_content:
            raise v.StructureValidationError("evento_duplicado_com_outro_id", f"/registros/{index}/id", rid,
                                              {"id_preservado": by_content[content]}, rid)
        records.append(record)
        by_id[rid], by_content[content] = record, rid
    return records


def _evidence_keys(record):
    return {encode({"pagina": item["pagina"], "trecho_literal": item["trecho_literal"]})
            for _, item in v._walk_paths(record) if {"pagina", "trecho_literal"} <= item.keys()}


def _merge_reviews(task, incoming):
    previous = task["records"] + task["drafts"]
    by_id = {r["id"]: r for r in previous}
    draft_ids = {r["id"] for r in task["drafts"]}
    history = copy.deepcopy(task["review_history"])
    for index, record in enumerate(incoming):
        rid = record["id"]
        old = by_id.get(rid)
        if old is not None and rid in draft_ids:
            if not _evidence_keys(old) <= _evidence_keys(record):
                raise v.StructureValidationError("evidencia_revisao_removida", f"/registros/{index}", record,
                                                  "Preserve o ID e as evidências literais da ficha em revisão.", rid)
            if encode(old) != encode(record):
                history.append(copy.deepcopy(old))
            by_id[rid] = record
        elif old is not None:
            _merge([old], [record])  # Ficha concluída continua imutável.
        else:
            by_id[rid] = record
    # A conferência global também impede mesmo conteúdo com outro ID.
    return _merge([], list(by_id.values())), history


def _validate_incoming(records, targets, sent, pages, group_size=GROUP_SIZE):
    if len(records) > group_size:
        raise v.StructureValidationError("limite_eventos_resposta_excedido", "/registros", len(records),
                                          {"maximo_eventos": group_size})
    if len(records) > GROUP_SIZE and any(isinstance(row, dict) and row.get("destino") in {"incluido", "pendente"} for row in records):
        raise v.StructureValidationError("grupo_com_fichas_completas_excedido", "/registros", len(records),
            {"maximo_eventos": GROUP_SIZE, "orientacao": "Manter unidades restantes e seus IDs em inventários pendentes, sem apagá-los."})
    failures = []
    for index, record in enumerate(records):
        try:
            v._validate_records([record], targets, sent, pages, allow_pending_review=True)
        except v.AnvisaError as exc:
            detail = copy.deepcopy(exc.diagnostic)
            detail["campo"] = detail["campo"].replace("/registros/0", f"/registros/{index}", 1)
            failures.append((exc, detail))
    if failures:
        exc, first = failures[0]
        exc.diagnostic = {**first, "falhas_registros": [detail for _, detail in failures]}
        raise exc
    v._validate_records(records, targets, sent, pages, allow_pending_review=True)


def _validate_history(history, known_records, targets, sent, pages):
    if not isinstance(history, list):
        raise ValueError
    known = {r["id"]: r for r in known_records}
    for record in history:
        v._validate_records([record], targets, sent, pages, allow_pending_review=True)
        if (record["id"] not in known or not _needs_review(record)
                or not _evidence_keys(record) <= _evidence_keys(known[record["id"]])):
            raise ValueError


def _validated_state(state, pages):
    try:
        if state["schema"] != PROTOCOL_VERSION:
            raise ValueError
        partition = []
        all_records = []
        for complete, entries in ((True, state["completed"]), (False, state["pending"])):
            if not isinstance(entries, list):
                raise ValueError
            for entry in entries:
                if "group_policy" in entry:
                    adaptive.validate(entry["group_policy"])
                targets, sent = entry["targets"], entry["sent"]
                if (not isinstance(targets, list) or not targets or any(type(n) is not int for n in targets)
                        or targets != list(range(targets[0], targets[-1] + 1))
                        or not isinstance(sent, list) or any(type(n) is not int or n not in pages for n in sent)
                        or sent != sorted(set(sent)) or not set(targets) <= set(sent)):
                    raise ValueError
                partition.extend(targets)
                context = entry.get("context", ctx.empty()) if complete else entry["context"]
                ctx.validate(context, pages, sent)
                if complete:
                    result = entry["result"]
                    v._validate_block(result, targets, set(sent), pages)
                    if _partial(result) or ctx.pending(context) or context["review_required"]:
                        raise ValueError
                    all_records = _merge(all_records, result["registros"])
                    _validate_history(entry.get("review_history", []), result["registros"], targets, set(sent), pages)
                else:
                    records, drafts = entry["records"], entry["drafts"]
                    if not isinstance(records, list) or not isinstance(drafts, list):
                        raise ValueError
                    v._validate_records(records, targets, set(sent), pages)
                    v._validate_records(drafts, targets, set(sent), pages, allow_pending_review=True)
                    if any(not _needs_review(record) for record in drafts) or len({r["id"] for r in records + drafts}) != len(records + drafts):
                        raise ValueError
                    all_records = _merge(all_records, records + drafts)
                    _validate_history(entry["review_history"], records + drafts, targets, set(sent), pages)
                    if entry["continuation"] is not None:
                        result = {**entry["continuation"], "registros": records + drafts}
                        v._validate_block(result, targets, set(sent), pages, allow_pending=True)
                        if not _partial(result) and not ctx.pending(context) and not context["review_required"]:
                            raise ValueError
        if sorted(partition) != list(pages):
            raise ValueError
    except (ValueError, TypeError, KeyError, IndexError, AttributeError):
        raise CheckpointStorageError("Checkpoint privado incompatível com a fonte ou a validação.") from None
    return state


def _progress(result):
    return (sum(not _needs_review(r) for r in result["registros"]), len(result["registros"]),
            sum(r["estado"] == "analisada" for r in result["paginas"]),
            sum(b["estado_revisao"] == "revisada" and not b.get("pendencias") for b in result["reconciliacao_anexos"]))


def _references(inventory):
    return {rid for block in inventory for unit in block["unidades_fonte"] for rid in unit["ids_eventos"]}


def _task_steps(task, pages, base, key, deadline, diagnostic_sink, coordinator):
    continuations = automatic_continuations = transport_retries = 0
    targets, sent = task["targets"], set(task["sent"])
    correction, previous_result, failure = False, None, None
    page_expansions, group_calls, window_calls, stalls, transport_failures = 0, 0, 0, 0, 0
    while True:
        if not correction:
            group_size = adaptive.limit(task)
        instructions = [{"role": "system", "content": CONTINUATION}, {"role": "system", "content": ctx.INSTRUCTIONS}]
        extra = {}
        if correction:
            extra.update(ajuste_tecnico="Corrija somente o grupo atual; preserve a continuidade já validada.",
                        diagnostico_validacao=failure, resposta_anterior=previous_result)
            instructions.append({"role": "system", "content": v.CORRECTION_INSTRUCTIONS})
        instructions.append({"role": "system", "content": transport.INSTRUCTIONS})
        instructions.append({"role": "system", "content": adaptive.INSTRUCTIONS})
        # Zero na configuração desabilita apenas o prazo global. Cada
        # chamada continua limitada a 360 segundos e o progresso é validado.
        remaining = 360 if deadline is None else deadline - time.monotonic()
        if remaining <= 0:
            raise v.AnvisaError("IA: tempo total excedido; o progresso validado foi preservado no checkpoint.")
        if window_calls >= MAX_CONTINUATIONS:
            # Revalidar o estado persistido sem renovar as proteções de
            # correção, ausência de progresso, buscas ou ampliações.
            task = coordinator.reload(targets)
            window_calls = 0
            automatic_continuations += 1
        try:
            network_request = False
            ctx.add_searches(task, ctx.identifiers(task["drafts"][:group_size]), pages)
            data, window = ctx.build(task, pages, group_size, extra)
            if task != coordinator.task(targets):
                coordinator.persist(task)
            group_calls += 1
            window_calls += 1
            network_request = True
            result = yield parallel.RequestCall(base + instructions + [{"role": "user", "content": v._json(data).decode()}],
                                                key, min(remaining, 360), frozenset(parallel.scope(task, pages) | window), deadline)
        except v.TransientAnvisaError as exc:
            transport_failures += 1
            if transport_failures > len(TRANSPORT_RETRY_DELAYS):
                raise v.AnvisaError(str(exc) + f" Falha persistente após {transport_failures} tentativas; checkpoint preservado.") from None
            task = coordinator.reload(targets)
            transport_retries += 1
            yield parallel.RetryDelay(TRANSPORT_RETRY_DELAYS[transport_failures - 1])
            continue
        except v.AnvisaOutputLimit:
            if network_request and not correction and adaptive.shrink(task):
                coordinator.persist(task)
                continue
            if (len(targets) == 1 or task["continuation"] is not None
                    or task["context"]["review_required"]):
                raise
            middle = len(targets) // 2
            children = _tasks(targets[:middle], pages, task["records"]) + _tasks(targets[middle:], pages, task["records"])
            if "group_policy" in task:
                for child in children:
                    child["group_policy"] = copy.deepcopy(task["group_policy"])
            coordinator.split(task, children)
            break
        transport_failures = 0
        delivery_progress = ctx.acknowledge(task, window)
        sent = set(task["sent"])
        coordinator.persist(task)
        if ctx.has_request(result):
            context_before = task["context"]
            proposal = copy.deepcopy(task)
            try:
                page_expansions += int(ctx.request(proposal, result, pages))
                proposal["context"]["last_window"] = []
                ctx.build(proposal, pages, group_size, extra)  # Conferir orçamento antes de persistir o pedido.
                task = proposal
                coordinator.persist(task)
                if page_expansions > MAX_PAGE_EXPANSIONS:
                    raise ctx.ContextRequestError("limite de ampliações de páginas sem avanço do grupo atingido; pedido pendente preservado",
                        "contexto_limite_ampliacoes", "/contexto_necessario", result.get("contexto_necessario"),
                        "Até três ampliações explícitas desde o último avanço documental validado.")
            except v.AnvisaError as exc:
                error = exc if isinstance(exc, ctx.ContextRequestError) else ctx.ContextRequestError(
                    str(exc).removeprefix("IA: ").rstrip("."), "contexto_pedido_invalido", "/contexto_necessario",
                    {key: result[key] for key in ("contexto_necessario", "buscas_necessarias") if key in result},
                    "Pedido válido dentro dos limites de páginas, buscas, releituras e tamanho do pacote.")
                if diagnostic_sink is not None:
                    reference = diagnostic_sink({"model": v.MODEL, "prompt_sha256": v.PROMPT_HASH,
                        "generation_id": getattr(result, "generation_id", None), "chamada_no_bloco": group_calls,
                        "apos_pedido_correcao": correction,
                        "bloco": {"paginas_alvo": targets, "paginas_enviadas": sorted(window), "markdown_documental": data["markdown_documental"]},
                        "falha": error.diagnostic, "resposta_rejeitada": dict(result), "transporte_recebido": dict(result),
                        "evidencias_compartilhadas": data.get("evidencias_compartilhadas", {}),
                        "metricas_chamada": getattr(result, "metrics", {}),
                        "contexto": {"pedido": {key: result[key] for key in ("contexto_necessario", "buscas_necessarias") if key in result},
                            "janela_atual": sorted(window), "estado_antes": context_before,
                            "estado_proposto": proposal["context"]}})
                    error.args = (str(error) + " Diagnóstico: " + reference + ".",)
                if isinstance(result, v.ModelResult):
                    result.validation_status = "rejeitada"
                raise error from None
            if isinstance(result, v.ModelResult):
                result.validation_status = "contexto"
            continue
        try:
            wire_result = result
            result = transport.decode(wire_result, task, data, pages, window)
            if not isinstance(result.get("registros"), list):
                raise v.StructureValidationError("lista_obrigatoria", "/registros", result.get("registros"), "Lista JSON obrigatória.")
            _validate_incoming(result["registros"], targets, window, pages, group_size)
            v._evidence(result.get("reconciliacao_anexos", []), pages, window, path="/reconciliacao_anexos")
            merged, history = _merge_reviews(task, result["registros"])
            coordinator.check_records(targets, merged)
            combined = {**result, "registros": merged}
            v._validate_block(combined, targets, sent, pages, allow_pending=True)
            previous_references = _references((task["continuation"] or {}).get("reconciliacao_anexos", []))
            current_references = _references(combined["reconciliacao_anexos"])
            if not previous_references <= current_references:
                raise v.StructureValidationError("unidades_pendentes_omitidas", "/reconciliacao_anexos", sorted(current_references),
                                                  {"ids_a_preservar": sorted(previous_references)})
            pending_context = bool(ctx.pending(task["context"]))
            partial = _partial(combined) or pending_context
            if not partial:
                v._validate_block(combined, targets, sent, pages)
            before = {**(task["continuation"] or {}), "registros": task["records"] + task["drafts"]}
            old_progress = _progress(before) if task["continuation"] is not None else (len(task["records"]), len(before["registros"]), 0, 0)
            current_progress = _progress(combined)
            made_progress = current_progress > old_progress
            extra_reread = ctx.extra_reread_used(task["context"])
            if extra_reread and partial and not pending_context and not made_progress:
                raise ctx.reread_limit_error("", current_progress)
        except v.AnvisaError as exc:
            failure = getattr(exc, "diagnostic", {"motivo": "validacao_bloco", "mensagem": str(exc)})
            if diagnostic_sink is not None:
                reference = diagnostic_sink({"model": v.MODEL, "prompt_sha256": v.PROMPT_HASH,
                    "generation_id": getattr(result, "generation_id", None), "chamada_no_bloco": group_calls,
                    "apos_pedido_correcao": correction,
                    "bloco": {"paginas_alvo": targets, "paginas_enviadas": sorted(window), "markdown_documental": data["markdown_documental"]},
                    "falha": failure, "resposta_rejeitada": dict(result),
                    "transporte_recebido": dict(wire_result),
                    "evidencias_compartilhadas": data.get("evidencias_compartilhadas", {}),
                    "metricas_chamada": getattr(wire_result, "metrics", {})})
                exc.args = (str(exc) + " Diagnóstico: " + reference + ".",)
            if isinstance(wire_result, v.ModelResult):
                wire_result.validation_status = "rejeitada"
            if correction or isinstance(exc, ctx.ContextRequestError):
                raise
            previous_result, correction = transport.rejected_view(wire_result, data), True
            continue
        task["context"]["last_window"] = []
        if made_progress:
            page_expansions = 0
            ctx.progress(task)
            adaptive.accepted(task, group_size, result["registros"], wire_result, corrected=correction)
        if partial:
            if len(targets) > 1 and not merged and not current_references and not ctx.pending(task["context"]):
                middle = len(targets) // 2
                children = _tasks(targets[:middle], pages, merged) + _tasks(targets[middle:], pages, merged)
                if "group_policy" in task:
                    for child in children:
                        child["group_policy"] = copy.deepcopy(task["group_policy"])
                coordinator.split(task, children)
                if isinstance(wire_result, v.ModelResult):
                    wire_result.validation_status = "aceita"
                break
            draining_extra_context = extra_reread and pending_context
            stalls = stalls + 1 if not (delivery_progress or made_progress or draining_extra_context) else 0
            task["records"] = [r for r in merged if not _needs_review(r)]
            task["drafts"] = [r for r in merged if _needs_review(r)]
            task["review_history"] = history
            task["continuation"] = {k: combined[k] for k in ("paginas", "reconciliacao_anexos", "impedimento") if k in combined}
            task["sent"] = sorted(sent)
            coordinator.persist(task)
            if isinstance(wire_result, v.ModelResult):
                wire_result.validation_status = "aceita"
            if stalls >= 2:
                raise v.AnvisaError("IA: continuação sem progresso após duas respostas; checkpoint preservado.")
            continuations += 1
            correction, previous_result, failure = False, None, None
            continue
        if extra_reread and not made_progress:
            ctx.progress(task)
        task["context"]["review_required"] = False
        coordinator.complete(task, combined, history)
        if isinstance(wire_result, v.ModelResult):
            wire_result.validation_status = "aceita"
        break
    return {"continuacoes": continuations, "continuacoes_automaticas": automatic_continuations,
            "retentativas_transporte": transport_retries}


def run(pages, base, key, deadline, diagnostic_sink, checkpoint_store, *, sample_budget=None):
    state = checkpoint_store.load() if checkpoint_store is not None else None
    if state is None:
        pending = []
        for start in range(1, len(pages) + 1, 5):
            pending.extend(_tasks(list(range(start, min(start + 5, len(pages) + 1))), pages))
        state = {"schema": PROTOCOL_VERSION, "completed": [], "pending": pending}
    else:
        _validated_state(state, pages)
    reused = sorted(n for entry in state["completed"] for n in entry["targets"])
    reused_batches = len(state["completed"])
    coordinator = parallel.Coordinator(state, pages, checkpoint_store)
    coordinator.save(copy.deepcopy(state))
    state, execution_stats = coordinator.execute(
        lambda task, owner: _task_steps(task, pages, base, key, deadline, diagnostic_sink, owner),
        MAX_PARALLEL_BATCHES, sample_budget)
    _validated_state(state, pages)
    inventory, records, reviewed, checked = [], [], [], 0
    for entry in state["completed"]:
        rows, found, blocks, count = v._validate_block(entry["result"], entry["targets"], set(entry["sent"]), pages)
        reviewed.extend(rows)
        records.extend(found)
        inventory.extend(blocks)
        checked += count
    return inventory, records, reviewed, checked, {"lotes_reutilizados": reused_batches,
        "paginas_reutilizadas": reused, "lotes_concluidos": len(state["completed"]), **execution_stats}
