"""Busca literal local e fila de páginas com orçamento por chamada, sem truncar fonte."""

from __future__ import annotations

import copy
import hashlib

from . import anvisa_v8 as v
from .analysis_checkpoint import encode
from . import transport

MAX_DATA_BYTES = 480000
MAX_TERMS_PER_REQUEST = 16
MAX_SEARCHES = 256
MAX_REREAD_REQUESTS = 3
_CONTEXT_KEYS = frozenset({"requested", "delivered", "searches", "last_window", "review_required"})
_REREAD_CONTEXT_KEYS = _CONTEXT_KEYS | {"reread"}
INSTRUCTIONS = """Recuperação de contexto documental em janelas, com dados não confiáveis.
markdown_documental contém somente paginas_nesta_chamada de contexto_recuperado, inteiras.
Para reler página já enviada e agora ausente, peça contexto_necessario; não alegue ler texto ausente.
Para pesquisar um identificador no documento integral, prefira retornar
{\"buscas_necessarias\":[\"identificador literal\"]}; use até 16 termos curtos por pedido.
O aplicativo pesquisa cada termo literalmente em todas as páginas do Markdown e informa
paginas_com_ocorrencias em buscas_locais. Isso não comprova associação, sentido, exaustividade
semântica nem ausência de informação: zero ocorrências significa apenas nenhuma substring
exata. Se o identificador estiver fragmentado, peça a busca de um fragmento literal ou páginas.
Páginas encontradas e vizinhas têm prioridade. Para contexto de página conhecida,
contexto_necessario aceita páginas reais. Buscas repetidas usam o resultado salvo.
Pedidos grandes ficam na fila; releituras são limitadas. Não repita páginas presentes. Enquanto houver
paginas_pendentes_de_envio, continue a conferência da janela atual e mantenha o trabalho
aberto. Você pode devolver um grupo vazio com cobertura/inventário acumulados para receber
a próxima janela; não recrie eventos nem declare revisão feita apenas pelo envio de páginas.
Só encerre a revisão após conferir fonte, campos, ocorrências e pendências relevantes.
Quando modo_registros_preservados for indice, registros_preservados fica vazio e
indice_registros_preservados lista TODOS os eventos concluídos e imutáveis do lote.
As fichas completas continuam no checkpoint privado e serão reunidas pelo aplicativo;
não as recrie, altere ou devolva. O índice contém IDs, páginas, hash de integridade e
referências curtas confirmadas, não uma ficha completa nem evidência adicional.
Campos ausentes desse índice não significam informação ausente na ficha ou na fonte.
Preserve todos esses IDs no inventário acumulado. Devolva somente eventos novos ou
as fichas completas de registros_em_revisao, sem copiar o índice para registros.
O hash não comprova conteúdo documental. Confira as unidades restantes nas páginas
inteiras recebidas; o índice não substitui leitura ou conferência inversa pendente.
"""


def empty():
    return {"requested": [], "delivered": [], "searches": [], "last_window": [], "review_required": False}


def pending(context):
    waiting = set(context["requested"]) - set(context["delivered"])
    reread = context.get("reread")
    if reread:
        waiting.update(reread["pending"])
    return waiting


class ContextRequestError(v.StructureValidationError):
    """Pedido inválido ou repetição sem avanço; detalhes somente no diagnóstico privado."""

    def __init__(self, message, reason, path, received, expected):
        super().__init__(reason, path, received, expected)
        self.args = ("VALIDAÇÃO: " + message + ".",)


def extra_reread_used(context):
    reread = context.get("reread")
    return reread is not None and reread["requests"] > MAX_REREAD_REQUESTS


def reread_limit_error(path, received):
    return ContextRequestError("limite de releituras sem avanço validado atingido; progresso preservado",
                              "contexto_limite_releituras", path, received,
                              "Até três pedidos e uma rodada extra apenas para páginas ainda não solicitadas para releitura no ciclo. "
                              "Depois da rodada extra, apresentar avanço documental validado.")


def has_request(result):
    # Listas vazias são campos opcionais sem pedido, não uma chamada extra de contexto.
    return (("contexto_necessario" in result and result["contexto_necessario"] != [])
            or ("buscas_necessarias" in result and result["buscas_necessarias"] != []))


