"""HTML analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


def analyze_html(code: str) -> AnalysisResult:
    """Analyze HTML for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split('\n')
    fixed_lines = lines.copy()

    has_doctype = False
    has_lang = False
    has_charset = False
    has_viewport = False
    has_title = False
    in_head = False
    in_body = False

    head_open_idx = None

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        lower = stripped.lower()
        indent = len(line) - len(line.lstrip())
        indent_str = line[:indent]

        # HTML001: DOCTYPE declaration
        if '<!doctype' in lower:
            has_doctype = True
            if 'html' not in lower:
                warnings.append(Issue(i, 1, 'HTML001', 'Użyj <!DOCTYPE html> dla HTML5'))

        # Track sections
        if '<head' in lower:
            in_head = True
            if head_open_idx is None:
                head_open_idx = i - 1
        if '</head' in lower:
            in_head = False
        if '<body' in lower:
            in_body = True
        if '</body' in lower:
            in_body = False

        # HTML002: lang attribute on html
        if '<html' in lower:
            if 'lang=' not in lower:
                warnings.append(Issue(i, 1, 'HTML002', 'Brak atrybutu lang na <html>'))
                if '<html' in stripped and '>' in stripped:
                    fixed = re.sub(r'<html(\s[^>]*)?>', lambda m: (m.group(0)[:-1] + ' lang="en">') if 'lang=' not in m.group(0).lower() else m.group(0), line, count=1, flags=re.I)
                    if fixed != line:
                        fixes.append(Fix(i, 'Dodano lang="en" do <html>', line.rstrip(), fixed.rstrip()))
                        fixed_lines[i - 1] = fixed
            else:
                has_lang = True

        # HTML003: charset meta tag
        if 'charset=' in lower or 'content-type' in lower:
            has_charset = True

        # HTML004: viewport meta tag
        if 'viewport' in lower:
            has_viewport = True

        # HTML005: title tag
        if '<title>' in lower:
            has_title = True
            if '</title>' in lower:
                content = re.search(r'<title>([^<]*)</title>', lower)
                if content and len(content.group(1).strip()) < 3:
                    warnings.append(Issue(i, 1, 'HTML005', 'Tytuł strony zbyt krótki'))

        # HTML006: img without alt
        if '<img' in lower and 'alt=' not in lower:
            errors.append(Issue(i, 1, 'HTML006', '<img> bez atrybutu alt - accessibility'))
            if '<img' in stripped and '>' in stripped:
                fixed = re.sub(r'<img\b', '<img alt=""', line, count=1, flags=re.I)
                if fixed != line:
                    fixes.append(Fix(i, 'Dodano alt="" do <img>', line.rstrip(), fixed.rstrip()))
                    fixed_lines[i - 1] = fixed

        # HTML007: inline styles
        if 'style="' in lower:
            warnings.append(Issue(i, 1, 'HTML007', 'Inline style - przenieś do CSS'))

        # HTML008: inline event handlers
        event_handlers = ['onclick=', 'onmouseover=', 'onsubmit=', 'onload=', 'onerror=']
        for handler in event_handlers:
            if handler in lower:
                warnings.append(Issue(i, 1, 'HTML008', f'Inline {handler[:-1]} - użyj addEventListener'))

        # HTML009: deprecated tags
        deprecated = ['<font', '<center', '<marquee', '<blink', '<b>', '<i>']
        for tag in deprecated:
            if tag in lower:
                warnings.append(Issue(i, 1, 'HTML009', f'Przestarzały tag {tag} - użyj CSS'))

        # HTML010: form without action
        if '<form' in lower and 'action=' not in lower:
            warnings.append(Issue(i, 1, 'HTML010', '<form> bez atrybutu action'))

        # HTML011: input without label
        if '<input' in lower and 'type=' in lower:
            if 'type="hidden"' not in lower and 'type="submit"' not in lower:
                if 'id=' not in lower and 'aria-label' not in lower:
                    warnings.append(Issue(i, 1, 'HTML011', '<input> bez id/aria-label dla label'))

        # HTML012: target="_blank" without rel
        if 'target="_blank"' in lower or "target='_blank'" in lower:
            if 'rel=' not in lower:
                warnings.append(Issue(i, 1, 'HTML012', 'target="_blank" bez rel="noopener noreferrer"'))
                fixed = line
                fixed = re.sub(r'target="_blank"', 'target="_blank" rel="noopener noreferrer"', fixed, flags=re.I)
                fixed = re.sub(r"target='_blank'", "target='_blank' rel='noopener noreferrer'", fixed, flags=re.I)
                if fixed != line:
                    fixes.append(Fix(i, 'Dodano rel="noopener noreferrer"', line.rstrip(), fixed.rstrip()))
                    fixed_lines[i - 1] = fixed

        # HTML013: http:// links (should use https)
        if 'href="http://' in lower or "href='http://" in lower:
            if 'localhost' not in lower and '127.0.0.1' not in lower:
                warnings.append(Issue(i, 1, 'HTML013', 'HTTP link - rozważ HTTPS'))

        # HTML014: empty href
        if 'href=""' in lower or "href=''" in lower or 'href="#"' in lower:
            warnings.append(Issue(i, 1, 'HTML014', 'Pusty href - użyj button lub prawidłowego linku'))

        # HTML015: table without headers
        if '<table' in lower:
            next_lines = '\n'.join(lines[i:i+10]).lower()
            if '<th' not in next_lines:
                warnings.append(Issue(i, 1, 'HTML015', '<table> bez <th> - accessibility'))

    # Post-analysis checks
    if not has_doctype:
        errors.append(Issue(1, 1, 'HTML001', 'Brak <!DOCTYPE html>'))
        fixed_lines.insert(0, '<!DOCTYPE html>')
        fixes.append(Fix(1, 'Dodano <!DOCTYPE html>', '', '<!DOCTYPE html>'))

    if not has_charset:
        warnings.append(Issue(1, 1, 'HTML003', 'Brak deklaracji charset'))
        insert_at = head_open_idx + 1 if head_open_idx is not None else 0
        fixed_lines.insert(insert_at, '    <meta charset="utf-8">')
        fixes.append(Fix(1, 'Dodano <meta charset="utf-8">', '', '<meta charset="utf-8">'))

    if not has_viewport:
        warnings.append(Issue(1, 1, 'HTML004', 'Brak meta viewport - problemy na mobile'))
        insert_at = head_open_idx + 2 if head_open_idx is not None else 0
        fixed_lines.insert(insert_at, '    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        fixes.append(Fix(1, 'Dodano meta viewport', '', '<meta name="viewport" content="width=device-width, initial-scale=1.0">'))

    if not has_title:
        warnings.append(Issue(1, 1, 'HTML005', 'Brak <title>'))
        insert_at = head_open_idx + 3 if head_open_idx is not None else 0
        fixed_lines.insert(insert_at, '    <title>Document</title>')
        fixes.append(Fix(1, 'Dodano <title>Document</title>', '', '<title>Document</title>'))

    return AnalysisResult('html', code, '\n'.join(fixed_lines), errors, warnings, fixes)
