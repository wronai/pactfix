"""CSS analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


def analyze_css(code: str) -> AnalysisResult:
    """Analyze CSS for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split('\n')
    fixed_lines = lines.copy()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        indent_str = line[:indent]

        if not stripped or stripped.startswith('/*') or stripped.startswith('*'):
            continue

        # CSS001: !important usage
        if '!important' in stripped:
            warnings.append(Issue(i, 1, 'CSS001', '!important - rozważ zwiększenie specyficzności'))

        # CSS002: ID selectors (too specific)
        if re.match(r'^#\w+\s*\{', stripped):
            warnings.append(Issue(i, 1, 'CSS002', 'ID selector - rozważ klasę dla reużywalności'))

        # CSS003: Vendor prefixes without standard
        prefixes = ['-webkit-', '-moz-', '-ms-', '-o-']
        for prefix in prefixes:
            if prefix in stripped:
                prop = stripped.split(':')[0].replace(prefix, '').strip()
                if prop + ':' not in '\n'.join(lines[max(0,i-3):i+3]):
                    warnings.append(Issue(i, 1, 'CSS003', f'Vendor prefix bez standardowej właściwości: {prop}'))

        # CSS004: Color values - use variables
        if re.search(r'#[0-9a-fA-F]{3,8}', stripped):
            if 'var(--' not in stripped:
                warnings.append(Issue(i, 1, 'CSS004', 'Hardcoded kolor - rozważ CSS variable'))

        # CSS005: px units for font-size
        if 'font-size:' in stripped and 'px' in stripped:
            warnings.append(Issue(i, 1, 'CSS005', 'font-size w px - rozważ rem lub em'))

        # CSS006: Zero values with units
        if re.search(r':\s*0(px|em|rem|%)', stripped):
            warnings.append(Issue(i, 1, 'CSS006', '0 z jednostką - jednostka niepotrzebna'))
            fixed = re.sub(r':\s*0(px|em|rem|%)', ': 0', stripped)
            fixes.append(Fix(i, 'Usunięto jednostkę przy 0', stripped, fixed))
            fixed_lines[i-1] = indent_str + fixed

        # CSS007: Universal selector
        if re.match(r'^\*\s*\{', stripped) or re.search(r'\s+\*\s*\{', stripped):
            warnings.append(Issue(i, 1, 'CSS007', 'Universal selector (*) - może wpływać na wydajność'))

        # CSS008: Empty rules
        if re.search(r'\{\s*\}', stripped):
            warnings.append(Issue(i, 1, 'CSS008', 'Pusta reguła CSS'))

        # CSS009: Duplicate properties
        if ':' in stripped:
            prop = stripped.split(':')[0].strip()
            # Check for duplicate in same block (simplified)
            prev_lines = '\n'.join(lines[max(0,i-10):i-1])
            if f'{prop}:' in prev_lines and '{' not in prev_lines.split(f'{prop}:')[1][:20]:
                warnings.append(Issue(i, 1, 'CSS009', f'Duplikat właściwości: {prop}'))

        # CSS010: Float usage (consider flexbox/grid)
        if 'float:' in stripped:
            warnings.append(Issue(i, 1, 'CSS010', 'float - rozważ Flexbox lub Grid'))

        # CSS011: Outline: none without alternative
        if 'outline: none' in stripped or 'outline:none' in stripped:
            warnings.append(Issue(i, 1, 'CSS011', 'outline: none - zapewnij alternatywny focus indicator'))

        # CSS012: High z-index
        z_match = re.search(r'z-index:\s*(\d+)', stripped)
        if z_match and int(z_match.group(1)) > 100:
            warnings.append(Issue(i, 1, 'CSS012', f'Wysoki z-index: {z_match.group(1)} - rozważ mniejszą wartość'))

        # CSS013: calc() with mixed units
        if 'calc(' in stripped:
            calc_content = re.search(r'calc\(([^)]+)\)', stripped)
            if calc_content:
                content = calc_content.group(1)
                units = re.findall(r'\d+(px|em|rem|%|vh|vw)', content)
                if len(set(units)) > 2:
                    warnings.append(Issue(i, 1, 'CSS013', 'calc() z wieloma jednostkami - sprawdź'))

        # CSS014: Deprecated properties
        deprecated = ['clip:', 'zoom:']
        for prop in deprecated:
            if prop in stripped:
                warnings.append(Issue(i, 1, 'CSS014', f'Przestarzała właściwość: {prop[:-1]}'))

        # CSS015: Text-transform with locale issues
        if 'text-transform: uppercase' in stripped or 'text-transform:uppercase' in stripped:
            warnings.append(Issue(i, 1, 'CSS015', 'text-transform: uppercase może mieć problemy z locale'))

    return AnalysisResult('css', code, '\n'.join(fixed_lines), errors, warnings, fixes)
