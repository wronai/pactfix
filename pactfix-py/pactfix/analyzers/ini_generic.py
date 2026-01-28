"""Generic INI analyzer."""

import configparser
import re
from typing import List

from ..analyzer import Issue, Fix, AnalysisResult


def analyze_ini(code: str) -> AnalysisResult:
    """Analyze INI/CFG for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []

    fixed_code = code

    # INI002: Tabs
    if '\t' in fixed_code:
        warnings.append(Issue(1, 1, 'INI002', 'Tabulatory w INI - użyj spacji'))
        new_code = fixed_code.replace('\t', '  ')
        fixes.append(Fix(1, 'Zamieniono tabulatory na spacje', '\\t', '  '))
        fixed_code = new_code

    # INI003: Trailing whitespace
    if any(line.rstrip() != line for line in fixed_code.split('\n')):
        warnings.append(Issue(1, 1, 'INI003', 'Trailing whitespace w INI'))
        new_code = '\n'.join(line.rstrip() for line in fixed_code.split('\n'))
        if new_code != fixed_code:
            fixes.append(Fix(1, 'Usunięto trailing whitespace', '', ''))
            fixed_code = new_code

    parser = configparser.ConfigParser()

    # INI001: Missing section header at the beginning
    if not fixed_code.lstrip().startswith('[DEFAULT]'):
        first_meaningful = None
        for idx, line in enumerate(fixed_code.split('\n')):
            s = line.strip()
            if not s:
                continue
            if s.startswith(';') or s.startswith('#'):
                continue
            first_meaningful = s
            break

        if first_meaningful is not None and not first_meaningful.startswith('['):
            errors.append(Issue(1, 1, 'INI001', 'Brak nagłówka sekcji na początku pliku - dodano [DEFAULT]'))
            fixed_code = '[DEFAULT]\n' + fixed_code
            fixes.append(Fix(1, 'Dodano [DEFAULT] na początku pliku', '', '[DEFAULT]'))

    try:
        parser.read_string(fixed_code)
    except configparser.MissingSectionHeaderError as e:
        errors.append(Issue(1, 1, 'INI001', f'Brak sekcji INI: {e}'))
    except configparser.ParsingError as e:
        errors.append(Issue(1, 1, 'INI004', f'Błąd parsowania INI: {e}'))

    return AnalysisResult('ini', code, fixed_code, errors, warnings, fixes)
