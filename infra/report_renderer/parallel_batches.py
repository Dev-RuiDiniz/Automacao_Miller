"""Chamadas concorrentes com um único coordenador de validação e persistência."""

from __future__ import annotations

import copy
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass, field

from . import anvisa_v8 as v, context_window as ctx
from .analysis_checkpoint import CheckpointStorageError, encode
from .diagnostics import DiagnosticStorageError


@dataclass
class RequestCall:
    messages: list = field(repr=False)
    key: str = field(repr=False)
    timeout: float
    scope: frozenset
    deadline: float | None = None


@dataclass
class RetryDelay:
    seconds: int


class AnalysisSampleComplete(Exception):
    """Fim de amostra interna explícita; nunca configurado pela rota operacional."""


def scope(task, pages):
    """Contexto conhecido e ainda solicitado; sobreposição exige chamadas sequenciais."""
    numbers = (ctx.required(task) | ctx.pending(task["context"]) | ctx.retained_rereads(task["context"])
               | set(task["context"]["last_window"])
               | set(range(max(1, task["targets"][0] - 2), min(len(pages), task["targets"][-1] + 2) + 1)))
    for _, unit in v._walk_paths(task.get("continuation") or {}):
        for key in ("paginas_origem", "paginas"):
            references = unit.get(key, [])
            if isinstance(references, list):
                numbers.update(n for n in references if type(n) is int and n in pages)
    return numbers


