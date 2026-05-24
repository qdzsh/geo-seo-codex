---
name: geo
description: GEO-first SEO toolkit for Codex CLI. Use for website audits, AI search visibility, Generative Engine Optimization, citability scoring, AI crawler access, llms.txt analysis or generation, brand/entity signals, platform readiness for ChatGPT/Claude/Perplexity/Gemini/Google AI Overviews, Schema.org recommendations, technical SEO, content E-E-A-T, client reports, proposals, and prospect workflows. Invoke explicitly as $geo.
metadata:
  short-description: GEO and SEO audits for AI search visibility
---

# GEO-SEO Codex Skill

Use this skill when the user asks for GEO, SEO, AI search visibility, website audit,
citability, AI crawler access, llms.txt, schema, content E-E-A-T, platform readiness,
or client-ready GEO reports.

## Invocation

- Native Codex form: `$geo <command> <url-or-domain>`.
- If the user gives only a URL and asks for an audit, default to `$geo audit <url>`.

## Runtime Layout

Installed layout:

```text
~/.codex/skills/geo/
+-- SKILL.md
+-- scripts/
|   +-- geo_cli.py
|   +-- fetch_page.py
|   +-- citability_scorer.py
|   +-- llmstxt_generator.py
|   +-- brand_scanner.py
|   +-- generate_pdf_report.py
+-- schema/
+-- references/
+-- .venv/
```

Prefer the installed virtual environment when running scripts:

- Windows PowerShell: `~/.codex/skills/geo/.venv/Scripts/python.exe ~/.codex/skills/geo/scripts/geo_cli.py quick https://example.com`
- macOS/Linux: `~/.codex/skills/geo/.venv/bin/python ~/.codex/skills/geo/scripts/geo_cli.py quick https://example.com`

If the installed path is missing, fall back to the current repository's `scripts/`
directory and the active Python interpreter.

## Commands

| Command | Result |
|---|---|
| `$geo doctor` | Local installation health check |
| `$geo self-test` | End-to-end smoke test |
| `$geo quick <url>` | Fast deterministic snapshot, inline by default |
| `$geo audit <url>` | Full GEO + SEO audit report |
| `$geo audit-json <url>` | Standardized `GEO-AUDIT.json` artifact |
| `$geo citability <url>` | `GEO-CITABILITY-SCORE.md` |
| `$geo rewrite <url>` | Citation-ready rewrite starters |
| `$geo crawlers <url>` | `GEO-CRAWLER-ACCESS.md` |
| `$geo llmstxt <url>` | Analyze `/llms.txt` |
| `$geo llmstxt <url> --generate` | Write deployable `llms.txt` |
| `$geo compare-domain <url> <competitor>` | Competitor GEO comparison |
| `$geo brands <url-or-brand>` | Brand/entity signal assessment |
| `$geo platforms <url>` | ChatGPT, Google AIO, Perplexity, Gemini, Copilot readiness |
| `$geo schema <url>` | Schema.org detection and JSON-LD recommendations |
| `$geo schema <url> --generate organization` | Generate JSON-LD file |
| `$geo technical <url>` | Technical SEO and AI-crawler foundation audit |
| `$geo content <url>` | E-E-A-T and AI-citable content audit |
| `$geo report <url>` | Client-ready Markdown report |
| `$geo report-pdf <url-or-json>` | PDF report using `generate_pdf_report.py` |
| `$geo prospect <cmd>` | CRM-lite prospect pipeline workflow |
| `$geo proposal <domain>` | Client proposal from audit findings |
| `$geo compare <domain>` | Monthly before/after delta report |

For command-specific workflow details, read `references/commands.md` only for the
command being executed. For score weights, read `references/scoring.md`.

## Deterministic Helpers

Use `scripts/geo_cli.py` for checks it supports before doing LLM synthesis:

```bash
python scripts/geo_cli.py quick https://example.com
python scripts/geo_cli.py doctor
python scripts/geo_cli.py self-test
python scripts/geo_cli.py audit-json https://example.com --out GEO-AUDIT.json
python scripts/geo_cli.py citability https://example.com/page --out GEO-CITABILITY-SCORE.md
python scripts/geo_cli.py rewrite https://example.com/page --out GEO-REWRITE-SUGGESTIONS.md
python scripts/geo_cli.py crawlers https://example.com --out GEO-CRAWLER-ACCESS.md
python scripts/geo_cli.py llmstxt https://example.com
python scripts/geo_cli.py llmstxt https://example.com --generate --out llms.txt
python scripts/geo_cli.py schema https://example.com --generate organization --out schema-organization.jsonld
python scripts/geo_cli.py compare-domain https://example.com https://competitor.com
python scripts/geo_cli.py fetch https://example.com --out audit-data.json
```

The helper output is evidence, not the final consulting answer. Use it to ground
findings, then add prioritization, business context, and implementation advice.

## Full Audit Workflow

For `$geo audit <url>`:

1. Normalize the URL to `https://domain` unless the user supplied `http://`.
2. Run deterministic discovery:
   - `geo_cli.py quick <url> --out GEO-QUICK-SNAPSHOT.md`
   - `geo_cli.py fetch <url> --out audit-data.json`
   - `geo_cli.py crawlers <url> --json --out crawler-data.json`
   - `geo_cli.py citability <url> --json --out citability-data.json`
   - `geo_cli.py audit-json <url> --out GEO-AUDIT.json`
3. Inspect the homepage, sitemap, schema, robots.txt, llms.txt, and top pages if available.
4. Evaluate the six categories:
   - AI Citability and Visibility: 25%
   - Brand Authority Signals: 20%
   - Content Quality and E-E-A-T: 20%
   - Technical Foundations: 15%
   - Structured Data: 10%
   - Platform Optimization: 10%
5. Write `GEO-AUDIT-REPORT.md` with:
   - executive summary
   - score breakdown
   - critical/high/medium/low issues
   - quick wins
   - 30-day action plan
   - ready-to-paste robots.txt, llms.txt, or JSON-LD snippets when relevant

If Codex subagent tools are available and the user explicitly asked for parallel
agents, split the analysis by category. Otherwise perform the audit inline.

## Report Standards

- Be concrete: cite URLs, observed tags, scores, crawler statuses, and missing schema types.
- Separate deterministic evidence from judgment calls.
- Do not claim live AI search rankings unless they were actually checked.
- Treat llms.txt as an emerging convention, not a guaranteed ranking factor.
- Keep generated client reports usable without extra editing.

## Data Storage

CRM/prospect workflows store local runtime data under `~/.geo-prospects/`:

```text
~/.geo-prospects/
+-- prospects.json
+-- audits/
+-- proposals/
+-- reports/
```
