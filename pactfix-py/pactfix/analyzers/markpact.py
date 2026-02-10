"""Analyzer for markpact files (executable Markdown with markpact:* codeblocks)."""

import re
from typing import List, Dict, Any

from ..analyzer import Issue, Fix, AnalysisResult

# Regex matching markpact codeblocks: ```lang markpact:kind meta\nbody\n```
MARKPACT_BLOCK_RE = re.compile(
    r"^```(?:(?P<lang>[^\s]+)\s+)?markpact:(?P<kind>\w+)(?:\s+(?P<meta>[^\n]+))?\n(?P<body>.*?)\n^```[ \t]*$",
    re.DOTALL | re.MULTILINE,
)

# Map from codeblock lang hints to pactfix language names
LANG_MAP = {
    'python': 'python',
    'python3': 'python',
    'py': 'python',
    'bash': 'bash',
    'sh': 'bash',
    'shell': 'bash',
    'javascript': 'javascript',
    'js': 'javascript',
    'typescript': 'typescript',
    'ts': 'typescript',
    'go': 'go',
    'golang': 'go',
    'rust': 'rust',
    'rs': 'rust',
    'php': 'php',
    'ruby': 'ruby',
    'rb': 'ruby',
    'java': 'java',
    'sql': 'sql',
    'html': 'html',
    'css': 'css',
    'dockerfile': 'dockerfile',
    'docker': 'dockerfile',
    'yaml': 'yaml',
    'yml': 'yaml',
    'json': 'json',
    'toml': 'toml',
    'ini': 'ini',
    'nginx': 'nginx',
    'text': None,
}


def _resolve_language(lang: str, kind: str, meta: str, body: str) -> str | None:
    """Resolve pactfix language from block lang hint, kind, meta, and body."""
    if lang:
        mapped = LANG_MAP.get(lang.lower())
        if mapped:
            return mapped

    # Infer from kind
    if kind == 'deps':
        return None  # deps blocks are just package lists, skip analysis
    if kind == 'run':
        return 'bash'
    if kind == 'test':
        # markpact:test http -> skip (HTTP test DSL, not analyzable)
        if meta and meta.strip().lower().startswith('http'):
            return None
        return 'bash'

    # Infer from meta path= extension
    if meta:
        path_match = re.search(r'\bpath=(\S+)', meta)
        if path_match:
            path = path_match.group(1).lower()
            if path.endswith('.py'):
                return 'python'
            if path.endswith('.js'):
                return 'javascript'
            if path.endswith('.ts') or path.endswith('.tsx'):
                return 'typescript'
            if path.endswith('.go'):
                return 'go'
            if path.endswith('.rs'):
                return 'rust'
            if path.endswith('.php'):
                return 'php'
            if path.endswith('.rb'):
                return 'ruby'
            if path.endswith('.java'):
                return 'java'
            if path.endswith('.sh'):
                return 'bash'
            if path.endswith('.sql'):
                return 'sql'
            if path.endswith('.html') or path.endswith('.htm'):
                return 'html'
            if path.endswith('.css'):
                return 'css'
            if path.endswith(('.yml', '.yaml')):
                return 'yaml'
            if path.endswith('.json'):
                return 'json'
            if path.endswith('.toml'):
                return 'toml'
            if path == 'dockerfile' or 'dockerfile' in path:
                return 'dockerfile'

    return None


def _find_block_line(code: str, match: re.Match) -> int:
    """Return the 1-indexed line number where a regex match starts."""
    return code[:match.start()].count('\n') + 1


def analyze_markpact(code: str) -> AnalysisResult:
    """Analyze a markpact file by inspecting each markpact:* codeblock.

    Structural checks are performed on the markpact file itself (e.g. missing
    run block, missing deps). Each embedded codeblock is then analyzed using
    the appropriate language analyzer, and all issues are reported with line
    numbers relative to the original markpact file.
    """
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []

    blocks = list(MARKPACT_BLOCK_RE.finditer(code))

    if not blocks:
        warnings.append(Issue(1, 1, 'MP001', 'Brak bloków markpact:* — plik nie zawiera wykonywalnego kodu'))
        return AnalysisResult('markpact', code, code, errors, warnings, fixes)

    kinds_found = {m.group('kind') for m in blocks}

    # Structural checks
    if 'file' in kinds_found and 'run' not in kinds_found:
        warnings.append(Issue(1, 1, 'MP002', 'Brak bloku markpact:run — projekt nie ma punktu startowego'))

    if 'run' in kinds_found and 'deps' not in kinds_found:
        warnings.append(Issue(1, 1, 'MP003', 'Brak bloku markpact:deps — brak zdefiniowanych zależności'))

    # Per-block analysis
    # Import analyze_code lazily to avoid circular imports
    from ..analyzer import analyze_code

    context_blocks: List[Dict[str, Any]] = []

    for match in blocks:
        lang = (match.group('lang') or '').strip()
        kind = match.group('kind')
        meta = (match.group('meta') or '').strip()
        body = match.group('body').strip()
        block_start_line = _find_block_line(code, match)
        # Body starts after the opening ``` line
        body_start_line = block_start_line + 1

        resolved_lang = _resolve_language(lang, kind, meta, body)

        path_match = re.search(r'\bpath=(\S+)', meta) if meta else None
        block_path = path_match.group(1) if path_match else None

        block_info: Dict[str, Any] = {
            'kind': kind,
            'lang': lang,
            'resolved_lang': resolved_lang,
            'meta': meta,
            'path': block_path,
            'line': block_start_line,
            'issues': 0,
        }

        if not resolved_lang:
            context_blocks.append(block_info)
            continue

        # Run the language-specific analyzer on the block body
        result = analyze_code(body, filename=block_path, force_language=resolved_lang)

        block_label = f'markpact:{kind}'
        if block_path:
            block_label += f' path={block_path}'

        # Re-map line numbers from the sub-result to the markpact file
        for issue in result.errors:
            mapped_line = body_start_line + issue.line - 1
            errors.append(Issue(
                mapped_line, issue.column, issue.code,
                f'[{block_label}] {issue.message}',
                issue.severity,
            ))

        for issue in result.warnings:
            mapped_line = body_start_line + issue.line - 1
            warnings.append(Issue(
                mapped_line, issue.column, issue.code,
                f'[{block_label}] {issue.message}',
                issue.severity,
            ))

        for fix in result.fixes:
            mapped_line = body_start_line + fix.line - 1
            mapped_edits = []
            for edit in (fix.edits or []):
                mapped_edit = dict(edit)
                if 'startLine' in mapped_edit:
                    mapped_edit['startLine'] = body_start_line + int(mapped_edit['startLine']) - 1
                if 'endLine' in mapped_edit:
                    mapped_edit['endLine'] = body_start_line + int(mapped_edit['endLine']) - 1
                mapped_edits.append(mapped_edit)
            fixes.append(Fix(
                mapped_line, f'[{block_label}] {fix.description}',
                fix.before, fix.after, edits=mapped_edits,
            ))

        block_info['issues'] = len(result.errors) + len(result.warnings)
        context_blocks.append(block_info)

    context = {
        'blocks_total': len(blocks),
        'blocks_analyzed': sum(1 for b in context_blocks if b.get('resolved_lang')),
        'kinds': sorted(kinds_found),
        'blocks': context_blocks,
    }

    return AnalysisResult('markpact', code, code, errors, warnings, fixes, context)
