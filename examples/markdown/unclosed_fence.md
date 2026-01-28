# Pactfix Markdown - Unclosed fence

Ten plik zawiera niezamknięty fenced code block (edge-case parsera Markdown).

```bash
#!/bin/bash
cd /tmp
echo "this block is never closed"

I wszystko poniżej będzie traktowane jako treść code blocka.
