"""Análise Anvisa V8 em até duas chamadas ao Luna, sem usar checkpoints Terra."""

import hashlib
import json
import re
import socket
import uuid
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from http.client import HTTPException as HTTPProtocolError
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener

from . import anvisa_v8 as v

MODEL = "openai/gpt-6-luna"
OBSERVATION_LIMIT = 96
CONTEXT_OVERLAP = 2
PROCESS = re.compile(r"\d{5}\.\d{6}/\d{4}-\d{2}")
INSTRUCTIONS = """Analise os dois recortes conforme o contrato integral V8.
Para cada página-alvo, escreva uma observação de até 96 caracteres. Use rótulos curtos
como «Sem ato pertinente», «Unidade revisada» ou «Continuação conferida», conforme o caso.
Preserve as citações integrais nas fichas e no inventário, mesmo com observações curtas.
Copie valores técnicos do esquema literalmente, inclusive incluido sem acento.
Preencha justificativa_destino e todos os campos obrigatórios nas fichas completas.
Confira cada ocorrência indicada no índice e também procure atos sem processo identificado.
O índice local aponta ocorrências literais e não determina pertinência ou decisão.
Uma unidade que atravessa a divisão pertence ao recorte da sua página de início.
Um cabeçalho comum ou uma continuação de unidade não abre ficha própria.
Use o texto das páginas de sobreposição para conferir atos de fronteira.
Inclua deferimentos, cancelamentos e indeferimentos pertinentes.
Cada unidade do inventário contém ids_eventos como lista de strings com IDs deste recorte.
Use [] para grupos administrativos sem evento ou unidades que começam fora do recorte.
Reconcilie o inventário e declare pendências de forma fiel quando não houver contexto suficiente.
"""


def _object(properties, required=None):
    return {"type": "object", "properties": properties, "additionalProperties": True,
            "required": list(properties) if required is None else required}


def _array(items):
    return {"type": "array", "items": items}


def output_schema():
    text = {"type": "string"}
    nonempty = {"type": "string", "minLength": 1}
    integer = {"type": "integer"}
    evidence = _object({"pagina": integer, "trecho_literal": nonempty})
    field = _object({"estado": {"enum": sorted(v.STATES - {"limitacao_conversao", "falha_recuperacao"})},
                     "valor": {"type": ["string", "null"]}, "evidencias": _array(evidence)})
    review = _object({"estado": {"enum": ["revisada", "pendente"]}, "pendencias": _array(nonempty)})
    common = {"id": nonempty, "categoria": nonempty, "paginas_origem": _array(integer)}
    full = _object({
        **common, "destino": {"enum": ["incluido", "pendente"]}, "justificativa_destino": nonempty,
        **{name: field for name in sorted(v.FIELDS)},
        **{name: _array({}) for name in sorted(v.ARRAYS)},
        "campos_adicionais": {"type": "object"}, "conferencia_integridade": review,
    })
    compact = _object({
        **common, "destino": {"enum": ["excluido", "representacao_duplicada"]},
        "justificativa": nonempty, "justificativa_destino": nonempty, "evidencias": _array(evidence),
    }, [*common, "destino"])
    compact["anyOf"] = [{"required": ["justificativa"]}, {"required": ["justificativa_destino"]}]
    unit = _object({"ids_eventos": _array(nonempty)})
    inventory = _object({"estado_revisao": {"enum": ["revisada", "pendente"]},
                         "unidades_fonte": _array(unit), "pendencias": _array(text)})
    page = _object({"pagina": integer, "estado": {"enum": ["analisada", "pendente"]},
                    "observacao": {**nonempty, "maxLength": OBSERVATION_LIMIT}})
    return _object({"paginas": _array(page), "registros": _array({"anyOf": [full, compact]}),
                    "reconciliacao_anexos": _array(inventory)})


def _input(pages, targets, window):
    occurrences = []
    for number in window:
        for line, content in enumerate(pages[number].splitlines(), 1):
            identifiers = PROCESS.findall(content)
            if identifiers:
                occurrences.append({"pagina": number, "linha": line, "identificadores": identifiers,
                                    "alvo": targets[0] <= number <= targets[-1]})
    return {"paginas_alvo": targets, "total_paginas": len(pages),
            "markdown_documental": "".join(f"## Página {n}{pages[n]}" for n in window),
            "indice_ocorrencias_literais": occurrences}


def _request(messages, key, timeout):
    payload = {
        "model": MODEL, "messages": messages, "stream": False, "max_completion_tokens": 48000,
        "reasoning": {"effort": "medium"},
        "response_format": {"type": "json_schema",
                            "json_schema": {"name": "miller_anvisa_v8", "strict": False, "schema": output_schema()}},
        "provider": {"only": ["openai"], "data_collection": "deny", "require_parameters": True,
                     "allow_fallbacks": False},
        "plugins": [{"id": plugin, "enabled": False} for plugin in ("web", "context-compression", "pareto-router")],
    }
    request = Request(v.URL, data=v._json(payload), headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
    }, method="POST")
    try:
        with build_opener(v._NoRedirect()).open(request, timeout=timeout) as response:
            body = json.loads(response.read(8 * 1024 * 1024 + 1))
    except HTTPError as exc:
        status = exc.code
        exc.close()
        raise v.AnvisaError(f"IA: OpenRouter retornou HTTP {status} para o Luna.") from None
    except (URLError, socket.timeout, OSError, HTTPProtocolError):
        raise v.AnvisaError("IA: falha de conexão ou tempo limite no OpenRouter para o Luna.") from None
    except (ValueError, UnicodeError):
        raise v.AnvisaError("IA: resposta HTTP do Luna inválida.") from None
    try:
        choice = body["choices"][0]
        if choice["finish_reason"] == "length":
            raise v.AnvisaOutputLimit("IA: resposta do Luna incompleta por limite de saída.")
        if choice["finish_reason"] != "stop" or choice.get("error") or body.get("error"):
            raise v.AnvisaError("IA: resposta do Luna incompleta ou interrompida.")
        if body.get("model") not in {MODEL, f"{MODEL}-20261006"}:
            raise v.AnvisaError("IA: o OpenRouter não confirmou o modelo Luna solicitado.")
        result = json.loads(choice["message"]["content"])
        if not isinstance(result, dict):
            raise ValueError
        return result
    except v.AnvisaError:
        raise
    except (ValueError, TypeError, KeyError, IndexError, AttributeError):
        raise v.AnvisaError("IA: o Luna não retornou o JSON esperado.") from None


