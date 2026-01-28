"""Generic JSON analyzer."""

import json
import re
from typing import List, Any, Tuple

from ..analyzer import Issue, Fix, AnalysisResult


def _pos_to_line_col(code: str, pos: int) -> Tuple[int, int]:
    if pos is None or pos < 0:
        return 1, 1
    prefix = code[:pos]
    line = prefix.count('\n') + 1
    col = len(prefix.rsplit('\n', 1)[-1]) + 1
    return line, col


def _load_with_duplicates(code: str) -> Tuple[Any, List[str]]:
    duplicates: List[str] = []

    def hook(pairs):
        obj = {}
        for k, v in pairs:
            if k in obj:
                duplicates.append(k)
            obj[k] = v
        return obj

    return json.loads(code, object_pairs_hook=hook), duplicates


def analyze_json(code: str) -> AnalysisResult:
    """Analyze JSON for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []

    fixed_code = code

    # JSON002: Tabs
    if '\t' in fixed_code:
        warnings.append(Issue(1, 1, 'JSON002', 'Tabulatory w JSON - użyj spacji'))
        new_code = fixed_code.replace('\t', '  ')
        fixes.append(Fix(1, 'Zamieniono tabulatory na spacje', '\\t', '  '))
        fixed_code = new_code

    # JSON003: Trailing whitespace
    if any(line.rstrip() != line for line in fixed_code.split('\n')):
        warnings.append(Issue(1, 1, 'JSON003', 'Trailing whitespace w JSON'))
        new_code = '\n'.join(line.rstrip() for line in fixed_code.split('\n'))
        if new_code != fixed_code:
            fixes.append(Fix(1, 'Usunięto trailing whitespace', '', ''))
            fixed_code = new_code

    # JSON004: Python-style booleans/null
    if re.search(r'\b(True|False|None)\b', fixed_code):
        errors.append(Issue(1, 1, 'JSON004', 'Wykryto True/False/None - JSON wymaga true/false/null'))
        new_code = re.sub(r'\bTrue\b', 'true', fixed_code)
        new_code = re.sub(r'\bFalse\b', 'false', new_code)
        new_code = re.sub(r'\bNone\b', 'null', new_code)
        if new_code != fixed_code:
            fixes.append(Fix(1, 'Zamieniono True/False/None na true/false/null', '', ''))
            fixed_code = new_code

    # JSON005: Trailing commas
    if re.search(r',\s*[\]}]', fixed_code):
        warnings.append(Issue(1, 1, 'JSON005', 'Trailing comma w JSON - usuń przecinek przed } lub ]'))
        new_code = re.sub(r',\s*([\]}])', r'\1', fixed_code)
        if new_code != fixed_code:
            fixes.append(Fix(1, 'Usunięto trailing commas', '', ''))
            fixed_code = new_code

    # JSON001: Parse validation
    try:
        _, dups = _load_with_duplicates(fixed_code)
        if dups:
            warnings.append(Issue(1, 1, 'JSON006', f'Duplikaty kluczy w JSON: {", ".join(sorted(set(dups)))}'))
    except json.JSONDecodeError as e:
        line, col = getattr(e, 'lineno', 1), getattr(e, 'colno', 1)
        # Fallback when lineno/colno are missing
        if (line, col) == (1, 1) and getattr(e, 'pos', None) is not None:
            line, col = _pos_to_line_col(fixed_code, e.pos)

        errors.append(Issue(line, col, 'JSON001', f'Nieprawidłowy JSON: {e.msg}'))

    return AnalysisResult('json', code, fixed_code, errors, warnings, fixes)
