import re
from typing import List, Dict, Any

from ..analyzer import Issue, Fix, AnalysisResult


def _brace_unbraced_bash_vars(line: str) -> str:
    out = []
    i = 0
    in_single = False
    in_double = False
    escaped = False
    while i < len(line):
        ch = line[i]
        if escaped:
            out.append(ch)
            escaped = False
            i += 1
            continue
        if ch == '\\':
            out.append(ch)
            escaped = True
            i += 1
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            out.append(ch)
            i += 1
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            out.append(ch)
            i += 1
            continue
        if ch == '$' and not in_single:
            if i + 1 < len(line) and line[i + 1] == '{':
                out.append(ch)
                i += 1
                continue
            if i + 1 < len(line) and re.match(r'[A-Za-z_]', line[i + 1]):
                j = i + 2
                while j < len(line) and re.match(r'[A-Za-z0-9_]', line[j]):
                    j += 1
                name = line[i + 1:j]
                out.append('${' + name + '}')
                i = j
                continue
        out.append(ch)
        i += 1
    return ''.join(out)


def _split_bash_comment(line: str) -> tuple[str, str]:
    in_single = False
    in_double = False
    escaped = False
    for i, ch in enumerate(line):
        if escaped:
            escaped = False
            continue
        if ch == '\\':
            escaped = True
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            continue
        if ch == '#' and not in_single and not in_double:
            return line[:i], line[i:]
    return line, ''


def analyze_bash(code: str) -> AnalysisResult:
    """Analyze Bash script."""
    errors, warnings, fixes = [], [], []
    lines = code.split('\n')
    fixed_lines = lines.copy()
    
    for i, line in enumerate(lines, 1):
        current_line = fixed_lines[i-1]
        stripped = current_line.strip()
        
        # Variables without braces: use ${VAR} for clarity (e.g. ${OUTPUT}/${HOST})
        if not stripped.startswith('#') and '$' in current_line and re.search(r'\$[A-Za-z_][A-Za-z0-9_]*', current_line):
            code_part, comment_part = _split_bash_comment(current_line)
            braced_code_part = _brace_unbraced_bash_vars(code_part)
            if braced_code_part != code_part:
                new_line = braced_code_part + comment_part
                warnings.append(Issue(i, 1, 'BASH001', 'Zmienne bez klamerek: użyj składni ${VAR} (np. ${OUTPUT}/${HOST})'))
                fixes.append(Fix(i, 'Dodano klamerki do zmiennych', current_line.strip(), new_line.strip()))
                current_line = new_line
                stripped = current_line.strip()
        
        # SC2164: cd without error handling
        if re.match(r'^cd\s+', stripped) and '||' not in stripped and '&&' not in stripped:
            warnings.append(Issue(i, 1, 'SC2164', 'cd bez obsługi błędów - użyj cd ... || exit'))
            fix_line = stripped + ' || exit 1'
            fixes.append(Fix(i, 'Dodano obsługę błędów dla cd', stripped, fix_line))
            current_line = current_line.replace(stripped, fix_line)
            stripped = fix_line
        
        # SC2162: read without -r
        if re.match(r'^read\s+', stripped) and '-r' not in stripped:
            warnings.append(Issue(i, 1, 'SC2162', 'read bez -r może interpretować backslashe'))
        
        # Check for misplaced quotes
        # Pattern 1: word="text"word (quotes between words)
        quote_match = re.search(r'(\w+)="([^"]*)"(\w+)', stripped)
        if quote_match:
            errors.append(Issue(i, 1, 'SC1073', 'Błędne umiejscowienie cudzysłowów'))
            fixed = f'{quote_match.group(1)}="{quote_match.group(2)}{quote_match.group(3)}"'
            fixes.append(Fix(i, 'Poprawiono cudzysłowy', quote_match.group(0), fixed))
            current_line = current_line.replace(quote_match.group(0), fixed)
        
        # Pattern 2: Mismatched quotes in command substitution like $(cmd")
        if re.search(r'\$\([^)]*"[^)]*\)', stripped):
            errors.append(Issue(i, 1, 'SC1073', 'Błędnie umieszczony cudzysłów wewnątrz podstawienia polecenia'))
            # Fix by moving the quote outside
            fixed = re.sub(r'\$\(([^)]*)"([^)]*)\)', r'$(\1\2)"', stripped)
            fixes.append(Fix(i, 'Poprawiono cudzysłów w podstawieniu', stripped, fixed))
            current_line = current_line.replace(stripped, fixed)
        
        fixed_lines[i-1] = current_line
    
    return AnalysisResult('bash', code, '\n'.join(fixed_lines), errors, warnings, fixes)
