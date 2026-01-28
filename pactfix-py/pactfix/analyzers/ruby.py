"""Ruby code analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


def analyze_ruby(code: str) -> AnalysisResult:
    """Analyze Ruby code for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split('\n')
    fixed_lines = lines.copy()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        indent_str = line[:indent]

        # RUBY001: Using == instead of .eql? or .equal?
        if '== nil' in stripped:
            warnings.append(Issue(i, 1, 'RUBY001', 'Użyj .nil? zamiast == nil'))
            fixed = stripped.replace('== nil', '.nil?')
            fixes.append(Fix(i, 'Zamieniono == nil na .nil?', stripped, fixed))
            fixed_lines[i-1] = indent_str + fixed

        # RUBY002: Using rescue without exception class
        if re.match(r'^\s*rescue\s*$', stripped):
            warnings.append(Issue(i, 1, 'RUBY002', 'rescue bez klasy wyjątku łapie StandardError'))

        # RUBY003: Rescuing Exception (catches everything including system exceptions)
        if 'rescue Exception' in stripped:
            errors.append(Issue(i, 1, 'RUBY003', 'rescue Exception łapie także SystemExit i Interrupt'))

        # RUBY004: Using puts/print for logging
        if stripped.startswith('puts ') or stripped.startswith('print '):
            warnings.append(Issue(i, 1, 'RUBY004', 'puts/print - użyj Loggera'))

        # RUBY005: Hardcoded credentials
        secret_patterns = ['password', 'secret', 'api_key', 'token']
        for pattern in secret_patterns:
            if re.search(rf'{pattern}\s*=\s*["\'][^"\']+["\']', stripped, re.I):
                errors.append(Issue(i, 1, 'RUBY005', f'Hardcoded {pattern}'))

        # RUBY006: Using eval
        if 'eval(' in stripped or 'eval ' in stripped:
            errors.append(Issue(i, 1, 'RUBY006', 'eval() jest niebezpieczne'))

        # RUBY007: Using send with user input
        if '.send(' in stripped:
            warnings.append(Issue(i, 1, 'RUBY007', 'send() z zewnętrznym inputem może być niebezpieczne'))

        # RUBY008: SQL injection risk
        if '.where(' in stripped or '.find_by_sql' in stripped:
            if '#{' in stripped or '+' in stripped:
                errors.append(Issue(i, 1, 'RUBY008', 'Potencjalny SQL injection - użyj placeholderów'))

        # RUBY009: Using class variables @@
        if '@@' in stripped:
            warnings.append(Issue(i, 1, 'RUBY009', 'Zmienne klasowe @@ - rozważ class instance variables'))

        # RUBY010: Not using freeze for constants
        if re.match(r'^[A-Z_]+\s*=\s*["\']', stripped) and '.freeze' not in stripped:
            warnings.append(Issue(i, 1, 'RUBY010', 'String constant bez .freeze'))
            fixed = stripped.rstrip() + '.freeze'
            fixes.append(Fix(i, 'Dodano .freeze do stałej', stripped, fixed))
            fixed_lines[i-1] = indent_str + fixed

        # RUBY011: Using return in proc
        if 'proc' in '\n'.join(lines[max(0,i-5):i]).lower() and 'return ' in stripped:
            warnings.append(Issue(i, 1, 'RUBY011', 'return w Proc może powodować problemy - użyj lambda'))

        # RUBY012: Method too long
        if stripped.startswith('def '):
            # Count lines until end
            end_count = 0
            for j in range(i, min(i+50, len(lines))):
                if lines[j].strip() == 'end':
                    end_count = j - i
                    break
            if end_count > 20:
                warnings.append(Issue(i, 1, 'RUBY012', 'Metoda zbyt długa - rozważ refactoring'))

        # RUBY013: Using begin/rescue/end for control flow
        if 'begin' in stripped and 'rescue' in '\n'.join(lines[i:i+5]):
            warnings.append(Issue(i, 1, 'RUBY013', 'begin/rescue do kontroli przepływu - użyj warunku'))

        # RUBY014: Double negation
        if '!!' in stripped:
            warnings.append(Issue(i, 1, 'RUBY014', 'Podwójna negacja - użyj .present? lub !!var'))

    return AnalysisResult('ruby', code, '\n'.join(fixed_lines), errors, warnings, fixes)
