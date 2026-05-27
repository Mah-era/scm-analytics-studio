# Expected CLI behavior

Suggested smoke command patterns:

```bash
python -m scm_analytics_studio analyze tests/fixtures/cli/cli_orders_input.csv --output /tmp/scm_cli_out
python -m scm_analytics_studio analyze tests/fixtures/cli/legacy_cli_input.xls --output /tmp/scm_cli_out_legacy
```

Expected assertions:

- Process exits with code 0 for valid files.
- Process exits with a non-zero code and clear message for missing-column files.
- Output includes row count, stockout count, total purchase cost, late delivery count, and export paths when requested.
- Exported CSV/Excel/HTML/PDF/PNG artifacts are non-empty.
