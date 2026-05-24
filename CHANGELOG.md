# Changelog

## Unreleased

- Add `npx github:quangdo126/geo-seo-codex` installer support.
- Remove public bootstrap scripts and raw GitHub one-line install commands.

## v0.3.1 - 2026-05-24

Public-release verification patch.

- Add `scripts/verify_public_release.py` to verify anonymous access to the repo API, raw bootstrap files, release zip, and release checksum.
- Add public release verification to contributor and release docs.
- Include the verifier in CI Python compilation.

## v0.3.0 - 2026-05-24

Production-readiness hardening for public installation and contribution.

- Add stdlib unit tests for the deterministic CLI audit, schema, llms.txt, and comparison paths.
- Expand CI to run on Linux, macOS, and Windows across Python 3.10 and 3.12.
- Add contributor, security, support, issue, PR, and release checklist templates.
- Change bootstrap installers to download the latest GitHub release asset instead of cloning `main`.
- Add SHA-256 release checksums and bootstrap checksum verification.

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
