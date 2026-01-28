"""Tests for pactfix analyzer."""

import re
import pytest
from pactfix.analyzer import (
    analyze_code, detect_language, 
    analyze_bash, analyze_python, analyze_dockerfile,
    analyze_sql, analyze_terraform, analyze_kubernetes,
    add_fix_comments
)


class TestLanguageDetection:
    def test_detect_bash_shebang(self):
        assert detect_language("#!/bin/bash\necho hello") == 'bash'
    
    def test_detect_python_shebang(self):
        assert detect_language("#!/usr/bin/env python3\nprint('hi')") == 'python'
    
    def test_detect_python_by_content(self):
        assert detect_language("def foo():\n    pass") == 'python'
    
    def test_detect_dockerfile(self):
        assert detect_language("FROM ubuntu\nRUN apt-get update") == 'dockerfile'
    
    def test_detect_docker_compose(self):
        assert detect_language("services:\n  web:\n    image: nginx") == 'docker-compose'
    
    def test_detect_kubernetes(self):
        assert detect_language("apiVersion: v1\nkind: Pod") == 'kubernetes'
    
    def test_detect_terraform(self):
        assert detect_language('resource "aws_instance" "web" {}') == 'terraform'
    
    def test_detect_sql(self):
        assert detect_language("SELECT * FROM users") == 'sql'
    
    def test_detect_by_filename(self):
        assert detect_language("FROM ubuntu", "Dockerfile") == 'dockerfile'
        assert detect_language("x", "test.py") == 'python'
        assert detect_language("x", "app.tf") == 'terraform'


class TestBashAnalysis:
    def test_cd_without_error_handling(self):
        result = analyze_bash("cd /tmp")
        assert any(w.code == 'SC2164' for w in result.warnings)
        assert any(f.description for f in result.fixes)

    def test_add_fix_comments_inserts_comment_above_fixed_line(self):
        result = analyze_bash("cd /tmp")
        out = add_fix_comments(result)
        lines = out.splitlines()
        assert lines[0].startswith("# pactfix:")
        assert "Dodano obsługę błędów" in lines[0]
        assert lines[1] == "cd /tmp || exit 1"
    
    def test_misplaced_quotes(self):
        result = analyze_bash('VAR="hello"world')
        assert any(e.code == 'SC1073' for e in result.errors)

    def test_brace_unbraced_vars_output_host(self):
        result = analyze_bash("echo $OUTPUT/$HOST")
        assert "echo ${OUTPUT}/${HOST}" in result.fixed_code
        assert any(w.code == 'BASH001' for w in result.warnings)
        assert any(f.description == 'Dodano klamerki do zmiennych' for f in result.fixes)


_BASH_BRACE_VAR_NAMES = [
    'OUTPUT', 'HOST', 'NAME', 'PATH', 'VAR', 'X', 'LONG_NAME', 'TMPDIR', 'USER', 'HOME'
]

_BASH_BRACE_TEMPLATES = [
    'echo ${VAR}',
    'echo "$${VAR}"',
]

_BASH_BRACE_SHOULD_CHANGE_TEMPLATES = [
    'echo ${VAR}',
]


def _gen_bash_brace_cases() -> list[str]:
    templates = [
        'echo ${VAR}',
        'echo "${VAR}"',
        'printf "%s" ${VAR}',
        'rm -v ${VAR}',
        'test -f ${VAR}/${HOST}',
        'cat ${VAR}/${HOST}',
        'scp ${VAR} user@${HOST}:/tmp/',
        'cmd --out=${VAR}',
        'echo pre${VAR}/post',
        'echo user@${HOST}:${VAR}',
    ]
    cases = []
    for var in _BASH_BRACE_VAR_NAMES:
        for tpl in templates:
            line = tpl.replace('${VAR}', f'${var}').replace('${HOST}', '$HOST')
            cases.append(line)
    return cases


@pytest.mark.parametrize('line', _gen_bash_brace_cases())
def test_brace_unbraced_vars_many_cases(line: str):
    result = analyze_bash(line)
    assert any(w.code == 'BASH001' for w in result.warnings)
    assert any(f.description == 'Dodano klamerki do zmiennych' for f in result.fixes)
    assert re.search(r'\$(?!\{)[A-Za-z_][A-Za-z0-9_]*', result.fixed_code) is None


@pytest.mark.parametrize(
    'line',
    [
        "echo '$OUTPUT/$HOST'",
        r"echo \$OUTPUT/\$HOST",
        'echo ${OUTPUT}/${HOST}',
        '# comment $OUTPUT/$HOST',
        'echo ok # $OUTPUT/$HOST',
        'echo $1',
        'echo $?'
    ],
)
def test_brace_unbraced_vars_does_not_change_these_cases(line: str):
    result = analyze_bash(line)
    assert result.fixed_code == line
    assert not any(w.code == 'BASH001' for w in result.warnings)


def test_brace_unbraced_vars_does_not_change_comment_part():
    result = analyze_bash('echo $OUTPUT # $HOST')
    assert result.fixed_code == 'echo ${OUTPUT} # $HOST'
    assert any(w.code == 'BASH001' for w in result.warnings)


