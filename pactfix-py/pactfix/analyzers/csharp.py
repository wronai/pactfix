"""C# code analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


def analyze_csharp(code: str) -> AnalysisResult:
    """Analyze C# code for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split('\n')
    fixed_lines = lines.copy()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        indent_str = line[:indent]

        # CS001: Using == for string comparison (should use String.Equals)
        if re.search(r'==\s*"', stripped) and 'nameof' not in stripped:
            warnings.append(Issue(i, 1, 'CS001', 'Rozważ String.Equals() z StringComparison'))

        # CS002: Catching generic Exception
        if re.match(r'^\s*catch\s*\(\s*Exception\s*', stripped):
            warnings.append(Issue(i, 1, 'CS002', 'Łapanie ogólnego Exception - złap konkretny wyjątek'))

        # CS003: Empty catch block
        if 'catch' in stripped:
            next_lines = '\n'.join(lines[i:i+3])
            if re.search(r'\{\s*\}', next_lines):
                errors.append(Issue(i, 1, 'CS003', 'Pusty blok catch'))

        # CS004: Using Console.WriteLine for logging
        if 'Console.Write' in stripped:
            warnings.append(Issue(i, 1, 'CS004', 'Użyj ILogger zamiast Console.Write'))

        # CS005: Hardcoded credentials
        secret_patterns = ['password', 'secret', 'apiKey', 'connectionString']
        for pattern in secret_patterns:
            if re.search(rf'{pattern}\s*=\s*"[^"]+', stripped, re.I):
                errors.append(Issue(i, 1, 'CS005', f'Hardcoded {pattern}'))

        # CS006: Using var for unclear types
        if re.match(r'^\s*var\s+\w+\s*=\s*\w+\.\w+\(', stripped):
            warnings.append(Issue(i, 1, 'CS006', 'var z niejasnym typem - rozważ explicit type'))

        # CS007: Public fields instead of properties
        if re.match(r'^\s*public\s+\w+\s+\w+\s*;', stripped) and 'const' not in stripped:
            warnings.append(Issue(i, 1, 'CS007', 'Publiczne pole - użyj property'))

        # CS008: async void methods
        if re.match(r'^\s*(public|private|protected)?\s*async\s+void\s+', stripped):
            if 'EventHandler' not in stripped:
                errors.append(Issue(i, 1, 'CS008', 'async void - użyj async Task'))

        # CS009: Not awaiting async call
        if 'Async(' in stripped and 'await' not in stripped and 'Task' not in stripped:
            warnings.append(Issue(i, 1, 'CS009', 'Wywołanie async bez await'))

        # CS010: Using lock(this)
        if 'lock(this)' in stripped or 'lock (this)' in stripped:
            errors.append(Issue(i, 1, 'CS010', 'lock(this) jest niebezpieczne - użyj prywatnego obiektu'))

        # CS011: Using string concatenation instead of interpolation
        if re.search(r'"\s*\+\s*\w+\s*\+\s*"', stripped):
            warnings.append(Issue(i, 1, 'CS011', 'Konkatenacja stringów - użyj interpolacji $""'))

        # CS012: Not disposing IDisposable
        if 'new ' in stripped and any(x in stripped for x in ['Stream', 'Reader', 'Writer', 'Connection']):
            if 'using' not in stripped and 'using' not in (lines[i-2] if i > 1 else ''):
                warnings.append(Issue(i, 1, 'CS012', 'IDisposable bez using'))

        # CS013: SQL injection risk
        if 'SqlCommand' in stripped or 'ExecuteReader' in stripped:
            if '+' in stripped or 'String.Format' in stripped:
                errors.append(Issue(i, 1, 'CS013', 'Potencjalny SQL injection - użyj parametrów'))

        # CS014: Using Thread.Sleep
        if 'Thread.Sleep' in stripped:
            warnings.append(Issue(i, 1, 'CS014', 'Thread.Sleep - użyj await Task.Delay'))

        # CS015: Missing null check
        if re.search(r'(\w+)\.\w+', stripped) and 'null' not in stripped and '?' not in stripped:
            if 'if' not in stripped:
                pass  # Would need more context

        # CS016: Using DateTime.Now instead of DateTimeOffset
        if 'DateTime.Now' in stripped or 'DateTime.Today' in stripped:
            warnings.append(Issue(i, 1, 'CS016', 'Rozważ DateTimeOffset lub DateTime.UtcNow'))

        # CS017: Magic numbers
        if re.search(r'[=<>]\s*\d{2,}', stripped) and 'const' not in stripped and '//' not in stripped:
            warnings.append(Issue(i, 1, 'CS017', 'Magic number - użyj stałej z nazwą'))

    return AnalysisResult('csharp', code, '\n'.join(fixed_lines), errors, warnings, fixes)
