"""Apache config analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


def analyze_apache(code: str) -> AnalysisResult:
    """Analyze Apache configuration for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split('\n')
    fixed_lines = lines.copy()

    has_ssl = False
    has_security_headers = False
    server_tokens_set = False
    directory_listing = False

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        indent_str = line[:indent]

        if not stripped or stripped.startswith('#'):
            continue

        # APACHE001: ServerTokens not set to Prod
        if stripped.lower().startswith('servertokens'):
            server_tokens_set = True
            if 'Prod' not in stripped and 'ProductOnly' not in stripped:
                warnings.append(Issue(i, 1, 'APACHE001', 'ServerTokens powinien być ustawiony na Prod'))
                fixed = 'ServerTokens Prod'
                fixes.append(Fix(i, 'Ustawiono ServerTokens na Prod', stripped, fixed))
                fixed_lines[i-1] = indent_str + fixed

        # APACHE002: ServerSignature should be Off
        if stripped.lower().startswith('serversignature'):
            if 'Off' not in stripped:
                warnings.append(Issue(i, 1, 'APACHE002', 'ServerSignature powinien być Off'))
                fixed = 'ServerSignature Off'
                fixes.append(Fix(i, 'Ustawiono ServerSignature na Off', stripped, fixed))
                fixed_lines[i-1] = indent_str + fixed

        # APACHE003: TraceEnable should be Off
        if stripped.lower().startswith('traceenable'):
            if 'Off' not in stripped:
                errors.append(Issue(i, 1, 'APACHE003', 'TraceEnable powinien być Off (TRACE attack)'))

        # APACHE004: Options +Indexes enables directory listing
        if 'Options' in stripped and '+Indexes' in stripped:
            directory_listing = True
            warnings.append(Issue(i, 1, 'APACHE004', 'Directory listing włączony - usuń +Indexes'))

        # APACHE005: AllowOverride All is too permissive
        if stripped.lower().startswith('allowoverride') and 'All' in stripped:
            warnings.append(Issue(i, 1, 'APACHE005', 'AllowOverride All - rozważ bardziej restrykcyjne'))

        # APACHE006: SSL/TLS configuration
        if 'SSLEngine' in stripped and 'on' in stripped.lower():
            has_ssl = True

        # APACHE007: Weak SSL protocols
        if 'SSLProtocol' in stripped:
            if 'SSLv2' in stripped or 'SSLv3' in stripped or 'TLSv1 ' in stripped:
                errors.append(Issue(i, 1, 'APACHE007', 'Słabe protokoły SSL - użyj TLSv1.2+'))

        # APACHE008: Weak ciphers
        if 'SSLCipherSuite' in stripped:
            weak_ciphers = ['RC4', 'MD5', 'DES', 'EXPORT', 'NULL']
            for cipher in weak_ciphers:
                if cipher in stripped.upper():
                    errors.append(Issue(i, 1, 'APACHE008', f'Słaby cipher: {cipher}'))

        # APACHE009: Security headers
        if 'Header' in stripped:
            has_security_headers = True
            if 'X-Frame-Options' in stripped or 'X-Content-Type-Options' in stripped:
                pass  # Good

        # APACHE010: DocumentRoot outside standard paths
        if stripped.lower().startswith('documentroot'):
            path = stripped.split()[1] if len(stripped.split()) > 1 else ''
            if path and not path.startswith('/var/www') and not path.startswith('/srv'):
                warnings.append(Issue(i, 1, 'APACHE010', 'DocumentRoot w niestandardowej lokalizacji'))

        # APACHE011: Missing timeout settings
        if stripped.lower().startswith('timeout'):
            timeout_val = re.search(r'\d+', stripped)
            if timeout_val and int(timeout_val.group()) > 300:
                warnings.append(Issue(i, 1, 'APACHE011', 'Timeout > 300s - może powodować DoS'))

        # APACHE012: KeepAlive should be On
        if stripped.lower().startswith('keepalive') and 'Off' in stripped:
            warnings.append(Issue(i, 1, 'APACHE012', 'KeepAlive Off - rozważ włączenie'))

        # APACHE013: Expose PHP version
        if 'Header' in stripped and 'X-Powered-By' in stripped:
            warnings.append(Issue(i, 1, 'APACHE013', 'X-Powered-By ujawnia technologię'))

        # APACHE014: Missing Require directive in Directory
        if '<Directory' in stripped and 'Require' not in '\n'.join(lines[i:i+10]):
            warnings.append(Issue(i, 1, 'APACHE014', 'Directory bez Require directive'))

    # Post-analysis checks
    if not server_tokens_set:
        warnings.append(Issue(1, 1, 'APACHE001', 'ServerTokens nie ustawiony - domyślnie ujawnia wersję'))

    if has_ssl and not has_security_headers:
        warnings.append(Issue(1, 1, 'APACHE009', 'SSL włączone ale brak security headers'))

    return AnalysisResult('apache', code, '\n'.join(fixed_lines), errors, warnings, fixes)
