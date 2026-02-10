import re
from typing import List

from ..analyzer import Issue, Fix, AnalysisResult


def analyze_ansible(code: str) -> AnalysisResult:
    """Analyze Ansible playbook."""
    errors, warnings, fixes = [], [], []
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        if re.search(r'password\s*:\s*["\']?[^\$\{]', stripped, re.I):
            errors.append(Issue(i, 1, 'ANS001', 'Plain text password - użyj ansible-vault'))
        
        if stripped.startswith('- shell:') or stripped.startswith('- command:'):
            if 'changed_when' not in '\n'.join(lines[i:min(i+5, len(lines))]):
                warnings.append(Issue(i, 1, 'ANS002', 'shell/command bez changed_when'))
        
        if 'become: true' in stripped or 'become: yes' in stripped:
            if 'become_user' not in '\n'.join(lines[max(0,i-3):i+3]):
                warnings.append(Issue(i, 1, 'ANS003', 'become bez become_user'))
        
        if 'ignore_errors: true' in stripped or 'ignore_errors: yes' in stripped:
            warnings.append(Issue(i, 1, 'ANS004', 'ignore_errors ukrywa błędy'))
    
    return AnalysisResult('ansible', code, code, errors, warnings, fixes)