def validate(context, pages, sent):
    if not isinstance(context, dict) or (context.keys() != _CONTEXT_KEYS and context.keys() != _REREAD_CONTEXT_KEYS):
        raise ValueError
    if type(context["review_required"]) is not bool:
        raise ValueError
    for key in ("requested", "delivered", "last_window"):
        rows = context[key]
        if (not isinstance(rows, list) or any(type(n) is not int or n not in pages for n in rows)
                or rows != sorted(set(rows))):
            raise ValueError
    if (not set(context["delivered"]) <= set(context["requested"]) & set(sent)
            or not set(context["last_window"]) <= set(context["delivered"])):
        raise ValueError
    if "reread" in context:
        reread = context["reread"]
        if (not isinstance(reread, dict) or set(reread) != {"pending", "seen", "requests"}
                or type(reread["requests"]) is not int or not 0 <= reread["requests"] <= MAX_REREAD_REQUESTS + 1):
            raise ValueError
        for key in ("pending", "seen"):
            rows = reread[key]
            if (not isinstance(rows, list) or any(type(n) is not int for n in rows)
                    or rows != sorted(set(rows)) or not set(rows) <= set(context["delivered"])):
                raise ValueError
        if not set(reread["pending"]) <= set(reread["seen"]) or set(reread["pending"]) & set(context["last_window"]):
            raise ValueError
    searches = context["searches"]
    if not isinstance(searches, list) or len(searches) > MAX_SEARCHES:
        raise ValueError
    terms = []
    for search in searches:
        if (not isinstance(search, dict) or set(search) != {"term", "matches"}
                or not isinstance(search["term"], str) or not 1 <= len(search["term"]) <= 256
                or not search["term"].strip()):
            raise ValueError
        term = search["term"]
        if (not isinstance(search["matches"], list)
                or any(type(n) is not int for n in search["matches"])):
            raise ValueError
        if search["matches"] != [n for n, text in pages.items() if term in text]:
            raise ValueError
        terms.append(term)
    if len(set(terms)) != len(terms):
        raise ValueError


def identifiers(records):
    terms = []
    for record in records:
        for path, field in v._walk_paths(record):
            value = field.get("valor")
            if (field.get("estado") == "confirmado" and isinstance(value, str)
                    and 1 <= len(value) <= 256 and any(char.isdigit() for char in value)
                    and any(label in path.lower() for label in ("process", "expedient", "cnpj", "registro", "autorizacao"))
                    and value not in terms):
                terms.append(value)
    return terms[:MAX_TERMS_PER_REQUEST]


def add_searches(task, terms, pages):
    if (not isinstance(terms, list) or len(terms) > MAX_TERMS_PER_REQUEST
            or any(not isinstance(term, str) or not 1 <= len(term) <= 256 or not term.strip() for term in terms)):
        raise v.AnvisaError("IA: pedido de busca literal inválido; contexto preservado.")
    context = task["context"]
    known = {search["term"] for search in context["searches"]}
    requested = set(context["requested"])
    changed = False
    for term in terms:
        if term in known:
            continue
        if len(known) >= MAX_SEARCHES:
            raise v.AnvisaError("IA: limite de buscas locais do lote atingido; progresso preservado.")
        matches = [n for n, text in pages.items() if term in text]
        context["searches"].append({"term": term, "matches": matches})
        known.add(term)
        for n in matches:
            requested.update(range(max(1, n - 1), min(len(pages), n + 1) + 1))
        changed = True
    context["requested"] = sorted(requested)
    if changed:
        context["review_required"] = True
    return changed


