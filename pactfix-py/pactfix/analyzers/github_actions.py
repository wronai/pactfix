import re
from typing import List

from ..analyzer import Issue, Fix, AnalysisResult


def analyze_github_actions(code: str) -> AnalysisResult:
    """Analyze GitHub Actions workflow."""
    errors, warnings, fixes = [], [], []
    lines = code.split('\n')
    fixed_lines = lines.copy()
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        if 'uses:' in stripped and ('@master' in stripped or '@main' in stripped):
            warnings.append(Issue(i, 1, 'GHA001', 'Użyj wersji/SHA zamiast @master'))
            fixed = re.sub(r'@(master|main)$', '@v4', stripped)
            fixes.append(Fix(i, 'Zmieniono na wersję', stripped, fixed))
            fixed_lines[i-1] = line.replace(stripped, fixed)
        
        if 'pull_request_target' in stripped:
            warnings.append(Issue(i, 1, 'GHA002', 'pull_request_target może być niebezpieczne'))
        
        if re.search(r'(password|token|key|secret)\s*[:=]\s*(?!\$\{\{)(?!\$\{)(?!\$)\S+', stripped, re.I):
            errors.append(Issue(i, 1, 'GHA003', 'Hardcoded secret - użyj ${{ secrets.NAME }}'))
        
        if '${{' in stripped and ('github.event.' in stripped or 'inputs.' in stripped):
            if 'run:' in stripped:
                warnings.append(Issue(i, 1, 'GHA004', 'Możliwy shell injection'))
        
        if stripped.startswith('jobs:'):
            warnings.append(Issue(i, 1, 'GHA005', 'Ustaw minimalne permissions'))
    
    return AnalysisResult('github-actions', code, '\n'.join(fixed_lines), errors, warnings, fixes)
