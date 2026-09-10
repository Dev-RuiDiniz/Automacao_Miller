from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from infra.dou.collector import DEFAULT_PDF_TYPES, DEFAULT_XML_TYPES, DouCollector


def main() -> int:
    parser = argparse.ArgumentParser(description="Baixa o corpus oficial do DOU para staging protegido")
    parser.add_argument("--start", default="2026-08-12")
    parser.add_argument("--end", default="2026-09-10")
    parser.add_argument("--output", type=Path, default=Path("staging/dou-2026-08-12_2026-09-10"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    manifest = DouCollector(args.output).collect(date.fromisoformat(args.start), date.fromisoformat(args.end), DEFAULT_PDF_TYPES, DEFAULT_XML_TYPES, args.dry_run)
    print(f"Itens planejados: {len(manifest['items'])}; baixados: {manifest['counts'].get('downloaded', 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