class TestPythonAnalysis:
    def test_print_statement(self):
        result = analyze_python('print "hello"')
        assert any(e.code == 'PY001' for e in result.errors)
        assert len(result.fixes) > 0
    
    def test_bare_except(self):
        result = analyze_python("try:\n    pass\nexcept:\n    pass")
        assert any(w.code == 'PY002' for w in result.warnings)
    
    def test_mutable_default(self):
        result = analyze_python("def foo(x=[]):\n    pass")
        assert any(w.code == 'PY003' for w in result.warnings)

    def test_none_comparison_autofix(self):
        result = analyze_python("def f(x):\n    if x == None:\n        return 1\n    if x != None:\n        return 2")
        assert any(w.code == 'PY004' for w in result.warnings)
        assert any(f.description.startswith('Zmieniono porównanie do None') for f in result.fixes)
        assert 'if x is None:' in result.fixed_code
        assert 'if x is not None:' in result.fixed_code

    def test_type_equals_autofix(self):
        result = analyze_python("def f(obj):\n    if type(obj) == list:\n        return 1")
        assert any(w.code == 'PY007' for w in result.warnings)
        assert any('type(x) == T' in f.description for f in result.fixes)
        assert 'if isinstance(obj, list):' in result.fixed_code

    def test_is_literal_autofix(self):
        result = analyze_python("def f(a, b):\n    if a is \"test\":\n        return True\n    if b is 100:\n        return True")
        assert any(w.code == 'PY008' for w in result.warnings)
        assert any('Zamieniono "is" na == ' in f.description for f in result.fixes)
        assert 'if a == "test":' in result.fixed_code
        assert 'if b == 100:' in result.fixed_code


class TestDockerfileAnalysis:
    def test_latest_tag(self):
        result = analyze_dockerfile("FROM ubuntu")
        assert any(w.code == 'DOCKER001' for w in result.warnings)
    
    def test_hardcoded_secret(self):
        result = analyze_dockerfile("ENV PASSWORD=secret123")
        assert any(e.code == 'DOCKER007' for e in result.errors)
    
    def test_add_vs_copy(self):
        result = analyze_dockerfile("FROM ubuntu\nADD app.py /app/")
        assert any(w.code == 'DOCKER004' for w in result.warnings)
        assert any('COPY' in f.after for f in result.fixes)
    
    def test_no_user(self):
        result = analyze_dockerfile("FROM ubuntu\nRUN echo hi")
        assert any(w.code == 'DOCKER009' for w in result.warnings)


class TestSQLAnalysis:
    def test_select_star(self):
        result = analyze_sql("SELECT * FROM users")
        assert any(w.code == 'SQL001' for w in result.warnings)
    
    def test_update_without_where(self):
        result = analyze_sql("UPDATE users SET active = 1;")
        assert any(e.code == 'SQL003' for e in result.errors)
    
    def test_drop_without_if_exists(self):
        result = analyze_sql("DROP TABLE logs")
        assert any(w.code == 'SQL004' for w in result.warnings)
        assert any('IF EXISTS' in f.after for f in result.fixes)


class TestTerraformAnalysis:
    def test_hardcoded_credentials(self):
        result = analyze_terraform('access_key = "AKIA123456"')
        assert any(e.code == 'TF001' for e in result.errors)
    
    def test_public_cidr(self):
        result = analyze_terraform('cidr_blocks = ["0.0.0.0/0"]')
        assert any(w.code == 'TF002' for w in result.warnings)
    
    def test_public_s3(self):
        result = analyze_terraform('acl = "public-read"')
        assert any(e.code == 'TF004' for e in result.errors)


class TestKubernetesAnalysis:
    def test_privileged_container(self):
        result = analyze_kubernetes("apiVersion: v1\nkind: Pod\nspec:\n  containers:\n  - securityContext:\n      privileged: true")
        assert any(e.code == 'K8S001' for e in result.errors)
    
    def test_default_namespace(self):
        result = analyze_kubernetes("apiVersion: v1\nkind: Pod\nmetadata:\n  namespace: default")
        assert any(w.code == 'K8S007' for w in result.warnings)
    
    def test_latest_tag(self):
        result = analyze_kubernetes("apiVersion: v1\nkind: Deployment\nspec:\n  template:\n    spec:\n      containers:\n      - image: myapp:latest")
        assert any(w.code == 'K8S004' for w in result.warnings)


class TestIntegration:
    def test_analyze_code_auto_detect(self):
        result = analyze_code("#!/bin/bash\ncd /tmp")
        assert result.language == 'bash'
        assert len(result.warnings) > 0
    
    def test_analyze_code_force_language(self):
        result = analyze_code("some code", force_language='python')
        assert result.language == 'python'
    
    def test_result_to_dict(self):
        result = analyze_code("SELECT * FROM users")
        d = result.to_dict()
        assert 'language' in d
        assert 'errors' in d
        assert 'warnings' in d
        assert 'fixes' in d


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
