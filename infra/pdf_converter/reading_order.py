"""Ordem espacial do texto: regiões, colunas e tabelas, sem regras por documento."""
from __future__ import annotations

from collections import Counter
from statistics import median
from typing import Any

WORD_X_TOLERANCE_RATIO = 0.2


def _gaps(items: list[dict], start: str, end: str) -> list[tuple[float, float]]:
    intervals = sorted((item[start], item[end]) for item in items)
    if not intervals:
        return []
    previous = intervals[0][1]
    gaps = []
    for left, right in intervals[1:]:
        if left > previous:
            gaps.append((previous, left))
        previous = max(previous, right)
    return gaps


def _rows(words: list[dict]) -> list[list[dict]]:
    rows: list[list[dict]] = []
    for word in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if rows and abs(word["top"] - rows[-1][0]["top"]) <= 3:
            rows[-1].append(word)
        else:
            rows.append([word])
    return [sorted(row, key=lambda w: w["x0"]) for row in rows]


def _line_text(words: list[dict]) -> str:
    parts = []
    previous = None
    for word in words:
        if previous is not None:
            # Mantém separação visível entre células sem fabricar conteúdo.
            gap = word["x0"] - previous["x1"]
            parts.append("    " if gap > 10 else " ")
        parts.append(word["text"])
        previous = word
    return "".join(parts)


def _render_rows(items: list[dict]) -> str:
    return "\n".join(_line_text(row) for row in _rows(items))


def _aligned_short_cells(first: list[dict], second: list[dict]) -> bool:
    """Sinal conservador de tabela sem bordas, não comprovação semântica."""
    left_rows, right_rows = _rows(first), _rows(second)
    matches = 0
    for left in left_rows:
        for right in right_rows:
            if abs(left[0]["top"] - right[0]["top"]) > 3:
                continue
            if all(len(_line_text(row)) <= 32 and len(row) <= 5 for row in (left, right)):
                matches += 1
                break
    return matches >= 3 and matches / max(len(left_rows), len(right_rows)) >= 0.8


def _ordered_regions(
    items: list[dict], font_height: float, depth: int = 0,
    layout_warnings: list[str] | None = None,
) -> list[list[dict]]:
    """XY-cut: separa espaços vazios reais, sem cortar caracteres ou tabelas."""
    if len(items) < 2:
        return [items]
    if depth >= 40:
        if layout_warnings is not None:
            layout_warnings.append(
                "limite de segmentação espacial atingido; confira a ordem de leitura no PDF."
            )
        return [items]

    # Uma faixa vertical contínua separa colunas inteiras. Tabelas são objetos
    # indivisíveis aqui, impedindo separar suas células em colunas de prosa.
    for left, right in sorted(_gaps(items, "x0", "x1"), key=lambda g: g[1] - g[0], reverse=True):
        if right - left < max(12, font_height * 1.5):
            continue
        split = (left + right) / 2
        first = [item for item in items if item["x1"] <= split]
        second = [item for item in items if item["x0"] >= split]
        if len(_rows(first)) < 3 or len(_rows(second)) < 3:
            continue
        if _aligned_short_cells(first, second):
            if layout_warnings is not None:
                layout_warnings.append(
                    "possível tabela sem bordas ou colunas curtas alinhadas; "
                    "texto mantido por linhas. Confira os vínculos entre células no PDF."
                )
            return [items]
        return (_ordered_regions(first, font_height, depth + 1, layout_warnings)
                + _ordered_regions(second, font_height, depth + 1, layout_warnings))

    # Cabeçalhos, tabelas transversais e mudanças de layout bloqueiam o corte
    # vertical. Separa suas faixas antes de procurar colunas em cada região.
    gaps = _gaps(items, "top", "bottom")
    if gaps:
        top, bottom = max(gaps, key=lambda g: g[1] - g[0])
        if bottom - top > font_height * 0.4:
            split = (top + bottom) / 2
            first = [item for item in items if item["bottom"] <= split]
            second = [item for item in items if item["top"] >= split]
            return (_ordered_regions(first, font_height, depth + 1, layout_warnings)
                    + _ordered_regions(second, font_height, depth + 1, layout_warnings))
    return [items]


def extract_ordered_text(
    page: Any, layout_warnings: list[str] | None = None,
) -> tuple[str, list[Any]]:
    """Lê geometria da página; falha explicitamente se houver perda de caracteres."""
    # O limiar acompanha o tamanho da fonte para não juntar palavras em texto
    # comprimido, mantendo os caracteres e os identificadores publicados.
    words = page.extract_words(
        use_text_flow=False, return_chars=True, expand_ligatures=False,
        x_tolerance_ratio=WORD_X_TOLERANCE_RATIO,
    )
    original = Counter(c["text"] for c in page.chars if c["text"].strip())
    recovered = Counter(c["text"] for w in words for c in w["chars"] if c["text"].strip())
    if original != recovered:
        raise ValueError("A leitura espacial não preservou todos os caracteres")
    if not words:
        return "", []
    if any(not c.get("upright", True) for c in page.chars):
        raise ValueError("Texto rotacionado requer conferência da ordem de leitura")

    height = median(w["bottom"] - w["top"] for w in words)
    tables = page.find_tables() if len(page.edges) >= 4 else []
    items = list(words)
    # Preserva o texto original da tabela por linhas no próprio local. Sua
    # versão Markdown estruturada é suplementar, com aviso, como no contrato.
    for table in tables:
        x0, top, x1, bottom = table.bbox
        if len(table.rows) < 2 or len(table.columns) < 2:
            continue
        inside = [w for w in items if "table" not in w
                  and x0 <= (w["x0"] + w["x1"]) / 2 <= x1
                  and top <= (w["top"] + w["bottom"]) / 2 <= bottom]
        if not inside:
            continue
        identities = {id(w) for w in inside}
        items = [w for w in items if id(w) not in identities]
        items.append({"x0": min(x0, min(w["x0"] for w in inside)),
                      "top": min(top, min(w["top"] for w in inside)),
                      "x1": max(x1, max(w["x1"] for w in inside)),
                      "bottom": max(bottom, max(w["bottom"] for w in inside)),
                      "text": _render_rows(inside), "table": True})
    regions = _ordered_regions(items, height, layout_warnings=layout_warnings)
    rendered = "\n\n".join(_render_rows(region) for region in regions if region)
    expected = Counter(c for word in words for c in word["text"] if not c.isspace())
    if Counter(c for c in rendered if not c.isspace()) != expected:
        raise ValueError("A reorganização espacial alterou caracteres do documento")
    return rendered, tables
