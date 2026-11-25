"""Migração explícita do checkpoint V8 anterior, sem rede ou chamada de IA.

Executar como módulo somente pelo operador, com backup e a análise parada.
O estado anterior não é alterado. Não há migração automática na rota HTTP.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

from . import anvisa_v8 as v, incremental as inc
from .analysis_checkpoint import AnalysisCheckpoint, CheckpointStorageError, CheckpointBusyError, encode
from . import context_window as ctx

# Implementações de origem reconhecidas; não aceitar hashes arbitrários.
LEGACY_IMPLEMENTATION = "52e3ea8d7561ecfd59cecb12fa969f42630a7c83489c68fc549d2ec7ffb3c7a6"
LEGACY_INSTRUCTIONS = "9221cba02b07885227963caa4f6fe1cfa5ae065fa30e067aa325f6256e858c08"
REVIEW_IMPLEMENTATION = "993245953dbd369db2dac6db41a73eccc3441bc40b01216d936c01a77d4a6284"
REVIEW_INSTRUCTIONS = "a86d84de63bb32ab0bf7df8b2c98d291f26708b64906bd3208e34715d473a020"
WINDOW_IMPLEMENTATION = "e898335d7b3cb03c44c12acb2b50b38ceff2c2bf83a879224bdde0f0d2c5c375"
WINDOW_INSTRUCTIONS = "780d7cb35ca427c08f8c35d005594578bbfc323e991c54ffe2602bfe7486ba50"
SEARCH_IMPLEMENTATION = "dda4b9c88c867c69afee2054ac3a930f45f69a13ba992d69c1cbd93bafc80858"
INDEX_IMPLEMENTATION = "e138d5524519a0d62256d077f32552a855bcabd1ec9020fcc49ca5f7a02019fa"
INDEX_INSTRUCTIONS = "e7bc894b9ee50c221ef193bdf754c076897813430cc523acfad12ce97cd87792"
NO_DEADLINE_IMPLEMENTATION = "31b10ae5608efed11f7ce81a71e3cd45f9ef5657d34c453f31e513ff3f8ad52b"
RECOVERY_IMPLEMENTATION = "80c8d2ee5d36d0ae2902904e9812678cc2dd4a44af7681ccd5487f106a09b5a9"
COMPACT_IMPLEMENTATION = "410e223c78afda3d6c17b1d6232b6c5dbf843e800b972f4e088d9d3799a374d1"
COMPACT_INSTRUCTIONS = "bce46045f2c2f2e61795d47bd86c06bb5c5fd3afca41c99254b00ffecf443ac5"
EIGHT_IMPLEMENTATION = "dc6beae4179152963555067075c78ff3084bbb1506ad341bf65d40319297817e"
EIGHT_INSTRUCTIONS = "744698fe4fc602b58679df82989f78cd76496521100a7875782b04a8355731ee"
PARALLEL_IMPLEMENTATION = "6aeb38e8fea02ca2683f5de793fd48ffdd35283361cd00d5525e5753717558b0"
ADAPTIVE_IMPLEMENTATION = "40fa4011ff811de40645d1eeae40efa38394729269a0b958de3ba32aee7358aa"
ADAPTIVE_INSTRUCTIONS = "d4ca50407d9a1d97d0ee8888140fd37a93fad7218160d1a7054a7bb3cd93d397"
QUEUE_IMPLEMENTATION = "e83a941e242794fea02740a026f4e2dec7ae1a65f266463aeb3e826b93c21b5c"
SHARED_FIELDS_IMPLEMENTATION = "632770b707fd518b7204ed992e093ba0b4c8423c691ed6bebd18bb77a27dca55"
SHARED_FIELDS_INSTRUCTIONS = "c368ae552044ba2a1ef17b4d2c4000fb089dbbc1b233adc9dfada174d45d27c4"
EVIDENCE_LIMITS_IMPLEMENTATION = "2856f024795ea974eea1b8b51ce8a6840c70d80d3ce281a4a361ad8a5e7cd717"
EVIDENCE_LIMITS_INSTRUCTIONS = "43cdff0461ade11ce3106778bfffdd12df0aea3eed4fc868b95adefbb8474b05"
REREAD_IMPLEMENTATION = "2d82eb1598f6eab4db3e1baecd49aed88b5686f6f9c80fcd0865e4fdaa1c2cf5"
REREAD_INSTRUCTIONS = "1c26ea5b1e7ad1f0eb152da397f1a69741a00a1e8b492633f25f161dac11c250"


def legacy_identity(source_hash, page_count, version=1):
    if version not in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}:
        raise CheckpointStorageError("Implementação de origem não reconhecida.")
    return {"schema": min(version, 3), "source_sha256": source_hash, "pages": page_count,
            "model": "openai/gpt-6.1-terra", "prompt_sha256": v.PROMPT_HASH,
            "instructions_sha256": {1: LEGACY_INSTRUCTIONS, 2: REVIEW_INSTRUCTIONS, 3: WINDOW_INSTRUCTIONS,
                                    4: WINDOW_INSTRUCTIONS, 5: INDEX_INSTRUCTIONS, 6: INDEX_INSTRUCTIONS,
                                    7: INDEX_INSTRUCTIONS, 8: COMPACT_INSTRUCTIONS, 9: EIGHT_INSTRUCTIONS,
                                    10: EIGHT_INSTRUCTIONS, 11: ADAPTIVE_INSTRUCTIONS, 12: ADAPTIVE_INSTRUCTIONS,
                                    13: SHARED_FIELDS_INSTRUCTIONS, 14: EVIDENCE_LIMITS_INSTRUCTIONS,
                                    15: REREAD_INSTRUCTIONS}[version],
            "implementation_sha256": {1: LEGACY_IMPLEMENTATION, 2: REVIEW_IMPLEMENTATION, 3: WINDOW_IMPLEMENTATION,
                                      4: SEARCH_IMPLEMENTATION, 5: INDEX_IMPLEMENTATION, 6: NO_DEADLINE_IMPLEMENTATION,
                                      7: RECOVERY_IMPLEMENTATION, 8: COMPACT_IMPLEMENTATION, 9: EIGHT_IMPLEMENTATION,
                                      10: PARALLEL_IMPLEMENTATION, 11: ADAPTIVE_IMPLEMENTATION, 12: QUEUE_IMPLEMENTATION,
                                      13: SHARED_FIELDS_IMPLEMENTATION, 14: EVIDENCE_LIMITS_IMPLEMENTATION,
                                      15: REREAD_IMPLEMENTATION}[version]}


def migrate(markdown: str, scope: str, source_key: str) -> dict:
    if (not re.fullmatch(r"[a-f0-9]{64}", source_key)
            or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", scope)):
        raise CheckpointStorageError("Origem ou protocolo inválido para migração.")
    source_hash = hashlib.sha256(markdown.encode()).hexdigest()
    markers = list(v.PAGE.finditer(markdown))
    if not markers or [int(m[1]) for m in markers] != list(range(1, len(markers) + 1)):
        raise CheckpointStorageError("Fonte paginada inválida para migração.")
    pages = {i + 1: markdown[m.end():markers[i + 1].start() if i + 1 < len(markers) else len(markdown)]
             for i, m in enumerate(markers)}
    if (any(not text.strip() or "_Nenhum conteúdo textual extraível nesta página._" in text for text in pages.values())
            or hashlib.sha256(v.PROMPT_PATH.read_bytes()).hexdigest() != v.PROMPT_HASH):
        raise CheckpointStorageError("Fonte ou V8 inválido para migração.")
    sources = [AnalysisCheckpoint(legacy_identity(source_hash, len(pages), version), scope) for version in range(1, 16)]
    old = next((source for source in sources if source.key == source_key), None)
    current = AnalysisCheckpoint(inc.identity(source_hash, len(pages)), scope)
    if old is None or old.identity["model"] != current.identity["model"] or not old.path.is_file():
        raise CheckpointStorageError("Checkpoint de origem não corresponde à versão, fonte ou protocolo autorizados.")
    with current, old:
        previous = old.load()
        if (not isinstance(previous, dict) or type(previous.get("schema")) is not int
                or previous["schema"] != old.identity["schema"] or not isinstance(previous.get("pending"), list)):
            raise CheckpointStorageError("Checkpoint anterior ausente ou incompatível.")
        converted = copy.deepcopy(previous)
        converted["schema"] = inc.PROTOCOL_VERSION
        for task in converted["pending"]:
            if not isinstance(task, dict) or (previous["schema"] < 3 and "context" in task):
                raise CheckpointStorageError("Formato anterior inesperado.")
            if previous["schema"] == 1:
                # A primeira versão só guardava fichas concluídas; não promover rascunhos.
                if "drafts" in task or "review_history" in task:
                    raise CheckpointStorageError("Formato anterior inesperado.")
                task.update(drafts=[], review_history=[])
        if previous["schema"] < 3:
            # Revalidar antes de reconstituir a fila das versões sem controle de entrega.
            for task in converted["pending"]:
                task["context"] = ctx.empty()
            inc._validated_state(converted, pages)
            for task in converted["pending"]:
                task.pop("context")
            converted["pending"] = [ctx.from_legacy(task, pages) for task in converted["pending"]]
        # O formato 3 conserva integralmente contexto, entregas, buscas e revisões.
        inc._validated_state(converted, pages)
        if converted["pending"]:
            ctx.build(converted["pending"][0], pages, inc.adaptive.limit(converted["pending"][0]))
        provenance = {"source_key": source_key, "source_state_sha256": hashlib.sha256(encode(previous)).hexdigest(),
                      "source_identity": old.identity}
        converted["migration"] = provenance
        existing = current.load()
        if existing is not None:
            inc._validated_state(existing, pages)
            if existing.get("migration") != provenance:
                raise CheckpointStorageError("Destino já possui outro estado; migração não pode sobrescrevê-lo.")
            state, status = existing, "ja_migrado"
        else:
            current.save(converted)
            state, status = converted, "migrado"
    return {"status": status, "source_key": source_key, "destination_key": current.key,
            "completed_lots": len(state["completed"]),
            "completed_pages": [n for task in state["completed"] for n in task["targets"]]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--markdown", required=True, type=Path)
    parser.add_argument("--submission-id", required=True)
    parser.add_argument("--from-key", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(migrate(args.markdown.read_text(), args.submission_id, args.from_key), ensure_ascii=False))
    except (OSError, ValueError, KeyError, TypeError, CheckpointBusyError):
        parser.exit(1, "Migração interrompida: fonte, estado ou bloqueio incompatível; nenhuma chamada de IA realizada.\n")


if __name__ == "__main__":
    main()
