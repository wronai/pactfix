"""Rust code analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


def analyze_rust(code: str) -> AnalysisResult:
    """Analyze Rust code for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split('\n')
    fixed_lines = lines.copy()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        indent_str = line[:indent]

        # RUST001: Using unwrap() in production code
        if '.unwrap()' in stripped:
            warnings.append(Issue(i, 1, 'RUST001', 'unwrap() może spowodować panic - użyj ? lub match'))

        # RUST002: Using expect() without good message
        if '.expect("' in stripped:
            match = re.search(r'\.expect\("([^"]*)"\)', stripped)
            if match and len(match.group(1)) < 10:
                warnings.append(Issue(i, 1, 'RUST002', 'expect() z krótkim opisem - dodaj szczegółową wiadomość'))

        # RUST003: clone() usage - potential performance issue
        if '.clone()' in stripped:
            warnings.append(Issue(i, 1, 'RUST003', 'clone() może być kosztowne - rozważ borrowing'))

        # RUST004: Using panic! in library code
        if 'panic!' in stripped and 'fn main' not in code[:code.find(stripped)]:
            warnings.append(Issue(i, 1, 'RUST004', 'panic! w kodzie biblioteki - zwróć Result'))

        # RUST005: Unnecessary mut
        if 'let mut ' in stripped:
            var_match = re.search(r'let mut (\w+)', stripped)
            if var_match:
                var_name = var_match.group(1)
                rest_of_code = '\n'.join(lines[i:])
                if f'{var_name} =' not in rest_of_code and f'{var_name}.' not in rest_of_code:
                    warnings.append(Issue(i, 1, 'RUST005', f'Niepotrzebny mut dla {var_name}'))

        # RUST006: Using String instead of &str in function parameters
        if re.search(r'fn\s+\w+\([^)]*:\s*String[,)]', stripped):
            warnings.append(Issue(i, 1, 'RUST006', 'Rozważ &str zamiast String w parametrach funkcji'))

        # RUST007: Box<dyn Error> without Send + Sync
        if 'Box<dyn Error>' in stripped and 'Send' not in stripped:
            warnings.append(Issue(i, 1, 'RUST007', 'Box<dyn Error> - rozważ dodanie Send + Sync'))

        # RUST008: Using println! for logging
        if 'println!' in stripped and 'debug' not in stripped.lower():
            warnings.append(Issue(i, 1, 'RUST008', 'println! zamiast log/tracing - użyj proper logging'))

        # RUST009: Hardcoded secrets
        secret_patterns = ['password', 'secret', 'api_key', 'token']
        for pattern in secret_patterns:
            if re.search(rf'{pattern}\s*=\s*"[^"]+', stripped, re.I):
                errors.append(Issue(i, 1, 'RUST009', f'Hardcoded {pattern}'))

        # RUST010: Using unsafe without comment
        if 'unsafe {' in stripped or 'unsafe fn' in stripped:
            prev_line = lines[i-2].strip() if i > 1 else ''
            if not prev_line.startswith('//') and 'SAFETY:' not in prev_line:
                warnings.append(Issue(i, 1, 'RUST010', 'unsafe bez komentarza SAFETY:'))

        # RUST011: Empty match arm
        if '=> {}' in stripped or '=> ()' in stripped:
            warnings.append(Issue(i, 1, 'RUST011', 'Pusty match arm - dodaj komentarz lub obsługę'))

        # RUST012: Using to_string() on string literal
        if re.search(r'"[^"]*"\.to_string\(\)', stripped):
            warnings.append(Issue(i, 1, 'RUST012', 'Użyj String::from() lub .into() zamiast "".to_string()'))

        # RUST013: Redundant closure
        if re.search(r'\|\w+\|\s+\w+\(\w+\)', stripped):
            warnings.append(Issue(i, 1, 'RUST013', 'Zbędna closure - możesz przekazać funkcję bezpośrednio'))

        # RUST014: Missing #[must_use] on functions returning Result
        if stripped.startswith('pub fn') and '-> Result' in stripped:
            prev_lines = '\n'.join(lines[max(0, i-3):i-1])
            if '#[must_use]' not in prev_lines:
                warnings.append(Issue(i, 1, 'RUST014', 'Rozważ #[must_use] dla funkcji zwracającej Result'))

    return AnalysisResult('rust', code, '\n'.join(fixed_lines), errors, warnings, fixes)
