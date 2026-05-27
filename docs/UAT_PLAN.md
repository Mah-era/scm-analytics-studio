# UAT Plan

## Goal

Validate that SCM Analytics Studio is acceptable for offline business users who need to load supply chain files, clean and map data, analyze SCM performance, export reports, reuse mappings, and run CLI/integration workflows locally.

## UAT Scope

| Area | Included |
|---|---|
| Installation | Python environment, requirements, local launch. |
| UI | Streamlit app at `localhost:3000`, sidebar workflow, workspaces, filters, hover contrast, and slight target growth. |
| Data import | CSV, XLSX, XLS, multi-sheet workbooks, combined sheets, sample data. |
| Cleaning | Missing values, duplicates, date parsing, numeric parsing, messy headers. |
| Mapping | Auto-detect, manual mapping, saved mapping profiles, mapping template import/export. |
| Analytics | Data quality, planning, operations, finance, smart charts, workflow assistant. |
| Exports | CSV, XLSX, PDF, PPTX, full workbook, chart ZIP, glossary, audit, mapping template, SQLite backup. |
| Local storage | SQLite mappings, snapshots, audit log, dashboard templates. |
| CLI | Analysis, validation-only, fixture regression, fixture accuracy, tool calls, skill calls. |
| Integrations | Local HTTP API and MCP-style stdio server. |
| Offline behavior | No cloud/API dependency for core app after installation. |

## UAT Test Data

Use these sources:

- `sample_data/sample_scm_data.xlsx`
- `sample_data/integrated_scm_data.csv`
- `tests/fixtures/scm_analytics_studio_fixtures/`
- `tests/fixtures/legacy/`

The current fixture pack covers happy path data, messy files, bad data, forecasting, inventory, procurement, logistics, warehouse, production, MRP, finance, CLI/export, and offline deployment scenarios.

## UAT Execution Order

1. Run environment checks and open `http://localhost:3000`.
2. Load bundled sample data and verify the default dashboard.
3. Upload CSV and XLSX fixture files.
4. Test cleaning and mapping behavior.
5. Validate sidebar filters.
6. Walk through Data, Planning, Operations, Finance, and Exports workspaces.
7. Run all export actions and reopen output files.
8. Save a dataset and mapping to SQLite, reload both, and verify persistence.
9. Run CLI acceptance commands.
10. Run API and MCP smoke checks.
11. Run offline/no-network acceptance after dependencies are installed.

The detailed scenario checklist is stored at:

```text
tests/uat/UAT_CHECKLIST.md
```

## Entry Criteria

- Dependencies are installed.
- App starts on port 3000.
- Current fixture pack exists under `tests/fixtures/scm_analytics_studio_fixtures/`.
- Sample data exists under `sample_data/`.
- `data/` and `exports/` folders are present.

## Exit Criteria

- Pytest passes.
- Fixture regression passes for the current fixture pack.
- Fixture accuracy has zero tabular failures and golden KPI checks pass.
- Streamlit smoke test passes.
- UAT checklist scenarios pass or have documented exceptions.
- Generated exports open offline.
- User can identify where data is stored using `docs/STORAGE_MAP.md`.

## Known UAT Notes

- Legacy `.xls` fixtures are retained for edge-case coverage; legacy parser behavior can vary by local xlrd/Pandas compatibility.
- Uploads are session-only unless saved to SQLite or exported.
- Optional LLM summaries are disabled by default and are not required for offline analytics.
