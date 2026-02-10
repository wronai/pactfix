"""Multi-language code and config file analyzer."""

import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path

SUPPORTED_LANGUAGES = [
    'bash', 'python', 'php', 'javascript', 'nodejs',
    'dockerfile', 'docker-compose', 'sql', 'terraform',
    'kubernetes', 'nginx', 'github-actions', 'ansible',
    'typescript', 'go', 'rust', 'java', 'csharp', 'ruby',
    'makefile', 'yaml', 'apache', 'systemd', 'html', 'css',
    'json', 'toml', 'ini',
    'helm', 'gitlab-ci', 'jenkinsfile', 'markdown', 'markpact']

@dataclass
class Issue:
    line: int
    column: int
    code: str
    message: str
    severity: str = "warning"

@dataclass
class Fix:
    line: int
    description: str
    before: str
    after: str
    edits: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class AnalysisResult:
    language: str
    original_code: str
    fixed_code: str
    errors: List[Issue] = field(default_factory=list)
    warnings: List[Issue] = field(default_factory=list)
    fixes: List[Fix] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'language': self.language,
            'originalCode': self.original_code,
            'fixedCode': self.fixed_code,
            'errors': [asdict(e) for e in self.errors],
            'warnings': [asdict(w) for w in self.warnings],
            'fixes': [{**asdict(f), 'message': f.description} for f in self.fixes],
            'context': self.context
        }