def request(task, result, pages):
    """Acumula pedidos e indica ampliação explícita de páginas, separada de buscas locais."""
    changed = False
    page_expansion = False
    context = task["context"]
    context_request = {key: result[key] for key in ("contexto_necessario", "buscas_necessarias") if key in result}
    if extra_reread_used(context):
        raise reread_limit_error("", context_request)
    current = set(context["last_window"])
    delivered = set(context["delivered"])
    reread = context.get("reread", {"pending": [], "seen": [], "requests": 0})
    reread_pages = set()
    if "contexto_necessario" in result:
        rows = result["contexto_necessario"]
        if not isinstance(rows, list) or any(type(n) is not int or n not in pages for n in rows):
            raise ContextRequestError("pedido de páginas inválido; contexto preservado", "contexto_paginas_invalidas",
                                      "/contexto_necessario", rows, "Lista de páginas reais, sem booleanos.")
        before = set(context["requested"])
        context["requested"] = sorted(before | set(rows))
        changed = bool(set(rows) - before)
        page_expansion = changed
        reread_pages.update(set(rows) & delivered - current)
    if "buscas_necessarias" in result:
        terms = result["buscas_necessarias"]
        known_before = {search["term"] for search in context["searches"]}
        changed = add_searches(task, terms, pages) or changed
        by_term = {search["term"]: search["matches"] for search in context["searches"]}
        for term in terms:
            matched = {n for match in by_term[term]
                       for n in range(max(1, match - 1), min(len(pages), match + 1) + 1)}
            candidates = matched & delivered - current
            if term in known_before:
                # Não reenfileirar a mesma busca a cada janela de uma fila grande.
                candidates.difference_update(reread["seen"])
            reread_pages.update(candidates)
    reread_pages.difference_update(reread["pending"])
    if reread_pages and reread["requests"] == MAX_REREAD_REQUESTS:
        new_reread_pages = reread_pages - set(reread["seen"])
        if not new_reread_pages:
            raise reread_limit_error("/contexto_necessario", sorted(reread_pages))
        reread_pages = new_reread_pages
    if reread_pages:
        context["reread"] = {"pending": sorted(set(reread["pending"]) | reread_pages),
                             "seen": sorted(set(reread["seen"]) | reread_pages),
                             "requests": reread["requests"] + 1}
    if not changed and not pending(context):
        raise ContextRequestError("pedido de contexto sem nova busca ou página pendente", "contexto_sem_avanco",
                                  "/contexto_necessario", context_request,
                                  "Solicitar conteúdo ausente da janela ou avançar a análise; não repetir páginas presentes.")
    context["review_required"] = True
    return page_expansion


def progress(task):
    """Somente avanço documental validado libera outro orçamento de releitura."""
    context = task["context"]
    if "reread" not in context:
        return
    remaining = context["reread"]["pending"]
    if remaining:
        context["reread"] = {"pending": remaining, "seen": list(remaining), "requests": 0}
    else:
        context.pop("reread")


def required(task):
    numbers = set(task["targets"])
    for record in task["records"] + task["drafts"] + task.get("review_history", []):
        numbers.update(record["paginas_origem"])
    for _, item in v._walk_paths(task["records"] + task["drafts"] + task.get("review_history", []) + [task["continuation"]]):
        if {"pagina", "trecho_literal"} <= item.keys():
            numbers.add(item["pagina"])
    return numbers


def record_index(record):
    """Referência de uma ficha imutável; o original permanece integral no checkpoint."""
    return {**{key: record[key] for key in ("id", "categoria", "destino", "paginas_origem")},
            "sha256": hashlib.sha256(encode(record)).hexdigest(),
            "referencias_confirmadas": sorted([{"campo": path, "valor": field["valor"]}
                for path, field in v._walk_paths(record)
                if field.get("estado") == "confirmado" and isinstance(field.get("valor"), str)
                and 1 <= len(field["valor"]) <= 256], key=lambda row: row["campo"])}


