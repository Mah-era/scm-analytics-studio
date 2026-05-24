# Project Structure

```text
scm_analytics_studio/
├── app.py                         # Streamlit UI at localhost:3000
├── cli.py                         # Batch analysis, exports, fixture runner, tools, skills
├── api_server.py                  # Local HTTP API integration server
├── mcp_server.py                  # Lightweight stdio MCP-style server
├── config/
│   └── mcp_client_config.example.json
├── docs/
│   ├── PROJECT_STRUCTURE.md          # File and folder layout
│   ├── PROJECT_REPORT.md             # Detailed project capability report
│   ├── PICKUP.md                     # LLM handoff dossier
│   ├── STORAGE_MAP.md                # Where data, exports, mappings, and logs live
│   ├── UAT_PLAN.md                   # User acceptance testing plan
│   └── USER_GUIDE.md                 # Frontend navigation guide
├── modules/
│   ├── advanced_features.py       # Advanced SCM analytics and exports
│   ├── chart_generator.py         # Plotly charts and PNG export bridge
│   ├── column_mapper.py           # SCM canonical field mapping
│   ├── data_cleaner.py            # Cleaning, type conversion, quality summary
│   ├── data_loader.py             # CSV/XLS/XLSX loading
│   ├── integration_gateway.py     # Shared MCP/API dataset + tool helpers
│   ├── skill_registry.py          # Built-in and custom workflow skills
│   ├── tool_registry.py           # Local callable SCM tools
│   ├── workflow_assistant.py      # Streamlit Workflow Assistant tab
│   └── *_analysis.py              # Domain dashboards
├── skills/
│   └── inventory_exception_review.json
├── sample_data/
├── tests/
│   ├── fixtures/
│   │   ├── legacy/                  # Original fixture pack, flattened by type
│   │   └── scm_analytics_studio_fixtures/
│   ├── regression/
│   │   └── offline_feature_check.py
│   ├── unit/
│   │   └── test_advanced_features.py
│   ├── uat/
│   │   └── UAT_CHECKLIST.md
├── data/                          # SQLite runtime data, ignored except .gitkeep
└── exports/                       # Generated exports, ignored except .gitkeep
```

## Runtime Outputs

Generated files belong in `exports/`. Local SQLite snapshots and audit data belong in `data/`. Both are intentionally ignored by git except their `.gitkeep` placeholders.

## Organization Rules

- App entry points stay at the project root: `app.py`, `cli.py`, `api_server.py`, and `mcp_server.py`.
- Reusable Python logic stays in `modules/`.
- User documentation stays in `docs/`.
- Manual UAT artifacts stay in `tests/uat/`.
- Unit tests stay in `tests/unit/`.
- Broader regression scripts stay in `tests/regression/`.
- QA fixtures stay in `tests/fixtures/`.
- User-facing example data stays in `sample_data/`.
- Runtime storage stays in `data/`.
- Generated reports and exports stay in `exports/`.
- Local skill definitions stay in `skills/`.
- Integration examples stay in `config/`.

## Integration Entry Points

- Streamlit UI: `python cli.py serve`
- Local HTTP API: `python cli.py api-server`
- MCP stdio server: `python cli.py mcp-server`
- Tool call from CLI: `python cli.py run-tool --tool forecast --input path/to/file.csv`
- Skill call from CLI: `python cli.py run-skill --skill inventory_planner --input path/to/file.csv`
