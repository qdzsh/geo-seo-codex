# Contributing

Thanks for improving GEO-SEO Codex. This project is a Codex CLI skill plus
deterministic Python helpers for GEO and SEO audits.

## Development Setup

```bash
git clone https://github.com/quangdo126/geo-seo-codex.git
cd geo-seo-codex
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
```

On Windows PowerShell:

```powershell
python -m venv .venv
./.venv/Scripts/Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Required Checks

Run these before opening a pull request:

```bash
python -m unittest discover -s tests -v
python -m py_compile scripts/geo_cli.py scripts/fetch_page.py scripts/citability_scorer.py scripts/llmstxt_generator.py scripts/brand_scanner.py scripts/generate_pdf_report.py scripts/crm_dashboard.py scripts/webapp/app.py geo_seo/__init__.py geo_seo/__main__.py tests/test_geo_cli.py
python scripts/geo_cli.py doctor
python -m geo_seo --help
geo-seo --help
```

For release verification, also confirm anonymous public access:

```bash
python scripts/verify_public_release.py --tag vX.Y.Z
```

Also check installer syntax:

```bash
bash -n install.sh
bash -n bootstrap.sh
```

PowerShell parser check:

```powershell
$tokens = $null
$errors = $null
$null = [System.Management.Automation.Language.Parser]::ParseFile("install.ps1", [ref]$tokens, [ref]$errors)
if ($errors.Count -gt 0) { $errors | ForEach-Object { Write-Error $_ }; exit 1 }
$null = [System.Management.Automation.Language.Parser]::ParseFile("bootstrap.ps1", [ref]$tokens, [ref]$errors)
if ($errors.Count -gt 0) { $errors | ForEach-Object { Write-Error $_ }; exit 1 }
```

## Pull Request Guidelines

- Keep the skill Codex-only.
- Do not add references to other agent runtimes or legacy project names.
- Keep deterministic logic in `scripts/geo_cli.py` or helper scripts.
- Keep guidance and workflows in `SKILL.md` and `references/`.
- Add or update tests for new deterministic behavior.
- Update `README.md` and `CHANGELOG.md` for public-facing changes.

## Release Process

See [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md).
