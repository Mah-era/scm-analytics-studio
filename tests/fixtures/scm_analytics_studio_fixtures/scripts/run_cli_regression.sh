#!/usr/bin/env bash
set -euo pipefail

SCM="${SCM:-python -m scm_analytics_studio.cli}"
FIXTURES="${FIXTURES:-fixtures}"
OUT="${OUT:-out}"
export SCM_OFFLINE=1
mkdir -p "$OUT"

$SCM analyze "$FIXTURES/13_cli_export/cli_smoke_small.csv" --offline --output "$OUT/smoke"
$SCM analyze "$FIXTURES/01_happy_path/full_integrated_dataset.csv" --offline --module all --export-format json --output "$OUT/full_integrated"
$SCM validate "$FIXTURES/12_validation_bad_data/bad_data_validation.csv" --offline --validation-only --output "$OUT/bad_data_validation.json"
$SCM kpi "$FIXTURES/01_happy_path/full_integrated_dataset.csv" --offline --expected "$FIXTURES/13_cli_export/golden_kpis.json" --output "$OUT/golden_kpi_actual.json"
$SCM fixture-regression "$FIXTURES/13_cli_export/batch_regression_set.json" --offline --manifest "$FIXTURES/13_cli_export/fixture_manifest.json" --output "$OUT/batch_regression"
