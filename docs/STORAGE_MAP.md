# Storage Map

This app is offline-first. Uploaded files are read into the Streamlit session and are not copied into the project unless the user chooses an export or a SQLite save action.

## Runtime Data

| Data Type | Stored At | Created By | Notes |
|---|---|---|---|
| Uploaded CSV/XLS/XLSX contents | Streamlit session memory | File uploader | Cleared when the session ends or the app reloads. |
| Cleaned data preview | Streamlit session memory | Cleaning controls | Not persisted automatically. |
| Saved cleaned datasets | `data/scm_analytics_studio.sqlite` | `Save cleaned data to local SQLite` button or `python cli.py analyze --save-sqlite` | Stored as local SQLite tables with safe table names. |
| Mapping profiles | `data/scm_analytics_studio.sqlite` table `mapping_profiles` | `Save mapping` button or CLI `--save-mapping` | Reused from the sidebar on later sessions. |
| Dataset snapshot metadata | `data/scm_analytics_studio.sqlite` table `dataset_snapshots` | SQLite save actions | Tracks display name, row count, column count, and timestamps. |
| Audit history | `data/scm_analytics_studio.sqlite` table `audit_log` | App open, mapping save, dataset save, CLI workflows | Exportable from Settings/Help and CLI advanced exports. |
| Dashboard templates | `data/scm_analytics_studio.sqlite` table `dashboard_templates` | Settings/Help template save action | Stores local JSON template configuration. |
| User feedback | `data/scm_analytics_studio.sqlite` table `user_feedback` | Sidebar `Send Feedback` form | Stores optional name/contact, category, rating, message, dataset context, and timestamp. |
| Matplotlib font cache | `data/.matplotlib/` | Offline chart export | Local rendering cache only. |

## Project Inputs

| Folder | Purpose |
|---|---|
| `sample_data/` | Bundled demo and training files for normal app use. |
| `tests/fixtures/scm_analytics_studio_fixtures/` | Current fixture suite for QA, TDD, CLI regression, and data accuracy checks. |
| `tests/fixtures/legacy/` | Older fixture pack kept for compatibility and parser edge-case coverage. |
| `skills/` | Local JSON skill definitions used by the Workflow Assistant. |
| `config/` | Local integration configuration examples, including MCP client setup. |

## Generated Outputs

| Output Type | Stored At | Trigger |
|---|---|---|
| Cleaned CSV/XLSX | User browser download or `exports/<run>/` from CLI | Export Center or CLI analysis |
| KPI CSV/XLSX | User browser download or `exports/<run>/` from CLI | Export Center or CLI analysis |
| PDF dashboard summary | User browser download or `exports/<run>/` from CLI | Export Center or CLI analysis |
| PowerPoint summary | User browser download or `exports/<run>/` from CLI when enabled | Extended exports |
| Full dashboard workbook | User browser download or `exports/<run>/scm_dashboard_workbook.xlsx` | Extended exports |
| Chart HTML/PNG | User browser download or `exports/<run>/charts/` | Smart Chart or CLI analysis |
| Chart bundle ZIP | User browser download or `exports/<run>/chart_bundle.zip` | Extended exports |
| Data-quality issue report | User browser download or `exports/<run>/data_quality_issue_report.csv` | Extended exports |
| Failed-row quarantine | User browser download or `exports/<run>/failed_row_quarantine.csv` | Extended exports |
| User feedback export | User browser download from Data > Settings | Feedback table export |
| Mapping template JSON | User browser download or `exports/<run>/mapping_template.json` | Extended exports |
| Fixture regression report | `exports/fixture_regression/fixture_regression_report.csv` or chosen CLI output folder | `python cli.py test-fixtures` |

## Git Hygiene

Runtime folders are intentionally ignored except placeholders:

- `data/*.sqlite`
- `data/.matplotlib/`
- `exports/*`
- `.venv/`
- `.pytest_cache/`
- `__pycache__/`
- `.DS_Store`

This keeps source, docs, fixtures, tests, and sample data organized while allowing local runs to create private runtime artifacts.