def detect_language(code: str, filename: str = None) -> str:
    """Detect the language/format of the code."""
    lines = code.strip().split('\n')
    first_line = lines[0] if lines else ''
    
    if filename:
        fn_lower = filename.lower()
        fn_name = Path(filename).name.lower()
        
        if fn_name == 'dockerfile' or fn_lower.endswith('/dockerfile'):
            return 'dockerfile'
        if any(fn_lower.endswith(x) for x in ['docker-compose.yml', 'docker-compose.yaml', 'compose.yml', 'compose.yaml']):
            return 'docker-compose'
        if fn_lower.endswith('.tf'):
            return 'terraform'
        if fn_lower.endswith('.sql'):
            return 'sql'
        if fn_lower.endswith('nginx.conf') or '.nginx' in fn_lower:
            return 'nginx'
        if fn_lower.endswith(('.yml', '.yaml')) and ('workflow' in fn_lower or '.github' in fn_lower):
            return 'github-actions'
        if fn_name in ('.gitlab-ci.yml', '.gitlab-ci.yaml'):
            return 'gitlab-ci'
        if any(x in fn_lower for x in ['playbook', 'ansible']):
            return 'ansible'
        if fn_name in ('chart.yaml', 'chart.yml', 'values.yaml', 'values.yml'):
            return 'helm'
        if '/templates/' in fn_lower and fn_lower.endswith(('.yml', '.yaml')):
            return 'helm'
        if fn_lower.endswith(('.tpl', '.gotmpl')):
            return 'helm'
        if fn_lower.endswith('.py'):
            return 'python'
        if fn_lower.endswith('.php'):
            return 'php'
        if fn_lower.endswith('.js'):
            if 'require(' in code or 'module.exports' in code:
                return 'nodejs'
            return 'javascript'
        if fn_lower.endswith('.sh'):
            return 'bash'
        if fn_lower.endswith('.ts') or fn_lower.endswith('.tsx'):
            return 'typescript'
        if fn_lower.endswith('.go'):
            return 'go'
        if fn_lower.endswith('.rs'):
            return 'rust'
        if fn_lower.endswith('.java'):
            return 'java'
        if fn_lower.endswith('.cs'):
            return 'csharp'
        if fn_lower.endswith('.rb'):
            return 'ruby'
        if fn_lower.endswith('.json') or fn_lower.endswith('.jsonc'):
            return 'json'
        if fn_lower.endswith('.toml'):
            return 'toml'
        if fn_lower.endswith('.ini') or fn_lower.endswith('.cfg'):
            return 'ini'
        if fn_name == 'makefile' or fn_lower.endswith('.mk'):
            return 'makefile'
        if fn_lower.endswith('.html') or fn_lower.endswith('.htm'):
            return 'html'
        if fn_lower.endswith('.css'):
            return 'css'
        if fn_lower.endswith('.conf') and 'apache' in fn_lower:
            return 'apache'
        if fn_lower.endswith('.service') or fn_lower.endswith('.timer'):
            return 'systemd'
        if fn_lower.endswith('.md') or fn_lower.endswith('.markdown') or fn_lower.endswith('.mdx'):
            if 'markpact:' in code:
                return 'markpact'
            return 'markdown'
        if fn_name == 'jenkinsfile':
            return 'jenkinsfile'
        if fn_lower.endswith(('.yml', '.yaml')):
            # Check for specific YAML types first
            if 'workflow' in fn_lower or '.github' in fn_lower:
                return 'github-actions'
            if fn_name in ('.gitlab-ci.yml', '.gitlab-ci.yaml'):
                return 'gitlab-ci'
            if fn_name in ('chart.yaml', 'chart.yml', 'values.yaml', 'values.yml'):
                return 'helm'
            if '/templates/' in fn_lower:
                return 'helm'
            # Check for Kubernetes patterns in filename
            if any(x in fn_lower for x in ['deployment', 'service', 'configmap', 'secret', 'ingress', 'statefulset', 'daemonset', 'cronjob']):
                return 'kubernetes'
            return 'yaml'

    # Content-based detection
    if any(line.strip().upper().startswith(('FROM ', 'RUN ', 'COPY ', 'ENTRYPOINT ')) for line in lines[:20]):
        if 'FROM ' in code.upper():
            return 'dockerfile'
    
    if 'services:' in code and ('image:' in code or 'build:' in code):
        return 'docker-compose'
    
    if 'apiVersion:' in code and 'kind:' in code:
        return 'kubernetes'
    
    if 'resource "' in code or 'provider "' in code or 'variable "' in code:
        return 'terraform'
    
    sql_keywords = ['SELECT ', 'INSERT ', 'UPDATE ', 'DELETE ', 'CREATE TABLE', 'DROP ']
    if any(kw in code.upper() for kw in sql_keywords):
        return 'sql'
    
    if 'on:' in code and ('push:' in code or 'pull_request:' in code) and 'jobs:' in code:
        return 'github-actions'
    
    if 'stages:' in code and 'script:' in code and ('.gitlab-ci' in (filename or '').lower() or 'gitlab' in code.lower()):
        return 'gitlab-ci'

    if ('pipeline {' in code or 'node {' in code) and ('stage(' in code or 'stages {' in code):
        return 'jenkinsfile'
    
    if '- hosts:' in code or ('- name:' in code and 'tasks:' in code):
        return 'ansible'

    if '{{' in code and '}}' in code and ('.Values' in code or '.Release' in code or '.Chart' in code):
        return 'helm'
    
    if 'server {' in code or 'location ' in code:
        return 'nginx'
    
    # TypeScript detection
    if 'interface ' in code and '{' in code and (':' in code or 'export ' in code):
        return 'typescript'
    
    # Go detection
    if 'package ' in code and ('func ' in code or 'import (' in code):
        return 'go'
    
    # Rust detection
    if 'fn ' in code and ('let ' in code or 'use ' in code) and '::' in code:
        return 'rust'
    
    # Java detection
    if ('public class ' in code or 'private class ' in code) and 'void ' in code:
        return 'java'
    
    # C# detection
    if 'namespace ' in code and ('class ' in code or 'interface ' in code):
        return 'csharp'
    
    # Ruby detection
    if 'def ' in code and 'end' in code and ('class ' in code or 'module ' in code):
        return 'ruby'
    
    yaml_key_lines = sum(1 for l in lines if re.match(r'^\s*[A-Za-z0-9_.-]+\s*:\s*\S?', l))
    has_makefile_recipe = re.search(r'^\t(?!\s*[A-Za-z0-9_.-]+\s*:)\S', code, re.MULTILINE) is not None
    if yaml_key_lines >= 3 and not has_makefile_recipe and not re.search(r'^\s*(?:export\s+)?[A-Za-z_][A-Za-z0-9_]*\s*[:+?]?=\s*', code, re.MULTILINE):
        return 'yaml'
    
    # Makefile detection
    if (re.search(r'^[A-Za-z0-9_.-]+:\s*$', code, re.MULTILINE) or '.PHONY:' in code) and (has_makefile_recipe or '.PHONY:' in code):
        return 'makefile'
    
    # HTML detection
    if '<!DOCTYPE' in code.upper() or '<html' in code.lower():
        return 'html'
    
    # CSS detection
    if re.search(r'[.#]\w+\s*\{', code) and ':' in code and ';' in code:
        return 'css'
    
    # Apache config detection
    if '<VirtualHost' in code or 'ServerName' in code or 'DocumentRoot' in code:
        return 'apache'
    
    # Systemd unit detection
    if '[Unit]' in code or '[Service]' in code or '[Install]' in code:
        return 'systemd'
    
    if first_line.startswith('#!'):
        if 'python' in first_line.lower():
            return 'python'
        if 'bash' in first_line or 'sh' in first_line:
            return 'bash'
        if 'node' in first_line:
            return 'nodejs'
    
    if '<?php' in code:
        return 'php'
    
    python_patterns = [r'^def\s+\w+\s*\(', r'^class\s+\w+.*:', r'^import\s+\w+', r'^from\s+\w+\s+import']
    for pattern in python_patterns:
        if any(re.search(pattern, line) for line in lines):
            return 'python'
    
    if 'require(' in code or 'module.exports' in code:
        return 'nodejs'
    
    js_patterns = [r'\bconst\s+\w+\s*=', r'\blet\s+\w+\s*=', r'\bvar\s+\w+\s*=', r'function\s+\w+\s*\(']
    for pattern in js_patterns:
        if any(re.search(pattern, line) for line in lines):
            return 'javascript'
    
    # INI/TOML/JSON detection
    # JSON: starts with { or [ and contains :
    stripped_code = code.lstrip()
    if stripped_code.startswith('{') or stripped_code.startswith('['):
        if ':' in code:
            return 'json'
    # TOML: section headers [x] or key = value
    if re.search(r'^\s*\[[^\]]+\]\s*$', code, re.MULTILINE) and '=' in code:
        return 'toml'
    # INI: section headers [x] and key=value
    if re.search(r'^\s*\[[^\]]+\]\s*$', code, re.MULTILINE) and re.search(r'^\s*[^#;\[][^=]*=', code, re.MULTILINE):
        return 'ini'

    return 'bash'


