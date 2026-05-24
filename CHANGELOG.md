# Changelog

## v0.2.0 - 2026-05-24

Release hardening and public-use features.

- Add `$geo doctor` health checks.
- Add `$geo self-test` install smoke test.
- Add one-line bootstrap installers for PowerShell and Bash.
- Add sample reports under `examples/`.
- Add `$geo compare-domain` for competitor comparisons.
- Add `$geo rewrite` for citation-ready rewrite starters.
- Add `$geo schema --generate` JSON-LD file generation.
- Add standardized `GEO-AUDIT.json` output through `$geo audit-json` and `$geo audit`.
- Add GitHub Actions CI checks.
- Add GitHub release packaging workflow.
- Add richer Codex skill metadata and icon assets.
- Add `python -m geo_seo` / `geo-seo` entrypoint support.

## v0.1.0 - 2026-05-24

Initial public release.

- Add Codex-native `geo` skill entry point.
- Add deterministic `geo_cli.py` helper for quick snapshots, citability, crawler access, llms.txt, and page extraction.
- Add Windows PowerShell and Bash installers.
- Add schema templates and command/scoring references.
- Add isolated Python virtual environment install flow under `~/.codex/skills/geo/.venv/`.
