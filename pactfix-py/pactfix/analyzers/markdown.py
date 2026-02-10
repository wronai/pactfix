"""Markdown analyzer - extracts fenced code blocks and analyzes each block."""

import re
from typing import List, Dict, Any

from ..analyzer import Issue, Fix, AnalysisResult


# Language aliases for fenced code block tags
_LANG_ALIASES = {
    'sh': 'bash',
    'shell': 'bash',
    'bash': 'bash',
    'python': 'python',
    'py': 'python',
    'python3': 'python',
    'php': 'php',
    'js': 'javascript',
    'javascript': 'javascript',
    'node': 'nodejs',
    'nodejs': 'nodejs',
    'ts': 'typescript',
    'typescript': 'typescript',
    'tsx': 'typescript',
    'docker': 'dockerfile',
    'dockerfile': 'dockerfile',
    'docker-compose': 'docker-compose',
    'sql': 'sql',
    'tf': 'terraform',
    'terraform': 'terraform',
    'hcl': 'terraform',
    'k8s': 'kubernetes',
    'kubernetes': 'kubernetes',
    'nginx': 'nginx',
    'github-actions': 'github-actions',
    'ansible': 'ansible',
    'go': 'go',
    'golang': 'go',
    'rust': 'rust',
    'rs': 'rust',
    'java': 'java',
    'csharp': 'csharp',
    'cs': 'csharp',
    'ruby': 'ruby',
    'rb': 'ruby',
    'makefile': 'makefile',
    'make': 'makefile',
    'yaml': 'yaml',
    'yml': 'yaml',
    'json': 'json',
    'jsonc': 'json',
    'toml': 'toml',
    'ini': 'ini',
    'html': 'html',
    'css': 'css',
    'apache': 'apache',
    'systemd': 'systemd',
    'helm': 'helm',
    'gitlab-ci': 'gitlab-ci',
    'jenkinsfile': 'jenkinsfile',
}


def analyze_markdown(code: str) -> AnalysisResult:
    """Analyze Markdown by extracting fenced code blocks and analyzing each."""
    # Import here to avoid circular imports
    from ..analyzer import analyze_code

    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []

    lines = code.split('\n')
    out_lines: List[str] = []

    in_fence = False
    fence_lang = None
    fence_start_line = None
    block_lines: List[str] = []

    blocks: List[Dict[str, Any]] = []

    def _flush_block(end_fence_line: int):
        nonlocal errors, warnings, fixes

        block_code = '\n'.join(block_lines)
        if not block_code.strip():
            out_lines.extend(block_lines)
            return

        forced = None
        if fence_lang:
            lang_tag = fence_lang.strip().lower()
            forced = _LANG_ALIASES.get(lang_tag, lang_tag)

        result = analyze_code(block_code, force_language=forced)

        fixed_block_lines = result.fixed_code.split('\n') if result.fixed_code else ['']

        content_start_line = (fence_start_line or 1) + 1
        for e in result.errors:
            errors.append(Issue(
                line=content_start_line + (e.line - 1),
                column=e.column,
                code=e.code,
                message=e.message,
                severity=e.severity,
            ))
        for w in result.warnings:
            warnings.append(Issue(
                line=content_start_line + (w.line - 1),
                column=w.column,
                code=w.code,
                message=w.message,
                severity=w.severity,
            ))
        for f in result.fixes:
            fixes.append(Fix(
                line=content_start_line + (f.line - 1),
                description=f.description,
                before=f.before,
                after=f.after,
            ))

        out_lines.extend(fixed_block_lines)

        blocks.append({
            'language': forced or result.language,
            'start_line': fence_start_line,
            'end_line': end_fence_line,
            'content_start_line': content_start_line,
            'errors': len(result.errors),
            'warnings': len(result.warnings),
            'fixes': len(result.fixes),
        })

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if not in_fence:
            if stripped.startswith('```'):
                in_fence = True
                fence_lang = stripped[3:].strip() or None
                fence_start_line = idx
                block_lines = []
                out_lines.append(line)
            else:
                out_lines.append(line)
        else:
            if stripped == '```':
                _flush_block(end_fence_line=idx)
                in_fence = False
                fence_lang = None
                fence_start_line = None
                block_lines = []
                out_lines.append(line)
            else:
                block_lines.append(line)

    # Unclosed fence: flush remaining block and keep content
    if in_fence and block_lines:
        _flush_block(end_fence_line=len(lines))
        # Don't re-add lines since _flush_block already added fixed lines

    fixed_code = '\n'.join(out_lines)

    return AnalysisResult(
        language='markdown',
        original_code=code,
        fixed_code=fixed_code,
        errors=errors,
        warnings=warnings,
        fixes=fixes,
        context={'blocks': blocks},
    )
