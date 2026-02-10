import re
from typing import List

from ..analyzer import Issue, Fix, AnalysisResult


def analyze_nginx(code: str) -> AnalysisResult:
    """Analyze nginx config."""
    errors, warnings, fixes = [], [], []
    lines = code.splitlines()
    fixed_lines = lines.copy()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        if 'server_tokens on' in stripped:
            warnings.append(Issue(i, 1, 'NGINX001', 'server_tokens ujawnia wersję'))
            fixed = stripped.replace('server_tokens on', 'server_tokens off')
            fixes.append(Fix(i, 'Wyłączono server_tokens', stripped, fixed))
            fixed_lines[i - 1] = line.replace(stripped, fixed)

        if 'autoindex on' in stripped:
            warnings.append(Issue(i, 1, 'NGINX002', 'autoindex ujawnia strukturę'))
            fixed = stripped.replace('autoindex on', 'autoindex off')
            fixes.append(Fix(i, 'Wyłączono autoindex', stripped, fixed))
            fixed_lines[i - 1] = line.replace(stripped, fixed)

        if 'ssl_protocols' in stripped and ('SSLv3' in stripped or 'TLSv1 ' in stripped or 'TLSv1.1' in stripped):
            errors.append(Issue(i, 1, 'NGINX003', 'Słabe protokoły SSL'))
            fixed = 'ssl_protocols TLSv1.2 TLSv1.3;'
            indent = re.match(r'^\s*', line).group(0)
            fixes.append(Fix(i, 'Ustawiono bezpieczne ssl_protocols', stripped, fixed))
            fixed_lines[i - 1] = indent + fixed

        if 'ssl_ciphers' in stripped:
            upper = stripped.upper()
            if 'RC4' in upper or 'MD5' in upper or 'DES' in upper:
                errors.append(Issue(i, 1, 'NGINX004', 'Słabe szyfry w ssl_ciphers'))
                fixed = "ssl_ciphers 'HIGH:!aNULL:!MD5:!3DES:!RC4';"
                indent = re.match(r'^\s*', line).group(0)
                fixes.append(Fix(i, 'Ustawiono bezpieczne ssl_ciphers', stripped, fixed))
                fixed_lines[i - 1] = indent + fixed

    server_blocks = []
    brace = 0
    in_server = False
    server_start = None
    server_level = None

    for idx, line in enumerate(fixed_lines):
        stripped = line.strip()
        if not in_server and re.match(r'^\s*server\s*\{\s*$', stripped):
            in_server = True
            server_start = idx
            server_level = brace

        brace += line.count('{') - line.count('}')

        if in_server and server_level is not None and brace == server_level and server_start is not None and idx > server_start:
            server_blocks.append((server_start, idx))
            in_server = False
            server_start = None
            server_level = None

    inserts = []
    all_text = '\n'.join(fixed_lines)
    has_any_ssl = bool(re.search(r'^\s*listen\s+443\b', all_text, re.MULTILINE)) or ('ssl_certificate' in all_text)

    for start, end in server_blocks:
        block_lines = fixed_lines[start:end + 1]
        block_text = '\n'.join(block_lines)
        has_ssl = bool(re.search(r'^\s*listen\s+443\b', block_text, re.MULTILINE)) or ' ssl' in block_text
        has_http = bool(re.search(r'^\s*listen\s+80\b', block_text, re.MULTILINE))
        has_headers = 'add_header' in block_text

        if has_http and has_any_ssl and 'return 301 https://' not in block_text:
            insert_at = end
            insert_indent = None
            for j in range(start, end + 1):
                if 'server_name' in fixed_lines[j]:
                    insert_at = j + 1
                    insert_indent = re.match(r'^\s*', fixed_lines[j]).group(0)
                    break
            if insert_indent is None:
                for j in range(start, end + 1):
                    if re.search(r'^\s*listen\s+80\b', fixed_lines[j]):
                        insert_at = j + 1
                        insert_indent = re.match(r'^\s*', fixed_lines[j]).group(0)
                        break
            if insert_indent is None:
                insert_indent = re.match(r'^\s*', fixed_lines[start]).group(0) + '    '

            inserts.append((insert_at, [insert_indent + 'return 301 https://$host$request_uri;'], start + 1))
            warnings.append(Issue(start + 1, 1, 'NGINX007', 'Brak przekierowania HTTP->HTTPS'))

        if has_ssl and not has_headers:
            warnings.append(Issue(start + 1, 1, 'NGINX005', 'Brak security headers'))
            insert_at = end
            insert_indent = None
            for j in range(start, end + 1):
                if 'server_name' in fixed_lines[j]:
                    insert_at = j + 1
                    insert_indent = re.match(r'^\s*', fixed_lines[j]).group(0)
                    break
            if insert_indent is None:
                insert_indent = re.match(r'^\s*', fixed_lines[start]).group(0) + '    '

            hdrs = [
                insert_indent + 'add_header X-Frame-Options "SAMEORIGIN" always;',
                insert_indent + 'add_header X-Content-Type-Options "nosniff" always;',
                insert_indent + 'add_header Referrer-Policy "strict-origin-when-cross-origin" always;',
                insert_indent + 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
            ]
            inserts.append((insert_at, hdrs, start + 1))

        if has_ssl and 'ssl_session_tickets' not in block_text:
            insert_at = end
            insert_indent = re.match(r'^\s*', fixed_lines[start]).group(0) + '    '
            inserts.append((insert_at, [insert_indent + 'ssl_session_tickets off;'], start + 1))
            warnings.append(Issue(start + 1, 1, 'NGINX008', 'Brak ssl_session_tickets off'))

        if has_ssl and 'ssl_prefer_server_ciphers' not in block_text:
            insert_at = end
            insert_indent = re.match(r'^\s*', fixed_lines[start]).group(0) + '    '
            inserts.append((insert_at, [insert_indent + 'ssl_prefer_server_ciphers on;'], start + 1))
            warnings.append(Issue(start + 1, 1, 'NGINX009', 'Brak ssl_prefer_server_ciphers on'))

        if re.search(r'^\s*location\s+~\s*/\\.\s*\{\s*$', block_text, re.MULTILINE):
            brace2 = 0
            in_loc = False
            loc_start = None
            loc_level = None
            for j in range(start, end + 1):
                l = fixed_lines[j]
                s = l.strip()
                if not in_loc and re.match(r'^\s*location\s+~\s*/\\.\s*\{\s*$', s):
                    in_loc = True
                    loc_start = j
                    loc_level = brace2
                brace2 += l.count('{') - l.count('}')
                if in_loc and loc_level is not None and brace2 == loc_level and loc_start is not None and j > loc_start:
                    loc_text = '\n'.join(fixed_lines[loc_start:j + 1])
                    if 'deny all;' not in loc_text:
                        indent = re.match(r'^\s*', fixed_lines[loc_start]).group(0) + '    '
                        inserts.append((loc_start + 1, [indent + 'deny all;'], loc_start + 1))
                        warnings.append(Issue(loc_start + 1, 1, 'NGINX006', 'Brak deny all dla dotfiles'))
                    in_loc = False
                    loc_start = None
                    loc_level = None

    for insert_at, new_lines, line_no in sorted(inserts, key=lambda x: x[0], reverse=True):
        for k, nl in enumerate(new_lines):
            fixed_lines.insert(insert_at + k, nl)
        fixes.append(Fix(line_no, 'Dodano ustawienia hardening', '', new_lines[0].strip()))

    return AnalysisResult('nginx', code, '\n'.join(fixed_lines), errors, warnings, fixes)
