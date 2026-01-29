import re
from typing import List, Dict, Set, Tuple

from ..analyzer import Issue, Fix, AnalysisResult


def analyze_terraform(code: str) -> AnalysisResult:
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []

    lines = code.splitlines()
    fixed_lines = lines.copy()

    resources: List[Dict[str, str]] = []
    variables_defined: Set[str] = set()
    variables_used: Set[str] = set()
    providers: List[str] = []
    
    # Track resource blocks for context
    current_resource = None
    resource_start_line = 0

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Track resource blocks
        if stripped.startswith('resource "'):
            match = re.search(r'resource\s+"([^"]+)"\s+"([^"]+)"', stripped)
            if match:
                current_resource = {
                    'type': match.group(1),
                    'name': match.group(2),
                    'start_line': i
                }
                resources.append(current_resource)
                resource_start_line = i
            continue
        
        # End of resource block
        if current_resource and stripped == '}' and i > resource_start_line:
            current_resource = None
        
        # Track variables
        if stripped.startswith('variable "'):
            match = re.search(r'variable\s+"([^"]+)"', stripped)
            if match:
                variables_defined.add(match.group(1))
        
        # Track variable usage
        for match in re.finditer(r'var\.(\w+)', stripped):
            variables_used.add(match.group(1))
        
        # Track providers
        if stripped.startswith('provider "'):
            match = re.search(r'provider\s+"([^"]+)"', stripped)
            if match:
                providers.append(match.group(1))
        
        # Check for hardcoded credentials and fix them
        credential_patterns = [
            (r'(access_key)\s*=\s*"([^"$]+)"', 'access_key'),
            (r'(secret_key)\s*=\s*"([^"$]+)"', 'secret_key'),
            (r'(password)\s*=\s*"([^"$]+)"', 'password'),
            (r'(token)\s*=\s*"([^"$]+)"', 'token'),
            (r'(api_key)\s*=\s*"([^"$]+)"', 'api_key'),
        ]
        
        for pattern, cred_type in credential_patterns:
            match = re.search(pattern, stripped, re.I)
            if match:
                errors.append(Issue(i, 1, 'TF001', f'Hardcoded {cred_type}'))
                # Create variable name
                var_name = f"{current_resource['type']}_{current_resource['name']}_{cred_type}" if current_resource else f"{cred_type}_var"
                # Replace with variable
                fixed_line = re.sub(pattern, f'{cred_type} = var.{var_name}', stripped)
                fixed_lines[i-1] = line.replace(stripped, fixed_line)
                fixes.append(Fix(i, f'Zamieniono {cred_type} na zmienną', match.group(0), f'{cred_type} = var.{var_name}'))
                
                # Add variable definition at the end
                var_def = f'\nvariable "{var_name}" {{\n  description = "{cred_type} for {current_resource["type"] if current_resource else "general"}"\n  type        = string\n  sensitive   = true\n}}\n'
                fixed_lines.append(var_def)
                fixes.append(Fix(len(lines) + 1, f'Dodano zmienną {var_name}', '', var_def.strip()))
        
        # Check for insecure CIDR blocks
        if 'cidr_blocks' in stripped and '0.0.0.0/0' in stripped:
            warnings.append(Issue(i, 1, 'TF002', '0.0.0.0/0 otwiera dostęp z internetu'))
            # Suggest more secure CIDR
            if 'aws_security_group' in (current_resource.get('type') if current_resource else ''):
                # For security groups, suggest corporate IP range
                fixed_line = stripped.replace('0.0.0.0/0', '10.0.0.0/8')
                fixed_lines[i-1] = line.replace(stripped, fixed_line)
                fixes.append(Fix(i, 'Zamieniono 0.0.0.0/0 na 10.0.0.0/8', '0.0.0.0/0', '10.0.0.0/8'))
        
        # Check for disabled encryption
        encryption_patterns = [
            (r'encrypted\s*=\s*false', 'encrypted = false'),
            (r'encryption_at_rest\s*=\s*false', 'encryption_at_rest = false'),
            (r'storage_encrypted\s*=\s*false', 'storage_encrypted = false'),
            (r'kms_key_id\s*=\s*""', 'kms_key_id = ""'),
        ]
        
        for pattern, text in encryption_patterns:
            if pattern in stripped.lower():
                errors.append(Issue(i, 1, 'TF003', 'Wyłączone szyfrowanie'))
                # Fix by enabling encryption
                if 'encrypted' in text.lower():
                    fixed_line = stripped.replace('false', 'true')
                elif 'kms_key_id' in text.lower():
                    fixed_line = stripped.replace('""', '"alias/aws/ebs"')
                else:
                    fixed_line = stripped.replace('false', 'true')
                
                fixed_lines[i-1] = line.replace(stripped, fixed_line)
                fixes.append(Fix(i, 'Włączono szyfrowanie', text, fixed_line))
        
        # Check for public S3 buckets
        if 'acl' in stripped and ('public-read' in stripped or 'public-read-write' in stripped):
            errors.append(Issue(i, 1, 'TF004', 'Publiczny bucket S3'))
            # Remove ACL or set to private
            fixed_line = re.sub(r'acl\s*=\s*"[^"]*"', 'acl = "private"', stripped)
            fixed_lines[i-1] = line.replace(stripped, fixed_line)
            fixes.append(Fix(i, 'Zmieniono ACL na private', stripped, fixed_line))
        
        # Check for missing resource tags
        if current_resource and current_resource['type'].startswith('aws_'):
            # Look for tags block
            has_tags = False
            for j in range(i, min(i + 20, len(lines))):
                if 'tags' in lines[j] and '=' not in lines[j]:
                    has_tags = True
                    break
                if lines[j].strip() == '}':
                    break
            
            if not has_tags and stripped == '}':
                # Add tags before closing brace
                indent = line[:len(line) - len(line.lstrip())]
                tags_block = [
                    f'{indent}  tags = {{',
                    f'{indent}    Environment = var.environment',
                    f'{indent}    Project     = var.project_name',
                    f'{indent}    ManagedBy   = "terraform"',
                    f'{indent}  }}',
                    line
                ]
                fixed_lines[i-1:i] = tags_block
                fixes.append(Fix(i, 'Dodano blok tags', '', 'tags = { ... }'))
        
        # Check for missing version constraints
        if stripped.startswith('terraform {'):
            # Look for required_version
            has_version = False
            for j in range(i, min(i + 10, len(lines))):
                if 'required_version' in lines[j]:
                    has_version = True
                    break
                if lines[j].strip() == '}':
                    break
            
            if not has_version and stripped == '}':
                # Add version constraint
                indent = line[:len(line) - len(line.lstrip())]
                version_line = f'{indent}  required_version = ">= 1.0"'
                fixed_lines[i-1:i] = [version_line, line]
                fixes.append(Fix(i, 'Dodano required_version', '', 'required_version = ">= 1.0"'))
        
        # Check for provider version constraints
        if stripped.startswith('provider "') and not any('version' in lines[j] for j in range(i, min(i + 10, len(lines))) if '}' not in lines[j]):
            provider_name = re.search(r'provider\s+"([^"]+)"', stripped).group(1)
            # Find closing brace
            brace_line = i
            for j in range(i, min(i + 20, len(lines))):
                if lines[j].strip() == '}':
                    brace_line = j
                    break
            
            if brace_line > i:
                indent = lines[brace_line - 1][:len(lines[brace_line - 1]) - len(lines[brace_line - 1].lstrip())]
                version_line = f'{indent}  version = "~> 5.0"'
                fixed_lines[brace_line - 1:brace_line - 1] = [version_line]
                fixes.append(Fix(brace_line, f'Dodano wersję providera {provider_name}', '', f'version = "~> 5.0"'))

    # Check for undefined variables
    undefined = variables_used - variables_defined
    for var in undefined:
        warnings.append(Issue(1, 1, 'TF005', f'Zmienna var.{var} nie jest zdefiniowana'))
        # Add variable definition at the end
        var_def = f'\nvariable "{var}" {{\n  description = "TODO: Add description"\n  type        = string\n}}\n'
        fixed_lines.append(var_def)
        fixes.append(Fix(len(lines) + 1, f'Dodano zmienną {var}', '', var_def.strip()))

    context = {
        'resources': resources,
        'providers': providers,
        'undefined_variables': list(undefined),
        'total_variables_defined': len(variables_defined),
        'total_variables_used': len(variables_used)
    }
    
    return AnalysisResult('terraform', code, '\n'.join(fixed_lines), errors, warnings, fixes, context)
