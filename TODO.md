# TODO

## Priorytety

### 🔴 Wysokie

- [ ] **Refaktoryzacja `analyzer.py`** — monolityczny plik (58KB) wymaga rozbicia na mniejsze moduły
- [ ] **Synchronizacja wersji** — VERSION, pyproject.toml i package.json powinny być spójne
- [ ] **Testy E2E** — rozbudować testy Playwright o nowe scenariusze (analiza wielu języków)
- [ ] **`make test`** — upewnić się, że `make test` działa dla frontend, backend i pactfix-py ✅ (done)
- [ ] **`make publish`** — publikacja paczki Python pactfix na PyPI

### 🟡 Średnie

- [ ] **Kontekstowe testowanie DSL** — generowanie mock środowisk dla Docker, SQL, Terraform, Kubernetes itp.; wykrywanie błędów konfiguracji nawet bez pełnego środowiska
- [ ] **Poprawa wykrywania błędów** — nie wszystkie błędy są wykrywane; rozbudowa reguł per język
- [ ] **Responsywność UI** — poprawa widoku webowego (`http://localhost:8081/`) na urządzeniach mobilnych
- [ ] **Cachowanie snippetów** — generowanie hashu przy każdej edycji, link ważny 24h, potem wygasa
- [ ] **Batch testing examples** — szybkie testowanie wszystkich projektów z `examples/*/*`

### 🟢 Niskie / Przyszłość

- [ ] **Traefik + K3s** — możliwość uruchamiania na zdalnym serwerze z obsługą `.env`, szyfrowanie domeny
- [ ] **AI-powered explanations** — integracja z llama.cpp do objaśnień poprawek
- [ ] **VSCode extension** — plugin do edytora
- [ ] **Collaborative debugging** — sesje wspólnego debugowania w czasie rzeczywistym
- [ ] **Integracja z GitHub PRs** — automatyczne komentarze w pull requestach

---

## Szybki start

```bash
# Instalacja
pip install -e pactfix-py

# Analiza pliku Python
python -m pactfix examples/python/faulty.py -o output.py --log-file log.json -v

# Analiza pliku Bash
python -m pactfix examples/bash/faulty.sh -o output.sh --log-file log.json -v

# Pipe z komentarzami
cat examples/python/faulty.py | pactfix -o output.py --comment
```