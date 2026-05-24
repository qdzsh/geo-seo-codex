# Release Checklist

Use this checklist before tagging a release.

## Preflight

- [ ] Working tree is clean.
- [ ] `VERSION` matches the intended release.
- [ ] `pyproject.toml` version matches `VERSION`.
- [ ] `CHANGELOG.md` has a dated entry for the release.
- [ ] README install commands are still accurate.

## Local Verification

- [ ] `python -m unittest discover -s tests -v`
- [ ] `python -m py_compile scripts/geo_cli.py scripts/fetch_page.py scripts/citability_scorer.py scripts/llmstxt_generator.py scripts/brand_scanner.py scripts/generate_pdf_report.py scripts/crm_dashboard.py scripts/webapp/app.py geo_seo/__init__.py geo_seo/__main__.py tests/test_geo_cli.py`
- [ ] `bash -n install.sh && bash -n bootstrap.sh`
- [ ] PowerShell parser passes for `install.ps1` and `bootstrap.ps1`
- [ ] `python scripts/geo_cli.py doctor`
- [ ] `python scripts/geo_cli.py self-test`
- [ ] `python -m geo_seo --help`
- [ ] `pip install .` followed by `geo-seo --help`
- [ ] Legacy reference scan passes.
- [ ] `python scripts/verify_public_release.py`

## Install Verification

- [ ] Clean clone from local repository installs successfully.
- [ ] Clean clone from GitHub installs successfully.
- [ ] Installed skill has `SKILL.md`, `scripts/`, `schema/`, `references/`, `agents/`, and `assets/`.
- [ ] Installed skill venv runs `geo_cli.py self-test`.

## GitHub Verification

- [ ] Push `main`.
- [ ] Push annotated tag `vX.Y.Z`.
- [ ] GitHub Actions CI passes on all matrix entries.
- [ ] Release is created with:
  - [ ] `geo-seo-codex.zip`
  - [ ] `geo-seo-codex.zip.sha256`
- [ ] Bootstrap install works from the latest release asset.
- [ ] Anonymous access to `qdzsh.dev` bootstrap files, release zip, and checksum returns HTTP 200.

## Post-Release

- [ ] Verify `gh release view vX.Y.Z`.
- [ ] Verify a fresh remote clone reports the expected `VERSION`.
- [ ] Verify one-line install commands in README.