class Coordinator:
    def __init__(self, state, pages, store):
        self.state, self.pages, self.store = state, pages, store
        self.stats = {"continuacoes": 0, "continuacoes_automaticas": 0, "retentativas_transporte": 0,
                      "chamadas_simultaneas_maximas": 0}

    def task(self, targets):
        return next(row for row in self.state["pending"] if tuple(row["targets"]) == tuple(targets))

    def save(self, candidate):
        candidate["completed"].sort(key=lambda row: row["targets"][0])
        candidate["pending"].sort(key=lambda row: row["targets"][0])
        partition = sorted(n for row in candidate["completed"] + candidate["pending"] for n in row["targets"])
        if partition != list(self.pages):
            raise CheckpointStorageError("Partição divergente ao salvar o progresso coordenado.")
        if self.store is not None:
            self.store.save(candidate)
        self.state = candidate

    def persist(self, task):
        candidate = copy.deepcopy(self.state)
        index = next(i for i, row in enumerate(candidate["pending"]) if row["targets"] == task["targets"])
        candidate["pending"][index] = copy.deepcopy(task)
        self.save(candidate)

    def reload(self, targets):
        from . import incremental as inc
        restored = self.store.load() if self.store is not None else copy.deepcopy(self.state)
        if restored is None or encode(restored) != encode(self.state):
            raise CheckpointStorageError("Checkpoint divergente antes da continuação automática.")
        self.state = inc._validated_state(restored, self.pages)
        return copy.deepcopy(self.task(targets))

    def check_records(self, targets, incoming):
        from . import incremental as inc
        others = []
        for row in self.state["completed"]:
            others = inc._merge(others, row["result"]["registros"])
        for row in self.state["pending"]:
            if row["targets"] != targets:
                others = inc._merge(others, row["records"] + row["drafts"])
        inc._merge(others, incoming)

    def split(self, task, children):
        candidate = copy.deepcopy(self.state)
        candidate["pending"] = [row for row in candidate["pending"] if row["targets"] != task["targets"]] + children
        self.save(candidate)

    def complete(self, task, result, history):
        candidate = copy.deepcopy(self.state)
        candidate["completed"].append({"targets": task["targets"], "sent": task["sent"], "result": result,
            "review_history": history, "context": copy.deepcopy(task["context"])})
        if "group_policy" in task:
            candidate["completed"][-1]["group_policy"] = copy.deepcopy(task["group_policy"])
        candidate["pending"] = [row for row in candidate["pending"] if row["targets"] != task["targets"]]
        self.save(candidate)

    def execute(self, make_steps, max_parallel, sample_budget=None):
        """Só o I/O do provedor vai para threads; geradores e escritas ficam nesta thread."""
        if type(max_parallel) is not int or not 1 <= max_parallel <= 2:
            raise ValueError("Concorrência interna inválida.")
        if sample_budget is not None and (not isinstance(sample_budget, dict) or not sample_budget
                or any(not isinstance(key, tuple) or type(value) is not int or value < 1
                       for key, value in sample_budget.items())
                or not set(sample_budget) <= {tuple(row["targets"]) for row in self.state["pending"]}):
            raise ValueError("Orçamento da amostra interna inválido.")
        jobs, futures, used = {}, {}, {}
        failure = None

        def allowed(targets):
            return sample_budget is None or used.get(targets, 0) < sample_budget.get(targets, 0)

        def advance(job, value=None, error=None, initial=False):
            try:
                if initial:
                    action = next(job["steps"])
                elif error is not None:
                    action = job["steps"].throw(error)
                else:
                    action = job["steps"].send(value)
                job["action"] = action
                job["ready_at"] = time.monotonic() + action.seconds if isinstance(action, RetryDelay) else 0
                job["delay_had_peers"] = isinstance(action, RetryDelay) and bool(futures)
            except StopIteration as stopped:
                for key, count in (stopped.value or {}).items():
                    self.stats[key] += count
                jobs.pop(job["targets"])
            except Exception as exc:
                if isinstance(value, v.ModelResult) and value.validation_status == "recebida":
                    value.validation_status = "falha_armazenamento" if isinstance(exc, (CheckpointStorageError, DiagnosticStorageError)) else "erro"
                raise

        def dispatch(job, executor):
            targets = job["targets"]
            if job["busy"] or not allowed(targets) or len(futures) >= max_parallel:
                return
            if isinstance(job["action"], RetryDelay):
                if job["ready_at"] > time.monotonic():
                    return
                advance(job)
                if targets not in jobs or isinstance(job["action"], RetryDelay):
                    return
            action = job["action"]
            if not isinstance(action, RequestCall):
                raise CheckpointStorageError("Estado interno de solicitação inválido.")
            if any(action.scope & item[1].scope for item in futures.values()):
                return
            timeout = action.timeout if action.deadline is None else min(action.timeout, action.deadline - time.monotonic())
            if timeout <= 0:
                raise v.AnvisaError("IA: tempo total excedido; o progresso validado foi preservado no checkpoint.")
            used[targets] = used.get(targets, 0) + 1
            future = executor.submit(v._request, action.messages, action.key, timeout)
            futures[future] = (job, action)
            job["busy"] = True
            for waiting in jobs.values():
                if isinstance(waiting["action"], RetryDelay):
                    waiting["delay_had_peers"] = True
            self.stats["chamadas_simultaneas_maximas"] = max(self.stats["chamadas_simultaneas_maximas"], len(futures))

        try:
            with ThreadPoolExecutor(max_workers=max_parallel, thread_name_prefix="anvisa-lote") as executor:
                while True:
                    if failure is None:
                        try:
                            # A amostra é uma ferramenta interna optativa; a API nunca fornece orçamento.
                            for targets, job in list(jobs.items()):
                                if not job["busy"] and not allowed(targets):
                                    job["steps"].close()
                                    jobs.pop(targets)
                            # Lotes suspensos conservam gerador, contexto e orçamentos,
                            # mas somente chamadas em voo ocupam as vagas da API.
                            for job in list(jobs.values()):
                                dispatch(job, executor)
                            while len(futures) < max_parallel and (max_parallel > 1 or not jobs):
                                candidate = next((row for row in self.state["pending"]
                                    if tuple(row["targets"]) not in jobs and allowed(tuple(row["targets"]))
                                    and all(not scope(row, self.pages) & scope(self.task(other), self.pages) for other in jobs)), None)
                                if candidate is None:
                                    break
                                targets = tuple(candidate["targets"])
                                job = {"targets": targets, "steps": make_steps(copy.deepcopy(candidate), self),
                                       "busy": False, "action": None, "ready_at": 0}
                                jobs[targets] = job
                                advance(job, initial=True)
                                if targets in jobs:
                                    dispatch(job, executor)
                        except Exception as exc:
                            failure = exc
                    if not futures:
                        if failure is not None:
                            raise failure
                        waiting = [job for job in jobs.values() if isinstance(job["action"], RetryDelay)]
                        if waiting:
                            job = min(waiting, key=lambda item: item["ready_at"])
                            delay = max(0, job["ready_at"] - time.monotonic()) if job["delay_had_peers"] else job["action"].seconds
                            time.sleep(delay)
                            advance(job)
                            continue
                        if jobs:
                            raise CheckpointStorageError("Fila suspensa sem solicitação ou retentativa elegível.")
                        if self.state["pending"]:
                            if sample_budget is not None:
                                raise AnalysisSampleComplete()
                            raise CheckpointStorageError("Fila de lotes sem solicitação elegível.")
                        break
                    delays = [job["ready_at"] - time.monotonic() for job in jobs.values()
                              if failure is None and len(futures) < max_parallel and not job["busy"] and isinstance(job["action"], RetryDelay)]
                    completed, _ = wait(futures, timeout=max(0, min(delays)) if delays else None,
                                        return_when=FIRST_COMPLETED)
                    for future in sorted(completed, key=lambda item: futures[item][0]["targets"]):
                        job, _ = futures.pop(future)
                        job["busy"] = False
                        try:
                            result, error = future.result(), None
                        except Exception as exc:
                            result, error = None, exc
                        if isinstance(failure, (CheckpointStorageError, DiagnosticStorageError)):
                            if isinstance(result, v.ModelResult):
                                result.validation_status = "nao_validada_apos_falha_armazenamento"
                            continue  # Armazenamento incerto impede novas promoções.
                        try:
                            advance(job, result, error)
                        except Exception as exc:
                            if failure is None or isinstance(exc, (CheckpointStorageError, DiagnosticStorageError)):
                                failure = exc
                    # Após erro, drenar chamadas já em voo e salvar respostas válidas, sem despachar outras.
        finally:
            for job in jobs.values():
                job["steps"].close()
        return self.state, self.stats
