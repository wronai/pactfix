"""TypeScript code analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


def analyze_typescript(code: str) -> AnalysisResult:
    """Analyze TypeScript code for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split('\n')
    fixed_lines = lines.copy()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        indent_str = line[:indent]

        # TS001: any type usage
        if re.search(r':\s*any\b', stripped) or re.search(r'<any>', stripped):
            warnings.append(Issue(i, 1, 'TS001', 'Unikaj typu any - użyj unknown lub konkretnego typu'))

        # TS002: Non-null assertion overuse
        if '!' in stripped and re.search(r'\w+!\.', stripped):
            warnings.append(Issue(i, 1, 'TS002', 'Nadużycie non-null assertion (!) - rozważ optional chaining'))

        # TS003: var instead of let/const
        if re.search(r'\bvar\s+\w+', stripped):
            warnings.append(Issue(i, 1, 'TS003', 'Użyj let/const zamiast var'))
            fixed = re.sub(r'\bvar\b', 'let', stripped)
            fixes.append(Fix(i, 'Zamieniono var na let', stripped, fixed))
            fixed_lines[i-1] = indent_str + fixed

        # TS004: == instead of ===
        if re.search(r'[^=!]={2}[^=]', stripped) and '===' not in stripped:
            warnings.append(Issue(i, 1, 'TS004', 'Użyj === zamiast =='))
            fixed = re.sub(r'([^=!])={2}([^=])', r'\1===\2', stripped)
            fixes.append(Fix(i, 'Zamieniono == na ===', stripped, fixed))
            fixed_lines[i-1] = indent_str + fixed

        # TS005: console.log in production code
        if 'console.log' in stripped:
            warnings.append(Issue(i, 1, 'TS005', 'console.log w kodzie produkcyjnym'))

        # TS006: eval usage
        if 'eval(' in stripped:
            errors.append(Issue(i, 1, 'TS006', 'eval() jest niebezpieczne - unikaj'))

        # TS007: @ts-ignore without explanation
        if '@ts-ignore' in stripped and '//' in stripped:
            if len(stripped.split('@ts-ignore')[1].strip()) < 5:
                warnings.append(Issue(i, 1, 'TS007', '@ts-ignore bez wyjaśnienia'))

        # TS008: Empty interface
        if re.match(r'^\s*interface\s+\w+\s*\{\s*\}\s*$', stripped):
            warnings.append(Issue(i, 1, 'TS008', 'Pusty interface - użyj type alias lub Record<string, never>'))

        # TS009: Function without return type
        if re.search(r'function\s+\w+\s*\([^)]*\)\s*\{', stripped) and ':' not in stripped.split('{')[0]:
            warnings.append(Issue(i, 1, 'TS009', 'Funkcja bez typu zwracanego'))

        # TS010: async function without await
        if 'async ' in stripped and 'await' not in code:
            warnings.append(Issue(i, 1, 'TS010', 'Funkcja async bez await'))

        # TS011: Promise constructor anti-pattern
        if 'new Promise' in stripped and 'async' in stripped:
            warnings.append(Issue(i, 1, 'TS011', 'Niepotrzebny Promise w async function'))

        # TS012: Object type usage
        if re.search(r':\s*Object\b', stripped):
            warnings.append(Issue(i, 1, 'TS012', 'Użyj object lub Record zamiast Object'))

        # TS013: String/Number/Boolean wrapper types
        for wrapper in ['String', 'Number', 'Boolean']:
            if re.search(rf':\s*{wrapper}\b', stripped):
                lower = wrapper.lower()
                warnings.append(Issue(i, 1, 'TS013', f'Użyj {lower} zamiast {wrapper}'))

        # TS014: Unused import detection (basic)
        if stripped.startswith('import ') and ' from ' in stripped:
            match = re.search(r'import\s+\{([^}]+)\}', stripped)
            if match:
                imports = [x.strip() for x in match.group(1).split(',')]
                for imp in imports:
                    if imp and imp not in code.replace(stripped, ''):
                        warnings.append(Issue(i, 1, 'TS014', f'Potencjalnie nieużywany import: {imp}'))

    return AnalysisResult('typescript', code, '\n'.join(fixed_lines), errors, warnings, fixes)
