import re
from typing import List

from ..analyzer import Issue, Fix, AnalysisResult


def analyze_php(code: str) -> AnalysisResult:
    """Analyze PHP code."""
    errors, warnings, fixes = [], [], []
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        if re.search(r'\$_(GET|POST|REQUEST|COOKIE)\[', stripped):
            if 'htmlspecialchars' not in stripped and 'filter_' not in stripped:
                warnings.append(Issue(i, 1, 'PHP001', 'Niezwalidowane dane wejściowe - użyj filter_input lub htmlspecialchars'))
        
        if '==' in stripped and ('null' in stripped.lower() or 'false' in stripped.lower()):
            warnings.append(Issue(i, 1, 'PHP002', 'Użyj === zamiast == dla porównań'))
        
        if re.search(r'\bmysql_(connect|query|fetch)', stripped):
            errors.append(Issue(i, 1, 'PHP003', 'Przestarzałe funkcje mysql_* - użyj PDO lub mysqli'))
        
        if 'extract(' in stripped:
            errors.append(Issue(i, 1, 'PHP004', 'extract() jest niebezpieczne - użyj jawnego przypisania'))
        
        if stripped.startswith('@'):
            warnings.append(Issue(i, 1, 'PHP005', 'Operator @ tłumi błędy - obsłuż je prawidłowo'))
        
        if '<?=' in stripped or re.match(r'^<\?\s+', stripped):
            warnings.append(Issue(i, 1, 'PHP006', 'Użyj pełnego <?php zamiast short tags'))
    
    return AnalysisResult('php', code, code, errors, warnings, fixes)