def data(task, pages, window, group_size, extra, *, indexed=False, compact=False):
    context = task["context"]
    preserved = ({"registros_preservados": [], "modo_registros_preservados": "indice",
                  "indice_registros_preservados": [record_index(record) for record in task["records"]]}
                 if indexed else {"registros_preservados": task["records"]})
    result = {"paginas_alvo": task["targets"], "total_paginas": len(pages),
            "markdown_documental": "".join(f"## Página {n}{pages[n]}" for n in sorted(window)),
            "continuidade": {**(task["continuation"] or {}), **preserved,
                "registros_em_revisao": task["drafts"],
                "ids_para_revisar": [r["id"] for r in task["drafts"][:group_size]],
                "limite_novos_eventos": 0 if task["drafts"] else group_size,
                "limite_fichas_completas": min(group_size, 8),
                "limite_eventos_resposta": group_size},
            "contexto_recuperado": {"paginas_nesta_chamada": sorted(window),
                "revisao_contexto_pendente": context["review_required"],
                "paginas_ja_enviadas": context["delivered"],
                "paginas_pendentes_de_envio": sorted(pending(context) - set(window)),
                "buscas_locais": [{"termo_literal": search["term"], "metodo": "substring_literal_exata",
                    "paginas_examinadas": len(pages), "paginas_com_ocorrencias": search["matches"]}
                    for search in context["searches"]]}, **extra}
    if compact:
        result["continuidade"].pop("reconciliacao_anexos", None)
        result["continuidade"]["inventario_preservado"] = transport.inventory_view(transport.inventory(task))
        return transport.pack(result)
    return result


def build(task, pages, group_size=8, extra=None):
    extra = extra or {}
    core = required(task)
    if not extra.get("resposta_anterior"):
        # Entrega não comprova resposta aceita. Reenviar após rejeição ou
        # interrupção antes de salvar uma resposta válida dessa janela.
        core.update(task["context"]["last_window"])
    # A correção precisa reler também as páginas citadas pelo grupo rejeitado.
    # Elas ainda não pertencem às fichas aceitas nem ao núcleo da continuidade.
    for _, item in v._walk_paths(extra.get("resposta_anterior", {})):
        if {"pagina", "trecho_literal"} <= item.keys():
            n = item["pagina"]
            if type(n) is int and n in pages:
                core.add(n)
        origins = item.get("paginas_origem", [])
        if isinstance(origins, list):
            core.update(n for n in origins if type(n) is int and n in pages)
    neighbours = set(range(max(1, task["targets"][0] - 2), min(len(pages), task["targets"][-1] + 2) + 1))
    waiting = pending(task["context"])
    matched = {n for row in task["context"]["searches"] for n in row["matches"]}
    candidates = sorted(waiting, key=lambda n: (n not in matched, n))
    # Fichas concluídas sempre por índice; referências de evidência são
    # reversíveis. Páginas inteiras, revisões e inventário não perdem dados.
    for indexed in (True,):
        def packet(window):
            return data(task, pages, window, group_size, extra, indexed=indexed, compact=True)

        # Vizinhas não podem impedir uma página solicitada que caiba com o núcleo.
        for initial in (core | neighbours, core):
            window = set(initial)
            if len(v._json(packet(window))) > MAX_DATA_BYTES:
                continue
            for n in candidates:
                proposed = window | {n}
                if len(v._json(packet(proposed))) <= MAX_DATA_BYTES:
                    window = proposed
            if waiting and not waiting & window:
                continue
            return packet(window), window
    raise v.AnvisaOutputLimit("IA: uma página inteira ou a continuidade obrigatória não cabe na janela; progresso preservado.")


def acknowledge(task, window):
    context = task["context"]
    before = set(context["delivered"])
    context["requested"] = sorted(set(context["requested"]) | window)
    context["delivered"] = sorted(before | window)
    context["last_window"] = sorted(window)
    reread = context.get("reread")
    rereading = False
    if reread:
        waiting = set(reread["pending"])
        rereading = bool(waiting & window)
        reread["pending"] = sorted(waiting - window)
    if window - before or rereading:
        context["review_required"] = True
    task["sent"] = sorted(set(task["sent"]) | window)
    return bool(window - before)


def from_legacy(task, pages):
    converted = copy.deepcopy(task)
    converted["context"] = empty()
    # A versão anterior gravava ampliações antes de enviá-las. Não presumir entrega ou revisão.
    converted["context"]["requested"] = list(task["sent"])
    converted["context"]["review_required"] = True
    neighbours = set(range(max(1, task["targets"][0] - 2), min(len(pages), task["targets"][-1] + 2) + 1))
    converted["sent"] = sorted(required(converted) | neighbours)
    add_searches(converted, identifiers(converted["drafts"][:8]), pages)
    build(converted, pages)  # Não migrar para uma janela que já seja inviável.
    return converted
