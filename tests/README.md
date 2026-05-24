# Tests Folder

Test assets are organized by purpose:

| Folder | Purpose |
|---|---|
| `unit/` | Pytest tests for app logic, analytics modules, exports, CLI parity, MCP smoke, and fixture accuracy. |
| `regression/` | Broader offline regression scripts that exercise modules, charts, exports, SQLite, and CLI commands end to end. |
| `uat/` | Manual user acceptance testing checklist for frontend and workflow validation. |
| `fixtures/scm_analytics_studio_fixtures/` | Current structured fixture suite for TDD and QA. |
| `fixtures/legacy/` | Legacy fixture pack retained for old parser and edge-case coverage. |

Run the normal automated suite from the project root:

```bash
python -m pytest -q
```

Run the broader offline regression script:

```bash
python tests/regression/offline_feature_check.py
```

Run the current fixture regression suite:

```bash
python cli.py test-fixtures --manifest tests/fixtures/scm_analytics_studio_fixtures/00_manifest/manifest.csv
```
