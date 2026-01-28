"""Generic TOML analyzer."""

import re
from typing import List

try:
    import tomllib  # Python 3.11+
except Exception:  # pragma: no cover
    tomllib = None

from ..analyzer import Issue, Fix, AnalysisResult


def analyze_toml(code: str) -> AnalysisResult:
    """Analyze TOML for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []

    fixed_code = code

    # TOML002: Tabs
    if '\t' in fixed_code:
        warnings.append(Issue(1, 1, 'TOML002', 'Tabulatory w TOML - użyj spacji'))
        new_code = fixed_code.replace('\t', '  ')
        fixes.append(Fix(1, 'Zamieniono tabulatory na spacje', '\\t', '  '))
        fixed_code = new_code

    # TOML003: Trailing whitespace
    if any(line.rstrip() != line for line in fixed_code.split('\n')):
        warnings.append(Issue(1, 1, 'TOML003', 'Trailing whitespace w TOML'))
        new_code = '\n'.join(line.rstrip() for line in fixed_code.split('\n'))
        if new_code != fixed_code:
            fixes.append(Fix(1, 'Usunięto trailing whitespace', '', ''))
            fixed_code = new_code

    # TOML004: Bare keys with spaces (warn)
    if re.search(r'^\s*[A-Za-z0-9_.-]+\s+[A-Za-z0-9_.-]+\s*=\s*', fixed_code, re.MULTILINE):
        warnings.append(Issue(1, 1, 'TOML004', 'Podejrzany klucz z odstępami przed = (sprawdź składnię TOML)'))

    if tomllib is None:
        warnings.append(Issue(1, 1, 'TOML001', 'Brak tomllib (Python < 3.11) - pomijam walidację TOML'))
        return AnalysisResult('toml', code, fixed_code, errors, warnings, fixes)

    try:
        tomllib.loads(fixed_code)
    except Exception as e:
        # tomllib exceptions do not expose reliable line/col consistently
        errors.append(Issue(1, 1, 'TOML001', f'Nieprawidłowy TOML: {e}'))

    return AnalysisResult('toml', code, fixed_code, errors, warnings, fixes)
