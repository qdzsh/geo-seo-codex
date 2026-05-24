# GEO Scoring Reference

Use this weighting model for full audits and client reports.

| Category | Weight | Evidence |
|---|---:|---|
| AI Citability and Visibility | 25% | answer blocks, passage self-containment, crawler access, llms.txt |
| Brand Authority Signals | 20% | mentions on trusted third-party platforms, entity consistency |
| Content Quality and E-E-A-T | 20% | authorship, credentials, citations, original data, freshness |
| Technical Foundations | 15% | SSR, status codes, metadata, sitemap, mobile, security headers |
| Structured Data | 10% | Schema.org coverage, JSON-LD validity, rich result eligibility |
| Platform Optimization | 10% | Google AIO, ChatGPT, Perplexity, Gemini, Copilot readiness |

Formula:

```text
GEO Score =
  Citability * 0.25 +
  Brand Authority * 0.20 +
  Content E-E-A-T * 0.20 +
  Technical * 0.15 +
  Structured Data * 0.10 +
  Platform Optimization * 0.10
```

Score labels:

| Range | Label | Meaning |
|---|---|---|
| 90-100 | Excellent | Strong AI visibility foundation |
| 75-89 | Good | Solid foundation with targeted gaps |
| 60-74 | Fair | Visible but material improvements remain |
| 40-59 | Poor | Weak GEO signals and likely missed citations |
| 0-39 | Critical | AI systems may struggle to crawl, understand, or cite the site |

Severity:

- Critical: domain noindex, 5xx on key pages, all major AI crawlers blocked, no crawlable main content, no structured data on a machine-critical site.
- High: GPTBot/ClaudeBot/PerplexityBot blocked, no llms.txt, missing Organization/LocalBusiness schema, no author attribution, zero answer blocks.
- Medium: malformed llms.txt, partial crawler blocks, thin author bios, weak FAQ/comparison content, average citability below 60.
- Low: minor schema warnings, missing optional social profiles, metadata polish, alt text gaps on non-critical images.
