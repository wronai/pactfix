"""Java code analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


def analyze_java(code: str) -> AnalysisResult:
    """Analyze Java code for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split('\n')
    fixed_lines = lines.copy()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        indent_str = line[:indent]

        # JAVA001: Using == for String comparison
        if re.search(r'==\s*"', stripped) or re.search(r'"\s*==', stripped):
            warnings.append(Issue(i, 1, 'JAVA001', 'Użyj .equals() zamiast == dla Stringów'))

        # JAVA002: Catching generic Exception
        if re.match(r'^\s*catch\s*\(\s*Exception\s+', stripped):
            warnings.append(Issue(i, 1, 'JAVA002', 'Łapanie ogólnego Exception - złap konkretny wyjątek'))

        # JAVA003: Empty catch block
        if 'catch' in stripped:
            next_lines = '\n'.join(lines[i:i+3])
            if re.search(r'\{\s*\}', next_lines):
                errors.append(Issue(i, 1, 'JAVA003', 'Pusty blok catch - obsłuż lub zaloguj wyjątek'))

        # JAVA004: Using System.out.println for logging
        if 'System.out.print' in stripped or 'System.err.print' in stripped:
            warnings.append(Issue(i, 1, 'JAVA004', 'Użyj loggera zamiast System.out/err'))

        # JAVA005: Hardcoded credentials
        secret_patterns = ['password', 'secret', 'apiKey', 'api_key', 'token']
        for pattern in secret_patterns:
            if re.search(rf'{pattern}\s*=\s*"[^"]+', stripped, re.I):
                errors.append(Issue(i, 1, 'JAVA005', f'Hardcoded {pattern}'))

        # JAVA006: Using raw types (generics without type parameter)
        raw_types = ['List', 'Map', 'Set', 'ArrayList', 'HashMap', 'HashSet']
        for rtype in raw_types:
            if re.search(rf'\b{rtype}\s+\w+\s*=', stripped) and '<' not in stripped:
                warnings.append(Issue(i, 1, 'JAVA006', f'Raw type {rtype} - dodaj parametr typu'))

        # JAVA007: Public fields
        if re.match(r'^\s*public\s+(?!static|final|class|interface|enum)\w+\s+\w+\s*;', stripped):
            warnings.append(Issue(i, 1, 'JAVA007', 'Publiczne pole - użyj private z getterem/setterem'))

        # JAVA008: Missing @Override annotation
        if re.match(r'^\s*public\s+\w+\s+(equals|hashCode|toString)\s*\(', stripped):
            prev_line = lines[i-2].strip() if i > 1 else ''
            if '@Override' not in prev_line:
                warnings.append(Issue(i, 1, 'JAVA008', 'Brak @Override dla nadpisywanej metody'))

        # JAVA009: Using + for String concatenation in loop
        if '+' in stripped and 'String' in stripped and 'for' in '\n'.join(lines[max(0,i-5):i]):
            warnings.append(Issue(i, 1, 'JAVA009', 'Konkatenacja Stringów w pętli - użyj StringBuilder'))

        # JAVA010: Not closing resources
        if 'new FileInputStream' in stripped or 'new BufferedReader' in stripped:
            if 'try' not in stripped and 'try' not in lines[i-2] if i > 1 else '':
                warnings.append(Issue(i, 1, 'JAVA010', 'Zasób bez try-with-resources'))

        # JAVA011: Using Thread.sleep in main thread
        if 'Thread.sleep' in stripped:
            warnings.append(Issue(i, 1, 'JAVA011', 'Thread.sleep - rozważ ScheduledExecutorService'))

        # JAVA012: Synchronized on method level
        if 'synchronized' in stripped and 'void' in stripped or 'synchronized' in stripped and re.search(r'\)\s*\{', stripped):
            warnings.append(Issue(i, 1, 'JAVA012', 'synchronized na metodzie - rozważ blok synchronized'))

        # JAVA013: Using Date instead of LocalDate
        if 'new Date()' in stripped or 'java.util.Date' in stripped:
            warnings.append(Issue(i, 1, 'JAVA013', 'java.util.Date - użyj java.time API'))

        # JAVA014: SQL injection risk
        if 'executeQuery(' in stripped or 'executeUpdate(' in stripped:
            if '+' in stripped or 'String.format' in stripped:
                errors.append(Issue(i, 1, 'JAVA014', 'Potencjalny SQL injection - użyj PreparedStatement'))

        # JAVA015: NullPointerException risk
        if re.search(r'\w+\.\w+\(\)', stripped) and 'null' in '\n'.join(lines[max(0,i-3):i]):
            warnings.append(Issue(i, 1, 'JAVA015', 'Potencjalny NullPointerException - sprawdź null'))

    return AnalysisResult('java', code, '\n'.join(fixed_lines), errors, warnings, fixes)
