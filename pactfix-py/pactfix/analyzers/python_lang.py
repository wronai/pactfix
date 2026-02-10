import ast
import re
from typing import List, Dict, Any

from ..analyzer import Issue, Fix, AnalysisResult


def _split_python_comment(line: str) -> tuple[str, str]:
    in_single = False
    in_double = False
    escaped = False
    for i, ch in enumerate(line):
        if escaped:
            escaped = False
            continue
        if ch == '\\':
            escaped = True
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            continue
        if ch == '#' and not in_single and not in_double:
            return line[:i], line[i:]
    return line, ''


def analyze_python(code: str) -> AnalysisResult:
    """Analyze Python code."""
    errors, warnings, fixes = [], [], []
    lines = code.split('\n')
    fixed_lines = lines.copy()
    
    for i, line in enumerate(lines, 1):
        current_line = fixed_lines[i - 1]
        stripped = current_line.strip()
        code_part, comment_part = _split_python_comment(current_line)
        code_stripped = code_part.strip()
        in_condition_stmt = code_stripped.startswith(('if ', 'elif ', 'while ', 'assert '))

        if re.match(r'^\s*def\s+\w+\s*\(', current_line):
            next_non_empty = ''
            next_idx = i
            while next_idx < len(fixed_lines):
                probe = fixed_lines[next_idx]
                if probe.strip() != '':
                    next_non_empty = probe.strip()
                    break
                next_idx += 1
            if next_non_empty and not next_non_empty.startswith(('"""', "'''")):
                warnings.append(Issue(i, 1, 'PY006', 'Funkcja nie ma docstringa'))
                def_indent_match = re.match(r'^\s*', current_line)
                def_indent = def_indent_match.group(0) if def_indent_match else ''
                body_indent = def_indent + '    '
                if next_idx < len(fixed_lines):
                    probe_indent_match = re.match(r'^\s*', fixed_lines[next_idx])
                    probe_indent = probe_indent_match.group(0) if probe_indent_match else ''
                    if len(probe_indent) > len(def_indent):
                        body_indent = probe_indent
                doc_line = f'{body_indent}"""TODO: docstring."""'
                edit = {'startLine': i + 1, 'endLine': i, 'replacement': doc_line}
                fixes.append(Fix(i, 'Dodano szablon docstringa', current_line.strip(), '', edits=[edit]))
        
        # Python 2 print statement
        if re.match(r'^print\s+["\']', stripped) or re.match(r'^print\s+\w', stripped):
            if not stripped.startswith('print('):
                errors.append(Issue(i, 1, 'PY001', 'Użyj print() z nawiasami (Python 3)'))
                match = re.match(r'^print\s+(.+)$', stripped)
                if match:
                    fixed = f'print({match.group(1)})'
                    fixes.append(Fix(i, 'Dodano nawiasy do print()', stripped, fixed))
                    fixed_lines[i - 1] = current_line.replace(stripped, fixed)
                    current_line = fixed_lines[i - 1]
                    code_part, comment_part = _split_python_comment(current_line)
                    code_stripped = code_part.strip()
                    stripped = current_line.strip()
        
        # Bare except
        if re.match(r'^except\s*:', code_stripped):
            warnings.append(Issue(i, 1, 'PY002', 'Unikaj pustego except: - złap konkretne wyjątki'))
            if re.match(r'^except\s*:\s*$', code_stripped):
                fixed = re.sub(r'^except\s*:\s*$', 'except Exception:', code_stripped)
                if fixed != code_stripped:
                    fixes.append(Fix(i, 'Zmieniono except: na except Exception:', code_stripped, fixed))
                    fixed_lines[i - 1] = (code_part[:len(code_part) - len(code_part.lstrip())] + fixed + comment_part)
                    current_line = fixed_lines[i - 1]
                    code_part, comment_part = _split_python_comment(current_line)
                    code_stripped = code_part.strip()
                    stripped = current_line.strip()
        
        # Mutable default argument
        if re.search(r'def\s+\w+\s*\([^)]*=\s*(\[\]|\{\})', stripped):
            warnings.append(Issue(i, 1, 'PY003', 'Mutable default argument - użyj None'))
            m = re.match(r'^(\s*def\s+\w+\s*\()(?P<args>[^)]*)(\)\s*:.*)$', current_line)
            if m:
                args = m.group('args')
                arg_match = re.search(r'(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<lit>\[\]|\{\})', args)
                if arg_match:
                    name = arg_match.group('name')
                    lit = arg_match.group('lit')
                    new_args = args.replace(arg_match.group(0), f"{name}=None")
                    new_def_line = current_line.replace(args, new_args)

                    next_line = fixed_lines[i] if i < len(fixed_lines) else ''
                    if re.search(rf'^\s*if\s+{re.escape(name)}\s+is\s+None\s*:', next_line or ''):
                        pass
                    else:
                        def_indent_match = re.match(r'^\s*', current_line)
                        def_indent = def_indent_match.group(0) if def_indent_match else ''
                        body_indent = def_indent + '    '
                        for j in range(i, len(fixed_lines)):
                            probe = fixed_lines[j]
                            if probe.strip() == '':
                                continue
                            probe_indent_match = re.match(r'^\s*', probe)
                            probe_indent = probe_indent_match.group(0) if probe_indent_match else ''
                            if len(probe_indent) > len(def_indent):
                                body_indent = probe_indent
                            break

                        init_line = f"{body_indent}if {name} is None: {name} = {lit}"
                        fixes.append(
                            Fix(
                                i,
                                f'Zmieniono mutable default argument {name} na None',
                                current_line.strip(),
                                new_def_line.strip(),
                                edits=[
                                    {
                                        'startLine': i,
                                        'endLine': i,
                                        'replacement': new_def_line,
                                        'preserveIndent': True,
                                    },
                                    {
                                        'startLine': i + 1,
                                        'endLine': i,
                                        'replacement': init_line,
                                    },
                                ],
                            )
                        )
        
        # == None instead of is None
        if in_condition_stmt and ('== None' in code_part or '!= None' in code_part):
            warnings.append(Issue(i, 1, 'PY004', 'Użyj "is None" zamiast "== None"'))
            fixed_code = code_part
            fixed_code = re.sub(r'==\s*None\b', 'is None', fixed_code)
            fixed_code = re.sub(r'!=\s*None\b', 'is not None', fixed_code)
            if fixed_code != code_part:
                before = code_part.strip()
                after = fixed_code.strip()
                fixes.append(Fix(i, 'Zmieniono porównanie do None na is None/is not None', before, after))
                fixed_lines[i - 1] = fixed_code + comment_part
                current_line = fixed_lines[i - 1]
                code_part, comment_part = _split_python_comment(current_line)
                code_stripped = code_part.strip()
                stripped = current_line.strip()

        # type(x) == T instead of isinstance(x, T)
        m_type_cmp = None
        if in_condition_stmt:
            m_type_cmp = re.search(
                r'\btype\s*\(\s*(?P<expr>[^)]+?)\s*\)\s*==\s*(?P<typ>list|dict|tuple|set)\b',
                code_part,
            )
        if m_type_cmp:
            warnings.append(Issue(i, 1, 'PY007', 'Rozważ isinstance() zamiast type() == ...'))
            expr = m_type_cmp.group('expr')
            typ = m_type_cmp.group('typ')
            before = m_type_cmp.group(0)
            after = f'isinstance({expr}, {typ})'
            fixed_code = code_part.replace(before, after)
            if fixed_code != code_part:
                fixes.append(Fix(i, 'Zamieniono type(x) == T na isinstance(x, T)', before.strip(), after.strip()))
                fixed_lines[i - 1] = fixed_code + comment_part
                current_line = fixed_lines[i - 1]
                code_part, comment_part = _split_python_comment(current_line)
                code_stripped = code_part.strip()
                stripped = current_line.strip()

        # Using 'is'/'is not' for literal string/int comparison
        literal_pat = r'("[^"]*"|\'[^\']*\'|\d+)'
        tail_pat = r'(?=\s|$|:|,|\)|\]|\})'
        is_not_pat = rf'\bis\s+not\s+(?!None\b){literal_pat}{tail_pat}'
        is_pat = rf'\bis\s+(?!None\b){literal_pat}{tail_pat}'
        if in_condition_stmt and (re.search(is_not_pat, code_part) or re.search(is_pat, code_part)):
            warnings.append(Issue(i, 1, 'PY008', 'Nie używaj "is" do porównań z literałami - użyj =='))
            fixed_code = code_part
            fixed_code = re.sub(is_not_pat, r'!= \1', fixed_code)
            fixed_code = re.sub(is_pat, r'== \1', fixed_code)
            if fixed_code != code_part:
                fixes.append(Fix(i, 'Zamieniono "is" na == dla literałów', code_part.strip(), fixed_code.strip()))
                fixed_lines[i - 1] = fixed_code + comment_part
                current_line = fixed_lines[i - 1]
                code_part, comment_part = _split_python_comment(current_line)
                code_stripped = code_part.strip()
                stripped = current_line.strip()

    try:
        tree = ast.parse('\n'.join(fixed_lines))
        used_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import) and getattr(node, 'lineno', None):
                if len(node.names) != 1:
                    continue
                alias = node.names[0]
                imported = alias.asname or alias.name.split('.')[0]
                if imported in used_names:
                    continue
                line_no = int(node.lineno)
                before_line = fixed_lines[line_no - 1] if 0 < line_no <= len(fixed_lines) else ''
                warnings.append(Issue(line_no, 1, 'PY005', f'Import "{imported}" może być nieużywany'))
                edit = {'startLine': line_no, 'endLine': line_no, 'replacement': ''}
                fixes.append(Fix(line_no, f'Usunięto nieużywany import: {imported}', before_line.strip(), '', edits=[edit]))

            if isinstance(node, ast.ImportFrom) and getattr(node, 'lineno', None):
                if len(node.names) != 1:
                    continue
                alias = node.names[0]
                imported = alias.asname or alias.name
                if imported in used_names:
                    continue
                line_no = int(node.lineno)
                before_line = fixed_lines[line_no - 1] if 0 < line_no <= len(fixed_lines) else ''
                warnings.append(Issue(line_no, 1, 'PY005', f'Import "{imported}" może być nieużywany'))
                edit = {'startLine': line_no, 'endLine': line_no, 'replacement': ''}
                fixes.append(Fix(line_no, f'Usunięto nieużywany import: {imported}', before_line.strip(), '', edits=[edit]))
    except Exception:
        pass

    return AnalysisResult('python', code, '\n'.join(fixed_lines), errors, warnings, fixes)