def add_fix_comments(result: AnalysisResult) -> str:
    if result.language == 'json':
        return result.fixed_code

    if not result.fixes:
        return result.fixed_code

    comment_prefix_by_language = {
        'python': '#',
        'bash': '#',
        'php': '//',
        'javascript': '//',
        'nodejs': '//',
        'dockerfile': '#',
        'docker-compose': '#',
        'sql': '--',
        'terraform': '#',
        'kubernetes': '#',
        'nginx': '#',
        'github-actions': '#',
        'ansible': '#',
        'typescript': '//',
        'go': '//',
        'rust': '//',
        'java': '//',
        'csharp': '//',
        'ruby': '#',
        'makefile': '#',
        'yaml': '#',
        'helm': '#',
        'toml': '#',
        'ini': ';',
        'apache': '#',
        'systemd': '#',
        'html': '<!--',
        'css': '/*',
        'gitlab-ci': '#',
        'jenkinsfile': '//',
    }
    comment_suffix_by_language = {
        'html': ' -->',
        'css': ' */',
    }
    prefix = comment_prefix_by_language.get(result.language, '#')
    suffix = comment_suffix_by_language.get(result.language, '')

    lines = result.fixed_code.split('\n')
    fixes_by_line: Dict[int, List[Fix]] = {}
    for fx in result.fixes:
        fixes_by_line.setdefault(fx.line, []).append(fx)

    for line_no in sorted(fixes_by_line.keys(), reverse=True):
        idx = line_no - 1
        if idx < 0 or idx >= len(lines):
            continue

        indent_match = re.match(r'^\s*', lines[idx])
        indent = indent_match.group(0) if indent_match else ''

        parts = []
        for fx in fixes_by_line[line_no]:
            before = (fx.before or '').strip().replace('\n', ' ')
            if len(before) > 80:
                before = before[:77] + '...'
            parts.append(f"{fx.description} (was: {before})")

        msg = '; '.join(parts)
        if len(msg) > 220:
            msg = msg[:217] + '...'

        comment_line = f"{indent}{prefix} pactfix: {msg}{suffix}"
        lines.insert(idx, comment_line)

    return '\n'.join(lines)


