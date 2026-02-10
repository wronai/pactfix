import re
from typing import List

from ..analyzer import Issue, Fix, AnalysisResult


def analyze_javascript(code: str, is_nodejs: bool = False) -> AnalysisResult:
    """Analyze JavaScript/Node.js code."""
    errors, warnings, fixes = [], [], []
    lines = code.split('\n')
    fixed_lines = lines.copy()
    lang = 'nodejs' if is_nodejs else 'javascript'
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # var usage
        if re.search(r'\bvar\s+\w+', stripped):
            warnings.append(Issue(i, 1, 'JS001', 'Użyj let/const zamiast var'))
            fixed = re.sub(r'\bvar\b', 'let', stripped)
            fixes.append(Fix(i, 'Zamieniono var na let', stripped, fixed))
            fixed_lines[i-1] = line.replace(stripped, fixed)
        
        # == instead of ===
        if re.search(r'[^=!]={2}[^=]', stripped) and '===' not in stripped:
            warnings.append(Issue(i, 1, 'JS002', 'Użyj === zamiast =='))
        
        # console.log in production
        if 'console.log' in stripped:
            warnings.append(Issue(i, 1, 'JS003', 'console.log w kodzie produkcyjnym'))
        
        # eval usage
        if 'eval(' in stripped:
            errors.append(Issue(i, 1, 'JS004', 'eval() jest niebezpieczne - unikaj'))
        
        # Node.js specific
        if is_nodejs:
            if re.search(r'\b(readFileSync|writeFileSync)\b', stripped):
                warnings.append(Issue(i, 1, 'NODE002', 'Sync I/O blokuje event loop - użyj async'))
    
    return AnalysisResult(lang, code, '\n'.join(fixed_lines), errors, warnings, fixes)
