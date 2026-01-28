import unittest

import server


class MarkdownAnalysisTests(unittest.TestCase):
    def test_markdown_analyzes_fenced_blocks_with_aliases(self):
        md = """# Doc

```py
print \"Hello\"
```

```js
var x = 1
if (x == 1) {
  console.log(x)
}
```
"""
        result = server.analyze_code_multi(md, force_language="markdown")
        self.assertEqual(result.get("language"), "markdown")

        issues = (result.get("errors") or []) + (result.get("warnings") or [])
        codes = {i.get("code") for i in issues}

        self.assertIn("PY001", codes)
        self.assertIn("JS001", codes)

        fixed = result.get("fixedCode") or ""
        self.assertIn("```py", fixed)
        self.assertIn("```js", fixed)
        self.assertIn('print("Hello")', fixed)
        self.assertIn("let x", fixed)

    def test_markdown_analyzes_config_blocks(self):
        md = """# Config

```docker-compose
services:
  web:
    image: nginx:latest
    privileged: true
    environment:
      - PASSWORD=hunter2
```
"""
        result = server.analyze_code_multi(md, force_language="markdown")
        issues = (result.get("errors") or []) + (result.get("warnings") or [])
        codes = {i.get("code") for i in issues}

        self.assertIn("COMPOSE002", codes)
        self.assertIn("COMPOSE005", codes)

    def test_markdown_unclosed_fence_does_not_crash(self):
        md = """# Unclosed

```bash
cd /tmp
echo $VAR
"""
        result = server.analyze_code_multi(md, force_language="markdown")
        fixed = result.get("fixedCode") or ""
        self.assertIn("```bash", fixed)
        self.assertIn("cd /tmp", fixed)


if __name__ == "__main__":
    unittest.main()
