"""Language-specific analyzers for pactfix."""

from .bash import analyze_bash
from .python_lang import analyze_python
from .php import analyze_php
from .javascript import analyze_javascript
from .dockerfile import analyze_dockerfile
from .sql import analyze_sql
from .nginx import analyze_nginx
from .github_actions import analyze_github_actions
from .ansible import analyze_ansible
from .typescript import analyze_typescript
from .go import analyze_go
from .rust import analyze_rust
from .java import analyze_java
from .csharp import analyze_csharp
from .ruby import analyze_ruby
from .makefile import analyze_makefile
from .yaml_generic import analyze_yaml
from .apache import analyze_apache
from .systemd import analyze_systemd
from .html import analyze_html
from .css import analyze_css
from .json_generic import analyze_json
from .toml_generic import analyze_toml
from .ini_generic import analyze_ini
from .helm import analyze_helm
from .gitlab_ci import analyze_gitlab_ci
from .jenkinsfile import analyze_jenkinsfile
from .docker_compose import analyze_docker_compose
from .kubernetes import analyze_kubernetes
from .terraform import analyze_terraform
from .markdown import analyze_markdown
from .markpact import analyze_markpact

__all__ = [
    'analyze_bash',
    'analyze_python',
    'analyze_php',
    'analyze_javascript',
    'analyze_dockerfile',
    'analyze_sql',
    'analyze_nginx',
    'analyze_github_actions',
    'analyze_ansible',
    'analyze_typescript',
    'analyze_go',
    'analyze_rust',
    'analyze_java',
    'analyze_csharp',
    'analyze_ruby',
    'analyze_makefile',
    'analyze_yaml',
    'analyze_apache',
    'analyze_systemd',
    'analyze_html',
    'analyze_css',
    'analyze_json',
    'analyze_toml',
    'analyze_ini',
    'analyze_helm',
    'analyze_gitlab_ci',
    'analyze_jenkinsfile',
    'analyze_docker_compose',
    'analyze_kubernetes',
    'analyze_terraform',
    'analyze_markdown',
    'analyze_markpact',
]
