# GEO-SEO Codex

GEO-SEO Codex is a Codex CLI skill for auditing and improving website visibility in AI-powered search and answer engines. It focuses on Generative Engine Optimization (GEO) while keeping traditional SEO foundations in scope.

Current release: `v0.1.0`

## Requirements

- Codex CLI
- Python 3.8+
- Git
- PowerShell 7 on Windows, or Bash on macOS/Linux

## Install

Clone the repository:

```bash
git clone git@github.com:quangdo126/geo-seo-codex.git
cd geo-seo-codex
```

Windows PowerShell 7:

```powershell
./install.ps1
```

macOS/Linux or Git Bash:

```bash
./install.sh
```

The installer copies the skill to `~/.codex/skills/geo/`, creates an isolated virtual environment at `~/.codex/skills/geo/.venv/`, and installs the Python dependencies from `requirements.txt`.

## Verify

After installing, open Codex CLI and run:

```text
$geo quick https://example.com
```

For a direct script smoke test:

```powershell
~/.codex/skills/geo/.venv/Scripts/python.exe ~/.codex/skills/geo/scripts/geo_cli.py quick https://example.com
```

On macOS/Linux:

```bash
~/.codex/skills/geo/.venv/bin/python ~/.codex/skills/geo/scripts/geo_cli.py quick https://example.com
```

## Use

Open Codex CLI and invoke the skill with `$geo`:

```text
$geo quick https://example.com
$geo audit https://example.com
$geo citability https://example.com/blog/article
$geo crawlers https://example.com
$geo llmstxt https://example.com --generate
$geo schema https://example.com
$geo report https://example.com
```

## What It Includes

```text
geo-seo-codex/
+-- SKILL.md
+-- agents/openai.yaml
+-- references/
+-- scripts/
+-- schema/
+-- install.ps1
+-- install.sh
+-- requirements.txt
```

`SKILL.md` is the Codex skill entry point. `scripts/geo_cli.py` provides deterministic checks for quick snapshots, citability, crawler access, llms.txt, and raw page extraction. The reference files keep command-specific instructions and scoring details out of the main skill body.

## Commands

| Command | Result |
|---|---|
| `$geo quick <url>` | Fast GEO visibility snapshot |
| `$geo audit <url>` | Full GEO + SEO audit report |
| `$geo citability <url>` | AI citation readiness report |
| `$geo crawlers <url>` | AI crawler access report |
| `$geo llmstxt <url>` | Analyze `/llms.txt` |
| `$geo llmstxt <url> --generate` | Generate deployable `llms.txt` |
| `$geo schema <url>` | Schema.org detection and recommendations |
| `$geo technical <url>` | Technical SEO and AI crawler foundations |
| `$geo content <url>` | Content E-E-A-T and answer-block audit |
| `$geo report <url>` | Client-ready Markdown report |
| `$geo report-pdf <url-or-json>` | PDF report from audit data |

## Local Data

Prospect and recurring-report workflows store local data under `~/.geo-prospects/`. That directory is not removed by deleting the skill.

## Privacy

The skill runs locally through Codex CLI and bundled Python scripts. Website audits make normal HTTP requests to the target sites and public sources being checked. The project does not send audit data to a project-owned analytics service.

## Uninstall

```bash
rm -rf ~/.codex/skills/geo
```

On Windows PowerShell:

```powershell
Remove-Item -Recurse -Force $HOME/.codex/skills/geo
```
