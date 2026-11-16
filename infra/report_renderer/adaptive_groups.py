"""Escolha conservadora do tamanho da próxima resposta; não altera dados V8."""

from __future__ import annotations

import copy

from . import anvisa_v8 as v

ENABLED = True
INITIAL_SIZE = 8
MAX_SIZE = 16
SIZES = (1, 2, 4, 8, 12, 16)
INSTRUCTIONS = """O tamanho do grupo pode variar entre chamadas. Respeite limite_eventos_resposta.
Grupos acima de oito são exclusivos para registros compactos excluidos ou representacao_duplicada.
Ao encontrar incluido, pendente ou revisão de ficha completa, devolva até limite_fichas_completas
eventos no total, mantendo as demais unidades e seus IDs em inventários pendentes. Não resuma
fichas, não divida eventos, não omita informações nem invente eventos para preencher o limite.
Na correção, preserve o trabalho anterior e deixe explicitamente pendentes as unidades restantes.
O limite orienta apenas transporte; cobertura, evidências e conferência continuam integrais.
"""


def initial():
    return {"limit": INITIAL_SIZE, "cooldown": 0, "increases": 0, "reductions": 0}


def validate(policy):
    if (not isinstance(policy, dict) or set(policy) != set(initial())
            or any(type(value) is not int for value in policy.values())
            or policy["limit"] not in SIZES or not 0 <= policy["cooldown"] <= 2
            or policy["increases"] < 0 or policy["reductions"] < 0):
        raise ValueError("Estado do tamanho adaptativo inválido.")


def limit(task):
    if not ENABLED:
        return INITIAL_SIZE
    current = task.get("group_policy", initial())["limit"]
    return min(current, INITIAL_SIZE if task["drafts"] else MAX_SIZE)


def _save(task, policy):
    if policy != initial() or "group_policy" in task:
        task["group_policy"] = policy


def shrink(task):
    if not ENABLED or limit(task) <= 1:
        return False
    policy = copy.deepcopy(task.get("group_policy", initial()))
    policy.update(limit=SIZES[SIZES.index(limit(task)) - 1], cooldown=2,
                  reductions=policy["reductions"] + 1)
    _save(task, policy)
    return True


def accepted(task, requested, records, response, *, corrected=False):
    """Só respostas já aceitas e com progresso podem alimentar esta decisão."""
    if not ENABLED or not records:
        return
    policy = copy.deepcopy(task.get("group_policy", initial()))
    previous = policy["limit"]
    metrics = getattr(response, "metrics", {})
    tokens, seconds = metrics.get("completion_tokens"), metrics.get("duracao_requisicao_segundos")
    measured = type(tokens) is int and tokens >= 0 and type(seconds) in (int, float) and seconds >= 0
    lengths = [len(v._json(row)) for row in records]
    complete = any(row["destino"] in {"incluido", "pendente"} for row in records)
    expensive = max(lengths) > 8000 or (measured and (tokens > 16000 or seconds > 120))
    if expensive:
        policy["limit"] = SIZES[max(0, SIZES.index(min(previous, requested)) - 1)]
        if complete:
            policy["limit"] = min(policy["limit"], INITIAL_SIZE)
        policy["cooldown"] = 2
    elif complete or corrected:
        policy["limit"] = min(previous, INITIAL_SIZE)
        policy["cooldown"] = 2
    elif max(lengths) > 4000 or sum(lengths) > 2500 * len(records) or (measured and tokens > 1000 * len(records)):
        policy["limit"] = min(previous, INITIAL_SIZE)
        policy["cooldown"] = 2
    elif policy["cooldown"]:
        policy["cooldown"] -= 1
    elif (measured and len(records) == requested and max(lengths) <= 4000
          and sum(lengths) <= 2500 * len(records) and tokens <= 1000 * len(records)
          and seconds <= 120 and previous < MAX_SIZE):
        policy["limit"] = min(SIZES[SIZES.index(previous) + 1], MAX_SIZE)
    if policy["limit"] > previous:
        policy["increases"] += 1
    elif policy["limit"] < previous:
        policy["reductions"] += 1
    _save(task, policy)
