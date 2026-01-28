"""Systemd unit file analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


def analyze_systemd(code: str) -> AnalysisResult:
    """Analyze systemd unit file for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split('\n')
    fixed_lines = lines.copy()

    current_section = None
    has_description = False
    has_after = False
    has_restart = False
    has_user = False
    has_working_dir = False
    service_type = None

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        indent_str = line[:indent]

        if not stripped or stripped.startswith('#') or stripped.startswith(';'):
            continue

        # Section detection
        if stripped.startswith('[') and stripped.endswith(']'):
            current_section = stripped[1:-1]
            continue

        # SYSTEMD001: Description missing
        if stripped.startswith('Description='):
            has_description = True
            if len(stripped.split('=')[1].strip()) < 3:
                warnings.append(Issue(i, 1, 'SYSTEMD001', 'Opis usługi zbyt krótki'))

        # SYSTEMD002: After= dependency
        if stripped.startswith('After='):
            has_after = True

        # SYSTEMD003: Restart policy
        if stripped.startswith('Restart='):
            has_restart = True
            value = stripped.split('=')[1].strip()
            if value == 'no':
                warnings.append(Issue(i, 1, 'SYSTEMD003', 'Restart=no - usługa nie będzie restartowana'))

        # SYSTEMD004: User directive
        if stripped.startswith('User='):
            has_user = True
            user = stripped.split('=')[1].strip()
            if user == 'root':
                warnings.append(Issue(i, 1, 'SYSTEMD004', 'Usługa jako root - rozważ dedykowanego użytkownika'))

        # SYSTEMD005: WorkingDirectory
        if stripped.startswith('WorkingDirectory='):
            has_working_dir = True

        # SYSTEMD006: Type directive
        if stripped.startswith('Type='):
            service_type = stripped.split('=')[1].strip()
            valid_types = ['simple', 'forking', 'oneshot', 'dbus', 'notify', 'idle']
            if service_type not in valid_types:
                errors.append(Issue(i, 1, 'SYSTEMD006', f'Nieprawidłowy Type: {service_type}'))

        # SYSTEMD007: ExecStart without absolute path
        if stripped.startswith('ExecStart='):
            cmd = stripped.split('=')[1].strip()
            if cmd and not cmd.startswith('/') and not cmd.startswith('-/'):
                errors.append(Issue(i, 1, 'SYSTEMD007', 'ExecStart musi używać absolutnej ścieżki'))

        # SYSTEMD008: Environment with hardcoded secrets
        if stripped.startswith('Environment='):
            secret_patterns = ['PASSWORD', 'SECRET', 'API_KEY', 'TOKEN']
            for pattern in secret_patterns:
                if pattern in stripped.upper() and '${' not in stripped:
                    errors.append(Issue(i, 1, 'SYSTEMD008', f'Hardcoded {pattern} - użyj EnvironmentFile'))

        # SYSTEMD009: Missing RestartSec
        if has_restart and stripped.startswith('Restart=') and 'always' in stripped.lower():
            next_lines = '\n'.join(lines[i:i+5])
            if 'RestartSec=' not in next_lines:
                warnings.append(Issue(i, 1, 'SYSTEMD009', 'Restart=always bez RestartSec'))

        # SYSTEMD010: PrivateTmp for security
        if current_section == 'Service':
            if stripped.startswith('PrivateTmp='):
                if 'false' in stripped.lower():
                    warnings.append(Issue(i, 1, 'SYSTEMD010', 'PrivateTmp=false - rozważ true dla bezpieczeństwa'))

        # SYSTEMD011: ProtectSystem
        if stripped.startswith('ProtectSystem='):
            value = stripped.split('=')[1].strip()
            if value not in ['full', 'strict', 'true']:
                warnings.append(Issue(i, 1, 'SYSTEMD011', 'ProtectSystem - rozważ strict lub full'))

        # SYSTEMD012: NoNewPrivileges
        if stripped.startswith('NoNewPrivileges='):
            if 'false' in stripped.lower():
                warnings.append(Issue(i, 1, 'SYSTEMD012', 'NoNewPrivileges=false - rozważ true'))

        # SYSTEMD013: TimeoutStartSec/TimeoutStopSec
        if 'Timeout' in stripped and 'infinity' in stripped.lower():
            warnings.append(Issue(i, 1, 'SYSTEMD013', 'Timeout=infinity może blokować system'))

        # SYSTEMD014: WantedBy in Install section
        if current_section == 'Install' and stripped.startswith('WantedBy='):
            pass  # Good

        # SYSTEMD015: KillMode
        if stripped.startswith('KillMode='):
            if 'none' in stripped.lower():
                warnings.append(Issue(i, 1, 'SYSTEMD015', 'KillMode=none - procesy mogą nie być zabijane'))

    # Post-analysis checks
    if not has_description:
        warnings.append(Issue(1, 1, 'SYSTEMD001', 'Brak Description w sekcji [Unit]'))

    if not has_restart:
        warnings.append(Issue(1, 1, 'SYSTEMD003', 'Brak polityki Restart'))

    if not has_user:
        warnings.append(Issue(1, 1, 'SYSTEMD004', 'Brak User= - usługa będzie działać jako root'))

    return AnalysisResult('systemd', code, '\n'.join(fixed_lines), errors, warnings, fixes)
