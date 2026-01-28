"""Makefile analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


def analyze_makefile(code: str) -> AnalysisResult:
    """Analyze Makefile for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split('\n')
    fixed_lines = lines.copy()

    targets = set()
    phony_targets = set()
    has_default_goal = False

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        original = line

        # MAKE001: Spaces instead of tabs for recipes
        if i > 1 and lines[i-2].strip() and ':' in lines[i-2] and not lines[i-2].strip().startswith('#'):
            if line.startswith(' ') and not line.startswith('\t') and stripped:
                if not stripped.startswith('#') and '=' not in stripped:
                    errors.append(Issue(i, 1, 'MAKE001', 'Użyj tabulatora zamiast spacji w recepcie'))
                    fixed = '\t' + stripped
                    fixes.append(Fix(i, 'Zamieniono spacje na tabulator', line, fixed))
                    fixed_lines[i-1] = fixed

        # MAKE002: Target without recipe
        if ':' in stripped and not stripped.startswith('#') and not stripped.startswith('\t'):
            if '=' not in stripped and '::' not in stripped:
                target_match = re.match(r'^([a-zA-Z0-9_.-]+)\s*:', stripped)
                if target_match:
                    targets.add(target_match.group(1))

        # MAKE003: Missing .PHONY
        if stripped.startswith('.PHONY:'):
            phony_list = stripped.split(':')[1].strip().split()
            phony_targets.update(phony_list)

        # MAKE004: Hardcoded paths
        if re.search(r'/usr/local/|/home/\w+|C:\\', stripped):
            warnings.append(Issue(i, 1, 'MAKE004', 'Hardcoded path - użyj zmiennej'))

        # MAKE005: Missing error handling in shell commands
        if stripped.startswith('\t') and 'cd ' in stripped and '&&' not in stripped:
            warnings.append(Issue(i, 1, 'MAKE005', 'cd bez && może kontynuować po błędzie'))

        # MAKE006: Using shell instead of simple variable
        if '$(shell ' in stripped and re.search(r'\$\(shell\s+(echo|cat|pwd)\s', stripped):
            warnings.append(Issue(i, 1, 'MAKE006', '$(shell echo) - rozważ prostszą składnię'))

        # MAKE007: Recursive make without $(MAKE)
        if '\tmake ' in line and '$(MAKE)' not in line:
            warnings.append(Issue(i, 1, 'MAKE007', 'Użyj $(MAKE) zamiast make dla rekursji'))
            fixed = line.replace('\tmake ', '\t$(MAKE) ')
            fixes.append(Fix(i, 'Zamieniono make na $(MAKE)', line, fixed))
            fixed_lines[i-1] = fixed

        # MAKE008: Undefined variable usage
        var_usage = re.findall(r'\$\((\w+)\)', stripped)
        for var in var_usage:
            if var not in ['MAKE', 'SHELL', 'CC', 'CXX', 'CFLAGS', 'LDFLAGS', 'CURDIR', 'MAKECMDGOALS']:
                # Check if defined in file
                if f'{var}=' not in code and f'{var} =' not in code:
                    pass  # Too many false positives, skip

        # MAKE009: .DEFAULT_GOAL
        if '.DEFAULT_GOAL' in stripped:
            has_default_goal = True

        # MAKE010: Silent prefix without explanation
        if stripped.startswith('\t@') and '#' not in stripped:
            if len(stripped) > 3:
                pass  # Common pattern, not always an issue

        # MAKE011: Rm without -f
        if 'rm ' in stripped and '-f' not in stripped and '-rf' not in stripped:
            warnings.append(Issue(i, 1, 'MAKE011', 'rm bez -f może przerwać na brakującym pliku'))

        # MAKE012: Missing clean target
        if 'clean:' in stripped:
            targets.add('clean')

        # MAKE013: Using $(wildcard) in prerequisites
        if '$(wildcard' in stripped and ':' in stripped:
            warnings.append(Issue(i, 1, 'MAKE013', '$(wildcard) w prerequisites może być nieprzewidywalny'))

        # MAKE014: Double-colon rules without understanding
        if '::' in stripped and not stripped.startswith('#'):
            warnings.append(Issue(i, 1, 'MAKE014', 'Double-colon rule (::) - upewnij się że to zamierzone'))

    # Post-analysis warnings
    phony_candidates = {'all', 'clean', 'install', 'test', 'build', 'help', 'check', 'lint'}
    missing_phony = targets.intersection(phony_candidates) - phony_targets
    if missing_phony:
        warnings.append(Issue(1, 1, 'MAKE003', f'.PHONY brakuje dla: {", ".join(sorted(missing_phony))}'))

    if 'clean' not in targets:
        warnings.append(Issue(1, 1, 'MAKE012', 'Brak targetu clean'))

    return AnalysisResult('makefile', code, '\n'.join(fixed_lines), errors, warnings, fixes)