def _part(pages, targets, base, key, timeout, diagnostic_sink):
    window = range(max(1, targets[0] - CONTEXT_OVERLAP), min(len(pages), targets[-1] + CONTEXT_OVERLAP) + 1)
    data = _input(pages, targets, window)
    result = _request([*base, {"role": "user", "content": v._json(data).decode()}], key, timeout)
    try:
        if result.get("contexto_necessario") or result.get("buscas_necessarias") or result.get("impedimento"):
            raise v.StructureValidationError("luna_contexto_ou_impedimento", "/", result,
                                             "Parte concluída com o contexto fornecido.")
        checked = v._validate_block(result, targets, set(window), pages)
        for index, row in enumerate(checked[0]):
            if len(row["observacao"]) > OBSERVATION_LIMIT:
                raise v.StructureValidationError("observacao_extensa", f"/paginas/{index}/observacao",
                                                 row["observacao"], f"Até {OBSERVATION_LIMIT} caracteres.")
        return checked
    except (v.StructureValidationError, v.EvidenceValidationError) as exc:
        reference = diagnostic_sink({
            "model": MODEL, "prompt_sha256": v.PROMPT_HASH, "falha": exc.diagnostic,
            "bloco": {"paginas_alvo": targets, "paginas_enviadas": list(window),
                      "markdown_documental": data["markdown_documental"]},
            "resposta_rejeitada": result,
        })
        raise v.AnvisaError(f"VALIDAÇÃO: parte {targets[0]}–{targets[-1]} do Luna rejeitada. Diagnóstico: {reference}.") from None


def analyze(markdown, page_count, expected_hash, key, timeout, *, diagnostic_sink):
    source_hash = hashlib.sha256(markdown.encode()).hexdigest()
    markers = list(v.PAGE.finditer(markdown))
    if source_hash != expected_hash or page_count < 1 or [int(m[1]) for m in markers] != list(range(1, page_count + 1)):
        raise v.AnvisaError("VALIDAÇÃO: Markdown salvo, hash e páginas não correspondem.")
    pages = {i + 1: markdown[marker.end():markers[i + 1].start() if i + 1 < len(markers) else len(markdown)]
             for i, marker in enumerate(markers)}
    if any(not text.strip() or "_Nenhum conteúdo textual extraível nesta página._" in text for text in pages.values()):
        raise v.AnvisaError("VALIDAÇÃO: o Markdown tem página sem texto extraível; análise interrompida.")
    try:
        prompt = v.PROMPT_PATH.read_bytes()
    except OSError:
        raise v.AnvisaError("VALIDAÇÃO: arquivo do prompt V8 indisponível.") from None
    if v._sha(prompt) != v.PROMPT_HASH:
        raise v.AnvisaError("VALIDAÇÃO: o prompt instalado diverge do V8 aprovado.")
    base = [{"role": "system", "content": text} for text in (prompt.decode(), v.TRANSPORT, INSTRUCTIONS)]
    middle = (page_count + 1) // 2
    ranges = [list(range(1, middle + 1))]
    if middle < page_count:
        ranges.append(list(range(middle + 1, page_count + 1)))
    with ThreadPoolExecutor(max_workers=len(ranges)) as executor:
        futures = [executor.submit(_part, pages, targets, base, key, min(timeout or 360, 360), diagnostic_sink)
                   for targets in ranges]
        parts = [future.result() for future in futures]
    reviewed = [row for part in parts for row in part[0]]
    records = [record for part in parts for record in part[1]]
    page_ids = {number: [] for number in pages}
    for record in records:
        for number in record["paginas_origem"]:
            page_ids[number].append(record["id"])
    return records, {
        "versao_prompt": v.PROMPT_VERSION, "prompt_sha256": v.PROMPT_HASH, "modelo": MODEL,
        "revisao_checkpoint": f"ANV8-{uuid.uuid4().hex}",
        "fonte": {"sha256": source_hash, "paginas_encontradas": list(pages)},
        "paginas": [dict(row, ids_eventos=page_ids[row["pagina"]]) for row in reviewed],
        "reconciliacao_anexos": [block for part in parts for block in part[2]],
        "totais_por_destino": dict(Counter(record["destino"] for record in records)),
        "totais_por_categoria": dict(Counter(record["categoria"] for record in records if record["destino"] == "incluido")),
        "ultimo_bloco_fechado": page_count, "eventos_abertos": [], "proximo_bloco": None,
        "pendencias_integridade": [], "evidencias_literais_conferidas": sum(part[3] for part in parts),
        "processamento_incremental": {"modo": "luna_duas_partes", "chamadas": len(parts), "lotes_reutilizados": 0},
    }
