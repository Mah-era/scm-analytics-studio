# Fixture Folders

Fixtures are separated into current and legacy packs.

| Folder | Purpose |
|---|---|
| `scm_analytics_studio_fixtures/` | Current QA/TDD pack organized by domain: file formats, data cleaning, mapping, demand, inventory, procurement, logistics, warehouse, production/MRP, finance, validation, CLI/export, and offline deployment. |
| `legacy/` | Older pack kept for compatibility, parser regression, and historical edge cases. |

The default CLI fixture runner uses:

```text
tests/fixtures/scm_analytics_studio_fixtures/00_manifest/manifest.csv
```

Legacy fixtures can still be run explicitly:

```text
tests/fixtures/legacy/FIXTURE_MANIFEST.csv
```
