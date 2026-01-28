"""Generic YAML analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


def analyze_yaml(code: str) -> AnalysisResult:
    """Analyze YAML for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split('\n')
    fixed_lines = lines.copy()

    indent_stack = [0]
    prev_indent = 0

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        current_indent = len(line) - len(line.lstrip())

        # YAML001: Inconsistent indentation
        if current_indent > 0:
            indent_diff = current_indent - prev_indent
            if indent_diff > 0 and indent_diff != 2 and indent_diff != 4:
                if current_indent % 2 != 0:
                    warnings.append(Issue(i, 1, 'YAML001', 'Niespójna indentacja - użyj 2 lub 4 spacji'))

        # YAML002: Tabs instead of spaces
        if '\t' in line:
            errors.append(Issue(i, 1, 'YAML002', 'YAML nie powinien zawierać tabulatorów'))
            fixed = line.replace('\t', '  ')
            fixes.append(Fix(i, 'Zamieniono tabulatory na spacje', line, fixed))
            fixed_lines[i-1] = fixed

        # YAML003: Trailing whitespace
        if line.rstrip() != line:
            warnings.append(Issue(i, 1, 'YAML003', 'Trailing whitespace'))
            fixed = line.rstrip()
            fixes.append(Fix(i, 'Usunięto trailing whitespace', line, fixed))
            fixed_lines[i-1] = fixed

        # YAML004: Unquoted special values
        special_values = ['yes', 'no', 'on', 'off', 'true', 'false', 'null']
        for val in special_values:
            if re.search(rf':\s+{val}\s*$', stripped, re.I):
                if f'"{val}"' not in stripped.lower() and f"'{val}'" not in stripped.lower():
                    if val.lower() != stripped.split(':')[1].strip().lower():
                        continue
                    warnings.append(Issue(i, 1, 'YAML004', f'Wartość {val} może być interpretowana jako boolean'))
                    m = re.match(r'^(?P<prefix>\s*[^:#]+:\s+)(?P<value>[^#]+?)(?P<comment>\s+#.*)?$', line)
                    if m:
                        prefix = m.group('prefix')
                        value = m.group('value').strip()
                        comment = m.group('comment') or ''
                        if value.lower() == val.lower() and not (value.startswith('"') or value.startswith("'")):
                            fixed = f"{prefix}\"{value}\"{comment}".rstrip()
                            fixes.append(Fix(i, f'Zacytowano wartość {val}', line.rstrip(), fixed))
                            fixed_lines[i - 1] = fixed

        # YAML005: Colon in unquoted string
        value_match = re.search(r':\s+([^"\'\[{#][^#]*)', stripped)
        if value_match:
            value = value_match.group(1).strip()
            if ':' in value and not value.startswith('http'):
                warnings.append(Issue(i, 1, 'YAML005', 'Dwukropek w wartości bez cudzysłowów'))
                m = re.match(r'^(?P<prefix>\s*[^:#]+:\s+)(?P<value>[^#]+?)(?P<comment>\s+#.*)?$', line)
                if m:
                    prefix = m.group('prefix')
                    raw_value = m.group('value').strip()
                    comment = m.group('comment') or ''
                    if not (raw_value.startswith('"') or raw_value.startswith("'")):
                        escaped = raw_value.replace('"', '\\"')
                        fixed = f"{prefix}\"{escaped}\"{comment}".rstrip()
                        fixes.append(Fix(i, 'Dodano cudzysłowy dla wartości z :', line.rstrip(), fixed))
                        fixed_lines[i - 1] = fixed

        # YAML006: Very long lines
        if len(line) > 120:
            warnings.append(Issue(i, 1, 'YAML006', 'Linia > 120 znaków - rozważ multiline'))

        # YAML007: Duplicate keys (basic check)
        if ':' in stripped and not stripped.startswith('-'):
            key = stripped.split(':')[0].strip()
            # Check for duplicates in nearby lines with same indent
            for j in range(max(0, i-20), i-1):
                other = lines[j].strip()
                other_indent = len(lines[j]) - len(lines[j].lstrip())
                if other_indent == current_indent and other.startswith(key + ':'):
                    warnings.append(Issue(i, 1, 'YAML007', f'Potencjalnie duplikat klucza: {key}'))
                    break

        # YAML008: Hardcoded secrets
        secret_patterns = ['password', 'secret', 'api_key', 'token', 'credential']
        for pattern in secret_patterns:
            if re.search(rf'{pattern}\s*:\s*["\']?[^\s${{][^#]*', stripped, re.I):
                if '${' not in stripped and '$(' not in stripped:
                    errors.append(Issue(i, 1, 'YAML008', f'Hardcoded {pattern} - użyj zmiennej środowiskowej'))

        # YAML009: Empty value
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*:\s*$', stripped):
            warnings.append(Issue(i, 1, 'YAML009', 'Pusta wartość - czy to zamierzone?'))

        # YAML010: Anchor without alias usage
        if '&' in stripped and re.search(r'&\w+', stripped):
            anchor = re.search(r'&(\w+)', stripped).group(1)
            if f'*{anchor}' not in code:
                warnings.append(Issue(i, 1, 'YAML010', f'Anchor &{anchor} bez użycia aliasu'))

        prev_indent = current_indent if stripped else prev_indent

    return AnalysisResult('yaml', code, '\n'.join(fixed_lines), errors, warnings, fixes)
