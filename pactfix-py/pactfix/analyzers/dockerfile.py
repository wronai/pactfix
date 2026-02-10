import re
from typing import List

from ..analyzer import Issue, Fix, AnalysisResult


def analyze_dockerfile(code: str) -> AnalysisResult:
    """Analyze Dockerfile."""
    errors, warnings, fixes = [], [], []
    lines = code.split('\n')
    fixed_lines = lines.copy()
    
    has_user = False
    has_healthcheck = False
    base_image = None
    env_vars = set()
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        upper = stripped.upper()
        
        if upper.startswith('FROM '):
            base_image = stripped[5:].strip().split()[0]
            if ':latest' in base_image or (':' not in base_image and '@' not in base_image):
                warnings.append(Issue(i, 1, 'DOCKER001', f'Użyj konkretnego tagu zamiast :latest dla {base_image}'))
                if ':' not in base_image:
                    fixed = stripped + ':latest  # TODO: specify version'
                    fixes.append(Fix(i, 'Dodano placeholder dla wersji', stripped, fixed))
        
        if upper.startswith('USER '):
            has_user = True
        
        if upper.startswith('HEALTHCHECK '):
            has_healthcheck = True
        
        if upper.startswith('ENV '):
            parts = stripped[4:].split('=')
            if parts:
                env_vars.add(parts[0].strip())
        
        if upper.startswith('RUN ') and 'apt-get install' in stripped:
            if 'rm -rf /var/lib/apt/lists' not in stripped and '&&' not in stripped:
                warnings.append(Issue(i, 1, 'DOCKER002', 'apt-get install bez czyszczenia cache'))
            if 'apt-get update' not in stripped:
                warnings.append(Issue(i, 1, 'DOCKER003', 'apt-get install bez update w tej samej warstwie'))
        
        if upper.startswith('ADD ') and 'http' not in stripped and '.tar' not in stripped:
            warnings.append(Issue(i, 1, 'DOCKER004', 'Użyj COPY zamiast ADD dla lokalnych plików'))
            fixed = 'COPY' + stripped[3:]
            fixes.append(Fix(i, 'Zamieniono ADD na COPY', stripped, fixed))
            fixed_lines[i-1] = line.replace(stripped, fixed)
        
        if upper.startswith('WORKDIR ') and not stripped[8:].strip().startswith('/'):
            warnings.append(Issue(i, 1, 'DOCKER008', 'WORKDIR powinien używać ścieżki absolutnej'))
            fixed = 'WORKDIR /' + stripped[8:].strip()
            fixes.append(Fix(i, 'Dodano / do WORKDIR', stripped, fixed))
            fixed_lines[i-1] = line.replace(stripped, fixed)
        
        secret_patterns = ['PASSWORD=', 'SECRET=', 'API_KEY=', 'TOKEN=']
        for pattern in secret_patterns:
            if pattern in upper and 'ARG' not in upper:
                errors.append(Issue(i, 1, 'DOCKER007', 'Hardcoded secret - użyj build args lub secrets'))
        
        if (upper.startswith('CMD ') or upper.startswith('ENTRYPOINT ')) and '[' not in stripped:
            warnings.append(Issue(i, 1, 'DOCKER006', 'Użyj formy exec (JSON array) dla CMD/ENTRYPOINT'))
    
    if not has_user:
        warnings.append(Issue(1, 1, 'DOCKER009', 'Brak USER - kontener będzie działał jako root'))
    
    if not has_healthcheck and base_image:
        warnings.append(Issue(1, 1, 'DOCKER010', 'Brak HEALTHCHECK'))
    
    context = {'base_image': base_image, 'env_vars': list(env_vars)}
    return AnalysisResult('dockerfile', code, '\n'.join(fixed_lines), errors, warnings, fixes, context)
