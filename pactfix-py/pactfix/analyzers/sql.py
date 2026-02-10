import re
from typing import List

from ..analyzer import Issue, Fix, AnalysisResult


def analyze_sql(code: str) -> AnalysisResult:
    """Analyze SQL."""
    errors, warnings, fixes = [], [], []
    lines = code.split('\n')
    fixed_lines = lines.copy()
    
    tables_created = set()
    tables_referenced = set()
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        upper = stripped.upper()
        
        if 'CREATE TABLE' in upper:
            match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`"\[]?(\w+)', upper)
            if match:
                tables_created.add(match.group(1).lower())
        
        if any(kw in upper for kw in ['FROM ', 'JOIN ', 'INTO ', 'UPDATE ']):
            for match in re.finditer(r'(?:FROM|JOIN|INTO|UPDATE)\s+[`"\[]?(\w+)', upper):
                tables_referenced.add(match.group(1).lower())
        
        if re.search(r'\bSELECT\s+\*', upper):
            warnings.append(Issue(i, 1, 'SQL001', 'SELECT * - wymień konkretne kolumny'))
        
        if ('UPDATE ' in upper or 'DELETE FROM' in upper) and 'WHERE' not in upper:
            if ';' in stripped or i == len(lines):
                errors.append(Issue(i, 1, 'SQL003', 'UPDATE/DELETE bez WHERE!'))
        
        if 'DROP ' in upper and 'IF EXISTS' not in upper:
            warnings.append(Issue(i, 1, 'SQL004', 'DROP bez IF EXISTS'))
            fixed = stripped.replace('DROP ', 'DROP IF EXISTS ', 1)
            fixes.append(Fix(i, 'Dodano IF EXISTS', stripped, fixed))
            fixed_lines[i-1] = line.replace(stripped, fixed)
        
        if 'CREATE TABLE' in upper and 'IF NOT EXISTS' not in upper:
            warnings.append(Issue(i, 1, 'SQL005', 'CREATE bez IF NOT EXISTS'))
        
        if 'GRANT ALL' in upper:
            warnings.append(Issue(i, 1, 'SQL007', 'GRANT ALL - przyznaj tylko wymagane uprawnienia'))
        
        if re.search(r"PASSWORD\s*[=:]\s*['\"][^'\"]+['\"]", upper):
            errors.append(Issue(i, 1, 'SQL008', 'Hasło w plain text'))
    
    missing = tables_referenced - tables_created - {'dual', 'information_schema'}
    context = {'tables_created': list(tables_created), 'tables_referenced': list(tables_referenced), 'potentially_missing': list(missing)}
    return AnalysisResult('sql', code, '\n'.join(fixed_lines), errors, warnings, fixes, context)
