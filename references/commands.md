# GEO Command Reference for Codex

Load only the section needed for the active `$geo` command.

## quick

Run:

```bash
python scripts/geo_cli.py quick <url>
```

Return the score, top gaps, and next recommended command. Do not write files unless
the user asks.

## citability

Run:

```bash
python scripts/geo_cli.py citability <url> --out GEO-CITABILITY-SCORE.md
```

Explain the average citability score, strongest blocks, weakest blocks, and rewrite
patterns. Recommend passages of 134-167 words, direct answer openings, specific
facts, and low pronoun dependency.

## crawlers

Run:

```bash
python scripts/geo_cli.py crawlers <url> --out GEO-CRAWLER-ACCESS.md
```

Focus on GPTBot, ChatGPT-User, ClaudeBot, and PerplexityBot first. Call out wildcard
blocks and domain-level restrictions. Provide a ready-to-paste robots.txt patch.

## llmstxt

Analyze:

```bash
python scripts/geo_cli.py llmstxt <url>
```

Generate:

```bash
python scripts/geo_cli.py llmstxt <url> --generate --out llms.txt
```

Validate title, description, sections, absolute URLs, descriptions, key facts, and
contact information. Generated files should prioritize homepage, products/services,
resources, company, support, and contact pages.

## audit

Run the deterministic helpers first:

```bash
python scripts/geo_cli.py quick <url> --out GEO-QUICK-SNAPSHOT.md
python scripts/geo_cli.py fetch <url> --out audit-data.json
python scripts/geo_cli.py crawlers <url> --json --out crawler-data.json
python scripts/geo_cli.py citability <url> --json --out citability-data.json
```

Then synthesize `GEO-AUDIT-REPORT.md` with:

- Executive summary and overall GEO Score.
- Six-category score table using `references/scoring.md`.
- Evidence-backed findings by severity.
- Quick wins that can be done in 48 hours.
- 30-day action plan grouped by week.
- Technical appendix with robots.txt, llms.txt, and JSON-LD recommendations.

## schema

Use `fetch_page.py` or `geo_cli.py fetch` because markdown fetching may strip
JSON-LD from `<head>`. Detect existing Schema.org types, validation issues, and
missing opportunities:

- Organization for all brands.
- LocalBusiness for local service businesses.
- Article and Person for editorial content.
- Product and Offer for ecommerce.
- SoftwareApplication for SaaS.
- WebSite with SearchAction for sites with internal search.
- FAQPage or HowTo where the visible content supports it.

Use templates from `schema/` and customize factual fields from the target site.

## technical

Check raw HTML accessibility for AI crawlers, not only browser-rendered output.
Prioritize:

- indexability and robots directives
- server-side rendered main content
- HTTP status, canonical, redirects
- title, meta description, H1
- mobile viewport
- security headers
- sitemap and internal link discoverability
- image alt text for important images

## content

Assess E-E-A-T and AI-citation readiness:

- clear authorship and credentials
- about/contact/trust pages
- original data, examples, methods, and sources
- freshness and date clarity
- concise answer blocks under descriptive headings
- comparison, FAQ, definition, and how-to sections

## platforms

Score readiness separately for Google AI Overviews, ChatGPT, Perplexity, Gemini,
and Bing Copilot. Distinguish:

- retrievability: can the platform crawl or index the page?
- citability: are passages extractable and self-contained?
- authority: does the brand/entity appear on trusted third-party sources?
- schema: can machines identify entity type, author, product, and facts?

## brands

Use `brand_scanner.py` when useful:

```bash
python scripts/brand_scanner.py "<brand>" <domain>
```

Assess entity consistency across Wikipedia, Reddit, YouTube, LinkedIn, GitHub,
Crunchbase-like profiles, review platforms, and industry directories where relevant.

## report

Create a polished Markdown deliverable from an audit. The report should be ready
for a client and avoid internal agent notes. Use concrete scores, findings, and
actions. Include technical appendices only after the executive narrative.

## report-pdf

Create or reuse a JSON audit data file and run:

```bash
python scripts/generate_pdf_report.py audit-data.json GEO-REPORT.pdf
```

If no audit data exists, run `$geo audit <url>` or build the JSON from available
findings before generating the PDF.

## prospect

Store data in `~/.geo-prospects/prospects.json`. Supported subcommands:

- `new <domain>`
- `list [status]`
- `show <id-or-domain>`
- `audit <id-or-domain>`
- `note <id-or-domain> "<text>"`
- `status <id-or-domain> <lead|qualified|proposal|won|lost>`
- `pipeline`

Keep CRM updates local and timestamped.

## proposal

Use existing audit data when available. If absent, run `$geo quick <domain>` first.
Write proposals to `~/.geo-prospects/proposals/<domain>-proposal-<date>.md`.

## compare

Compare baseline and current audit files for the same domain. Write monthly delta
reports to `~/.geo-prospects/reports/<domain>-monthly-YYYY-MM.md`.