def _apply_edits_to_lines(lines: List[str], edits: List[Dict[str, Any]]) -> List[str]:
    if not edits:
        return lines

    sorted_edits = sorted(
        edits,
        key=lambda e: (-(int(e.get('startLine') or 0)), -(int(e.get('endLine') or 0))),
    )

    out = list(lines)
    for e in sorted_edits:
        try:
            start_line = int(e.get('startLine'))
            end_line = int(e.get('endLine'))
        except Exception:
            continue

        replacement = '' if e.get('replacement') is None else str(e.get('replacement'))
        replacement_lines = [] if replacement == '' else replacement.split('\n')

        start_idx = start_line - 1
        if start_idx < 0 or start_idx > len(out):
            continue

        if end_line < start_line:
            out[start_idx:start_idx] = replacement_lines
            continue

        end_idx = end_line - 1
        delete_count = max(0, min(len(out) - start_idx, end_idx - start_idx + 1))

        if e.get('preserveIndent') and delete_count == 1 and len(replacement_lines) == 1:
            indent_match = re.match(r'^\s*', out[start_idx] if start_idx < len(out) else '')
            indent = indent_match.group(0) if indent_match else ''
            without_indent = re.sub(r'^\s*', '', replacement_lines[0])
            replacement_lines = [indent + without_indent]

        out[start_idx:start_idx + delete_count] = replacement_lines

    return out


from .analyzers import (
    analyze_bash,
    analyze_python,
    analyze_php,
    analyze_javascript,
    analyze_dockerfile,
    analyze_sql,
    analyze_nginx,
    analyze_github_actions,
    analyze_ansible,
    analyze_typescript,
    analyze_go,
    analyze_rust,
    analyze_java,
    analyze_csharp,
    analyze_ruby,
    analyze_makefile,
    analyze_yaml,
    analyze_apache,
    analyze_systemd,
    analyze_html,
    analyze_css,
    analyze_json,
    analyze_toml,
    analyze_ini,
    analyze_helm,
    analyze_gitlab_ci,
    analyze_jenkinsfile,
    analyze_docker_compose,
    analyze_kubernetes,
    analyze_terraform,
    analyze_markdown,
    analyze_markpact,
)


def analyze_code(code: str, filename: str = None, force_language: str = None) -> AnalysisResult:
    """Main entry point for code analysis."""
    language = force_language or detect_language(code, filename)

    analyzers = {
        'bash': analyze_bash,
        'python': analyze_python,
        'php': analyze_php,
        'javascript': lambda c: analyze_javascript(c, False),
        'nodejs': lambda c: analyze_javascript(c, True),
        'dockerfile': analyze_dockerfile,
        'docker-compose': analyze_docker_compose,
        'sql': analyze_sql,
        'terraform': analyze_terraform,
        'kubernetes': analyze_kubernetes,
        'nginx': analyze_nginx,
        'github-actions': analyze_github_actions,
        'ansible': analyze_ansible,
        'gitlab-ci': analyze_gitlab_ci,
        'jenkinsfile': analyze_jenkinsfile,
        'typescript': analyze_typescript,
        'go': analyze_go,
        'rust': analyze_rust,
        'java': analyze_java,
        'csharp': analyze_csharp,
        'ruby': analyze_ruby,
        'makefile': analyze_makefile,
        'yaml': analyze_yaml,
        'apache': analyze_apache,
        'systemd': analyze_systemd,
        'html': analyze_html,
        'css': analyze_css,
        'helm': analyze_helm,
        'json': analyze_json,
        'toml': analyze_toml,
        'ini': analyze_ini,
        'markdown': analyze_markdown,
        'markpact': analyze_markpact,
    }

    analyzer = analyzers.get(language, analyze_bash)
    result = analyzer(code)
    result.language = language
    return result
