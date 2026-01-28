"""Go code analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


def analyze_go(code: str) -> AnalysisResult:
    """Analyze Go code for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split('\n')
    fixed_lines = lines.copy()

    in_func = False
    has_error_check = False

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        indent_str = line[:indent]

        # GO001: Unchecked error
        if ', err :=' in stripped or ', err =' in stripped:
            # Check next few lines for error handling
            next_lines = '\n'.join(lines[i:i+3])
            if 'if err != nil' not in next_lines and '_ = err' not in next_lines:
                warnings.append(Issue(i, 1, 'GO001', 'Błąd nie jest sprawdzany - dodaj if err != nil'))

        # GO002: Using panic in library code
        if 'panic(' in stripped and 'func main' not in code[:code.find(stripped)]:
            warnings.append(Issue(i, 1, 'GO002', 'panic() w kodzie biblioteki - użyj error'))

        # GO003: Empty error message
        if 'errors.New("")' in stripped or "errors.New('')" in stripped:
            errors.append(Issue(i, 1, 'GO003', 'Pusty komunikat błędu'))

        # GO004: fmt.Sprintf without format args
        if 'fmt.Sprintf(' in stripped and '%' not in stripped:
            warnings.append(Issue(i, 1, 'GO004', 'fmt.Sprintf bez argumentów formatowania - użyj zwykłego stringa'))

        # GO005: Goroutine without sync
        if 'go func()' in stripped or re.search(r'go\s+\w+\(', stripped):
            if 'sync.' not in code and 'chan ' not in code and '<-' not in code:
                warnings.append(Issue(i, 1, 'GO005', 'Goroutine bez synchronizacji'))

        # GO006: Using == for slice comparison
        if re.search(r'\[\].*==\s*nil', stripped) is None and re.search(r'==\s*\[\]', stripped):
            errors.append(Issue(i, 1, 'GO006', 'Nie można porównywać slice\'ów przez =='))

        # GO007: Defer in loop
        if stripped.startswith('defer ') and any('for ' in lines[j] for j in range(max(0, i-10), i)):
            warnings.append(Issue(i, 1, 'GO007', 'defer w pętli - może prowadzić do wycieków zasobów'))

        # GO008: Using time.Sleep in production
        if 'time.Sleep' in stripped:
            warnings.append(Issue(i, 1, 'GO008', 'time.Sleep w kodzie produkcyjnym - rozważ context.WithTimeout'))

        # GO009: Hardcoded credentials
        secret_patterns = ['password', 'secret', 'apikey', 'api_key', 'token']
        for pattern in secret_patterns:
            if re.search(rf'{pattern}\s*[:=]\s*["\'][^"\']+["\']', stripped, re.I):
                errors.append(Issue(i, 1, 'GO009', f'Hardcoded {pattern} - użyj zmiennych środowiskowych'))

        # GO010: SQL injection risk
        if 'db.Query(' in stripped or 'db.Exec(' in stripped:
            if '+' in stripped or 'fmt.Sprintf' in stripped:
                errors.append(Issue(i, 1, 'GO010', 'Potencjalny SQL injection - użyj prepared statements'))

        # GO011: Context as struct field
        if 'context.Context' in stripped and 'struct' in code[:code.find(stripped)]:
            warnings.append(Issue(i, 1, 'GO011', 'Context nie powinien być polem struktury'))

        # GO012: Using init() function
        if stripped.startswith('func init()'):
            warnings.append(Issue(i, 1, 'GO012', 'Unikaj init() - utrudnia testowanie'))

        # GO013: Missing package comment
        if stripped.startswith('package ') and i == 1:
            if i >= len(lines) or not lines[0].strip().startswith('//'):
                warnings.append(Issue(i, 1, 'GO013', 'Brak komentarza pakietu'))

        # GO014: Using interface{} instead of any
        if 'interface{}' in stripped:
            warnings.append(Issue(i, 1, 'GO014', 'Użyj any zamiast interface{} (Go 1.18+)'))
            fixed = stripped.replace('interface{}', 'any')
            fixes.append(Fix(i, 'Zamieniono interface{} na any', stripped, fixed))
            fixed_lines[i-1] = indent_str + fixed

    return AnalysisResult('go', code, '\n'.join(fixed_lines), errors, warnings, fixes)
