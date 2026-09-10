from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from infra.dou.package import create_package


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera Markdown, PDFs semanais, manifesto e ZIP do corpus DOU")
    parser.add_argument("--staging", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dataset-manifest", type=Path)
    args = parser.parse_args()
    print(create_package(args.staging, args.output, args.dataset_manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
