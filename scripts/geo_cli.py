#!/usr/bin/env python3
"""
GEO-SEO Codex command wrapper.

This script exposes deterministic checks that the Codex skill can call directly,
while leaving higher-judgment strategy and client synthesis to the agent.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

VERSION = "0.3.2"
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
TIER_1_CRAWLERS = ["GPTBot", "ChatGPT-User", "ClaudeBot", "PerplexityBot"]

SCHEMA_TEMPLATES = {
    "organization": "organization.json",
    "local-business": "local-business.json",
    "article": "article-author.json",
    "software": "software-saas.json",
    "product": "product-ecommerce.json",
    "website": "website-searchaction.json",
}


def _load_fetchers():
    from fetch_page import fetch_page, fetch_robots_txt

    return fetch_page, fetch_robots_txt


def _load_citability():
    from citability_scorer import analyze_page_citability

    return analyze_page_citability


def _load_llmstxt():
    from llmstxt_generator import generate_llmstxt, validate_llmstxt

    return generate_llmstxt, validate_llmstxt


def _status_label(score: float) -> str:
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 60:
        return "Fair"
    if score >= 40:
        return "Poor"
    return "Critical"


def _base_url(url: str) -> str:
    parsed = urlparse(url if "://" in url else f"https://{url}")
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("URL must be an http(s) URL or a bare domain")
    return f"{parsed.scheme}://{parsed.netloc}"


def _domain(url: str) -> str:
    return urlparse(_base_url(url)).netloc


def _safe_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9.-]+", "-", value.strip().lower()).strip("-") or "site"


def _crawler_score(robots: dict[str, Any]) -> int:
    statuses = robots.get("ai_crawler_status", {})
    if not statuses:
        return 55 if robots.get("exists") else 70

    score = 100
    for crawler, status in statuses.items():
        penalty = 0
        if status in {"BLOCKED", "BLOCKED_BY_WILDCARD"}:
            penalty = 18 if crawler in TIER_1_CRAWLERS else 8
        elif status == "PARTIALLY_BLOCKED":
            penalty = 9 if crawler in TIER_1_CRAWLERS else 4
        score -= penalty
    return max(0, min(100, score))


def _llms_score(llms: dict[str, Any]) -> int:
    if not llms.get("exists"):
        return 0
    score = 20
    for key in ("has_title", "has_description", "has_sections", "has_links"):
        if llms.get(key):
            score += 20
    if llms.get("full_version", {}).get("exists"):
        score += 10
    return max(0, min(100, score))


def _schema_score(page: dict[str, Any]) -> int:
    structured_data = page.get("structured_data") or []
    if not structured_data:
        return 0
    score = min(85, 35 + len(structured_data) * 15)
    types = json.dumps(structured_data).lower()
    if "organization" in types or "localbusiness" in types:
        score += 10
    if "article" in types or "product" in types or "faqpage" in types:
        score += 5
    return max(0, min(100, score))


def _technical_score(page: dict[str, Any]) -> int:
    score = 100
    status = page.get("status_code")
    if not status or status >= 500:
        score -= 40
    elif status >= 400:
        score -= 25
    elif status >= 300:
        score -= 5

    if not page.get("has_ssr_content", True):
        score -= 30
    if not page.get("title"):
        score -= 8
    if not page.get("description"):
        score -= 8
    if not page.get("h1_tags"):
        score -= 8

    headers = page.get("security_headers") or {}
    missing_headers = sum(1 for value in headers.values() if not value)
    score -= min(12, missing_headers * 2)
    return max(0, min(100, score))


def _write_output(path: str | None, content: str) -> None:
    if path:
        Path(path).write_text(content, encoding="utf-8")
    print(content)


def _collect_snapshot(url: str) -> dict[str, Any]:
    normalized_url = _base_url(url)
    fetch_page, fetch_robots_txt = _load_fetchers()
    analyze_page_citability = _load_citability()
    _, validate_llmstxt = _load_llmstxt()

    page = fetch_page(normalized_url)
    robots = fetch_robots_txt(normalized_url)
    llms = validate_llmstxt(normalized_url)
    citability = analyze_page_citability(normalized_url)

    scores = {
        "AI Citability": float(citability.get("average_citability_score") or 0),
        "AI Crawler Access": float(_crawler_score(robots)),
        "llms.txt": float(_llms_score(llms)),
        "Structured Data": float(_schema_score(page)),
        "Technical Foundations": float(_technical_score(page)),
    }
    overall = round(
        scores["AI Citability"] * 0.30
        + scores["AI Crawler Access"] * 0.25
        + scores["llms.txt"] * 0.15
        + scores["Structured Data"] * 0.15
        + scores["Technical Foundations"] * 0.15,
        1,
    )

    blockers: list[str] = []
    if scores["AI Crawler Access"] < 70:
        blockers.append("Review robots.txt because one or more AI crawlers appear blocked.")
    if scores["llms.txt"] < 60:
        blockers.append("Add or improve /llms.txt so AI systems can discover priority pages.")
    if scores["Structured Data"] < 60:
        blockers.append("Add Organization, Article, Product, FAQ, or LocalBusiness schema where relevant.")
    if scores["AI Citability"] < 60:
        blockers.append("Rewrite key passages into direct, self-contained answer blocks.")
    if scores["Technical Foundations"] < 70:
        blockers.append("Fix indexability, SSR, metadata, heading, or security-header gaps.")

    return {
        "tool": "geo-seo-codex",
        "version": VERSION,
        "generated_at": date.today().isoformat(),
        "url": normalized_url,
        "domain": urlparse(normalized_url).netloc,
        "overall_score": overall,
        "rating": _status_label(overall),
        "scores": scores,
        "highest_impact_gaps": blockers,
        "signals": {
            "http_status": page.get("status_code"),
            "title": page.get("title"),
            "description": page.get("description"),
            "h1_count": len(page.get("h1_tags") or []),
            "structured_data_blocks": len(page.get("structured_data") or []),
            "robots_txt_exists": bool(robots.get("exists")),
            "llms_txt_exists": bool(llms.get("exists")),
            "citability_blocks_analyzed": citability.get("total_blocks_analyzed", 0),
        },
        "raw": {
            "page": page,
            "robots": robots,
            "llms": llms,
            "citability": citability,
        },
    }


def _quick_markdown(snapshot: dict[str, Any]) -> str:
    lines = [
        f"# GEO Quick Snapshot: {snapshot['url']}",
        "",
        f"Generated: {snapshot['generated_at']}",
        "",
        f"**Approximate GEO Score:** {snapshot['overall_score']}/100 ({snapshot['rating']})",
        "",
        "## Score Breakdown",
        "",
        "| Category | Score |",
        "|---|---:|",
    ]
    lines.extend(f"| {name} | {score:.1f}/100 |" for name, score in snapshot["scores"].items())
    lines.extend(["", "## Highest-Impact Gaps", ""])
    gaps = snapshot.get("highest_impact_gaps") or ["No critical gaps found in the deterministic quick scan."]
    lines.extend(f"- {item}" for item in gaps[:5])
    signals = snapshot["signals"]
    lines.extend(
        [
            "",
            "## Raw Signals",
            "",
            f"- HTTP status: {signals.get('http_status')}",
            f"- Title present: {'yes' if signals.get('title') else 'no'}",
            f"- Meta description present: {'yes' if signals.get('description') else 'no'}",
            f"- H1 count: {signals.get('h1_count')}",
            f"- Structured data blocks: {signals.get('structured_data_blocks')}",
            f"- robots.txt exists: {'yes' if signals.get('robots_txt_exists') else 'no'}",
            f"- llms.txt exists: {'yes' if signals.get('llms_txt_exists') else 'no'}",
            f"- Citability blocks analyzed: {signals.get('citability_blocks_analyzed')}",
        ]
    )
    return "\n".join(lines) + "\n"


def _audit_json(snapshot: dict[str, Any]) -> dict[str, Any]:
    scores = snapshot["scores"]
    return {
        "schema_version": "geo-audit/v1",
        "tool": "geo-seo-codex",
        "tool_version": VERSION,
        "generated_at": snapshot["generated_at"],
        "target": {"url": snapshot["url"], "domain": snapshot["domain"]},
        "overall": {"score": snapshot["overall_score"], "rating": snapshot["rating"]},
        "scores": {
            "ai_citability": scores["AI Citability"],
            "ai_crawler_access": scores["AI Crawler Access"],
            "llms_txt": scores["llms.txt"],
            "structured_data": scores["Structured Data"],
            "technical_foundations": scores["Technical Foundations"],
        },
        "signals": snapshot["signals"],
        "issues": [
            {"severity": "high" if index < 2 else "medium", "title": gap}
            for index, gap in enumerate(snapshot.get("highest_impact_gaps") or [])
        ],
        "recommended_actions": snapshot.get("highest_impact_gaps") or [],
        "artifacts": {
            "markdown_report": "GEO-AUDIT-REPORT.md",
            "json_report": "GEO-AUDIT.json",
        },
    }


def _audit_markdown(audit: dict[str, Any]) -> str:
    scores = audit["scores"]
    lines = [
        f"# GEO Audit Report: {audit['target']['url']}",
        "",
        f"Generated: {audit['generated_at']}",
        "",
        f"**Overall GEO Score:** {audit['overall']['score']}/100 ({audit['overall']['rating']})",
        "",
        "## Score Breakdown",
        "",
        "| Category | Score |",
        "|---|---:|",
        f"| AI Citability | {scores['ai_citability']:.1f}/100 |",
        f"| AI Crawler Access | {scores['ai_crawler_access']:.1f}/100 |",
        f"| llms.txt | {scores['llms_txt']:.1f}/100 |",
        f"| Structured Data | {scores['structured_data']:.1f}/100 |",
        f"| Technical Foundations | {scores['technical_foundations']:.1f}/100 |",
        "",
        "## Prioritized Issues",
        "",
    ]
    if audit["issues"]:
        lines.extend(f"- **{item['severity'].title()}**: {item['title']}" for item in audit["issues"])
    else:
        lines.append("- No critical deterministic issues found.")
    lines.extend(
        [
            "",
            "## 30-Day Action Plan",
            "",
            "### Week 1",
            "- Fix crawler access, indexability, and metadata gaps.",
            "- Add or improve llms.txt.",
            "",
            "### Week 2",
            "- Add Organization, WebSite, and page-specific Schema.org JSON-LD.",
            "- Rewrite the weakest content blocks into direct answer blocks.",
            "",
            "### Week 3",
            "- Add FAQ, comparison, and definition sections to priority pages.",
            "- Improve author, about, contact, and trust signals.",
            "",
            "### Week 4",
            "- Compare against competitors and prepare client-facing report artifacts.",
            "",
            "## Raw Signal Summary",
            "",
        ]
    )
    for key, value in audit["signals"].items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines) + "\n"


def _load_schema_template(schema_type: str) -> dict[str, Any]:
    if schema_type not in SCHEMA_TEMPLATES:
        raise ValueError(f"Unknown schema type: {schema_type}")
    path = PROJECT_DIR / "schema" / SCHEMA_TEMPLATES[schema_type]
    return json.loads(path.read_text(encoding="utf-8"))


def _replace_placeholders(value: Any, replacements: dict[str, Any]) -> Any:
    if isinstance(value, dict):
        return {key: _replace_placeholders(item, replacements) for key, item in value.items()}
    if isinstance(value, list):
        return [_replace_placeholders(item, replacements) for item in value]
    if isinstance(value, str):
        output = value
        for needle, replacement in replacements.items():
            output = output.replace(needle, str(replacement))
        return output
    return value


def _generate_schema(url: str, schema_type: str) -> dict[str, Any]:
    normalized_url = _base_url(url)
    fetch_page, _ = _load_fetchers()
    page = fetch_page(normalized_url)
    parsed = urlparse(normalized_url)
    domain = parsed.netloc
    title = page.get("title") or domain
    name = re.split(r"\s+[-|]\s+", title)[0].strip() or domain
    description = page.get("description") or f"Official website for {name}."
    template = _load_schema_template(schema_type)
    replacements = {
        "https://YOURDOMAIN.com": normalized_url,
        "YOURDOMAIN.com": domain,
        "YOUR_ORGANIZATION_NAME": name,
        "YOUR_ORGANIZATION_DESCRIPTION": description,
        "YOUR_BUSINESS_NAME": name,
        "YOUR_BUSINESS_DESCRIPTION": description,
        "YOUR_SOFTWARE_NAME": name,
        "YOUR_SOFTWARE_DESCRIPTION": description,
        "YOUR_PRODUCT_NAME": name,
        "YOUR_PRODUCT_DESCRIPTION": description,
        "contact@YOURDOMAIN.com": f"contact@{domain}",
        "YYYY-MM-DD": date.today().isoformat(),
        "YYYY-12-31": f"{date.today().year}-12-31",
    }
    return _replace_placeholders(template, replacements)


def _schema_markdown(schema_data: dict[str, Any], output_path: str) -> str:
    return "\n".join(
        [
            f"# Schema Generated: {schema_data.get('@type', 'Schema.org')}",
            "",
            f"Output: {output_path}",
            "",
            "```json",
            json.dumps(schema_data, indent=2, ensure_ascii=False),
            "```",
            "",
        ]
    )


def _suggest_rewrite(block: dict[str, Any]) -> str:
    heading = block.get("heading") or "This section"
    preview = (block.get("preview") or "").rstrip(".")
    score = block.get("total_score")
    return (
        f"{heading}: {preview}. In practical terms, this means [specific outcome]. "
        f"The most important facts are [fact 1], [fact 2], and [fact 3]. "
        f"For teams evaluating this topic, the recommended next step is [action]. "
        f"(Current block score: {score}/100; replace placeholders with site-specific evidence.)"
    )


def _dependency_status(module_name: str) -> str:
    return "ok" if importlib.util.find_spec(module_name) else "missing"


def command_quick(args: argparse.Namespace) -> int:
    snapshot = _collect_snapshot(args.url)
    if args.json:
        _write_output(args.out, json.dumps(snapshot, indent=2, default=str) + "\n")
        return 0
    _write_output(args.out, _quick_markdown(snapshot))
    return 0


def command_audit_json(args: argparse.Namespace) -> int:
    audit = _audit_json(_collect_snapshot(args.url))
    _write_output(args.out, json.dumps(audit, indent=2, default=str) + "\n")
    return 0


def command_audit(args: argparse.Namespace) -> int:
    audit = _audit_json(_collect_snapshot(args.url))
    json_path = args.json_out or "GEO-AUDIT.json"
    md_path = args.out or "GEO-AUDIT-REPORT.md"
    Path(json_path).write_text(json.dumps(audit, indent=2, default=str) + "\n", encoding="utf-8")
    markdown = _audit_markdown(audit)
    _write_output(md_path, markdown)
    return 0


def command_citability(args: argparse.Namespace) -> int:
    url = _base_url(args.url)
    analyze_page_citability = _load_citability()
    result = analyze_page_citability(url)
    if args.json:
        _write_output(args.out, json.dumps(result, indent=2, default=str) + "\n")
        return 0

    lines = [f"# GEO Citability Score: {url}", "", f"Generated: {date.today().isoformat()}", ""]
    if "error" in result:
        lines.append(f"Error: {result['error']}")
        _write_output(args.out, "\n".join(lines) + "\n")
        return 1

    average = result.get("average_citability_score", 0)
    lines.extend(
        [
            f"**Average Citability Score:** {average}/100 ({_status_label(float(average))})",
            f"**Blocks analyzed:** {result.get('total_blocks_analyzed', 0)}",
            f"**Optimal-length passages:** {result.get('optimal_length_passages', 0)}",
            "",
            "## Strongest Blocks",
            "",
        ]
    )
    for block in result.get("top_5_citable", [])[:5]:
        lines.append(f"- **{block.get('heading')}**: {block.get('total_score')}/100 - {block.get('preview')}")

    lines.extend(["", "## Weakest Blocks", ""])
    for block in result.get("bottom_5_citable", [])[:5]:
        lines.append(f"- **{block.get('heading')}**: {block.get('total_score')}/100 - {block.get('preview')}")

    lines.extend(
        [
            "",
            "## Rewrite Guidance",
            "",
            "- Start important sections with a direct answer sentence.",
            "- Keep citation-ready passages close to 134-167 words.",
            "- Include specific facts, named entities, dates, numbers, and sources.",
            "- Reduce pronouns so each passage stands alone outside the page context.",
        ]
    )
    _write_output(args.out, "\n".join(lines) + "\n")
    return 0


def command_rewrite(args: argparse.Namespace) -> int:
    url = _base_url(args.url)
    analyze_page_citability = _load_citability()
    result = analyze_page_citability(url)
    if "error" in result:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        return 1
    weak_blocks = result.get("bottom_5_citable", [])[: args.limit]
    lines = [
        f"# GEO Rewrite Suggestions: {url}",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "These are deterministic rewrite starters. Replace bracketed placeholders with verified site-specific facts before publishing.",
        "",
    ]
    if not weak_blocks:
        lines.append("No eligible content blocks were found for rewrite suggestions.")
    for index, block in enumerate(weak_blocks, start=1):
        lines.extend(
            [
                f"## Suggestion {index}: {block.get('heading')}",
                "",
                f"Current score: {block.get('total_score')}/100",
                "",
                _suggest_rewrite(block),
                "",
            ]
        )
    _write_output(args.out, "\n".join(lines) + "\n")
    return 0


def command_crawlers(args: argparse.Namespace) -> int:
    url = _base_url(args.url)
    _, fetch_robots_txt = _load_fetchers()
    result = fetch_robots_txt(url)
    if args.json:
        _write_output(args.out, json.dumps(result, indent=2, default=str) + "\n")
        return 0

    score = _crawler_score(result)
    lines = [
        f"# GEO Crawler Access: {url}",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        f"**AI Crawler Access Score:** {score}/100 ({_status_label(score)})",
        f"**robots.txt:** {result.get('url')}",
        f"**Exists:** {'yes' if result.get('exists') else 'no'}",
        "",
        "## AI Crawler Status",
        "",
        "| Crawler | Status |",
        "|---|---|",
    ]
    for crawler, status in sorted((result.get("ai_crawler_status") or {}).items()):
        lines.append(f"| {crawler} | {status} |")
    if result.get("errors"):
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in result["errors"])
    lines.extend(
        [
            "",
            "## Recommended Tier-1 Allow Block",
            "",
            "```txt",
            "User-agent: GPTBot",
            "Allow: /",
            "",
            "User-agent: ChatGPT-User",
            "Allow: /",
            "",
            "User-agent: ClaudeBot",
            "Allow: /",
            "",
            "User-agent: PerplexityBot",
            "Allow: /",
            "```",
        ]
    )
    _write_output(args.out, "\n".join(lines) + "\n")
    return 0


def command_llmstxt(args: argparse.Namespace) -> int:
    url = _base_url(args.url)
    generate_llmstxt, validate_llmstxt = _load_llmstxt()
    result = generate_llmstxt(url) if args.generate else validate_llmstxt(url)
    if args.json:
        _write_output(args.out, json.dumps(result, indent=2, default=str) + "\n")
        return 0
    if args.generate:
        content = result.get("generated_llmstxt", "")
        output_path = args.out or "llms.txt"
        Path(output_path).write_text(content, encoding="utf-8")
        summary = [
            f"# llms.txt Generation: {url}",
            "",
            f"Generated: {date.today().isoformat()}",
            "",
            f"Output: {output_path}",
            f"Pages analyzed: {result.get('pages_analyzed', 0)}",
            "",
            "## Section Counts",
            "",
        ]
        for section, count in (result.get("sections") or {}).items():
            summary.append(f"- {section}: {count}")
        summary.extend(["", "## Generated llms.txt", "", "```txt", content, "```"])
        print("\n".join(summary) + "\n")
        return 0

    score = _llms_score(result)
    lines = [
        f"# llms.txt Analysis: {url}",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        f"**llms.txt Score:** {score}/100 ({_status_label(score)})",
        f"**File:** {result.get('url')}",
        f"**Exists:** {'yes' if result.get('exists') else 'no'}",
        "",
        "## Format Checks",
        "",
        f"- Title: {'yes' if result.get('has_title') else 'no'}",
        f"- Description: {'yes' if result.get('has_description') else 'no'}",
        f"- Sections: {result.get('section_count', 0)}",
        f"- Links: {result.get('link_count', 0)}",
        f"- llms-full.txt exists: {'yes' if result.get('full_version', {}).get('exists') else 'no'}",
    ]
    if result.get("issues"):
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in result["issues"])
    _write_output(args.out, "\n".join(lines) + "\n")
    return 0


def command_schema(args: argparse.Namespace) -> int:
    url = _base_url(args.url)
    fetch_page, _ = _load_fetchers()
    page = fetch_page(url)
    if not args.generate:
        result = {
            "url": url,
            "structured_data_blocks": len(page.get("structured_data") or []),
            "score": _schema_score(page),
            "detected": page.get("structured_data") or [],
            "recommended_types": list(SCHEMA_TEMPLATES.keys()),
        }
        _write_output(args.out, json.dumps(result, indent=2, default=str) + "\n")
        return 0

    schema_data = _generate_schema(url, args.generate)
    output_path = args.out or f"schema-{args.generate}.jsonld"
    Path(output_path).write_text(json.dumps(schema_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(_schema_markdown(schema_data, output_path))
    return 0


def command_compare_domain(args: argparse.Namespace) -> int:
    snapshots = [_collect_snapshot(args.url), _collect_snapshot(args.competitor_url)]
    if args.json:
        _write_output(args.out, json.dumps({"schema_version": "geo-compare/v1", "sites": snapshots}, indent=2, default=str) + "\n")
        return 0
    lines = [
        f"# GEO Domain Comparison: {snapshots[0]['domain']} vs {snapshots[1]['domain']}",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "| Metric | Primary | Competitor | Delta |",
        "|---|---:|---:|---:|",
        f"| Overall GEO Score | {snapshots[0]['overall_score']:.1f} | {snapshots[1]['overall_score']:.1f} | {snapshots[0]['overall_score'] - snapshots[1]['overall_score']:.1f} |",
    ]
    for key in snapshots[0]["scores"]:
        left = snapshots[0]["scores"][key]
        right = snapshots[1]["scores"][key]
        lines.append(f"| {key} | {left:.1f} | {right:.1f} | {left - right:.1f} |")
    lines.extend(["", "## Priority Gap", ""])
    if snapshots[0]["overall_score"] >= snapshots[1]["overall_score"]:
        lines.append("- Primary domain is ahead overall. Focus on the lowest category score to widen the gap.")
    else:
        lines.append("- Competitor is ahead overall. Prioritize the categories with the largest negative deltas.")
    _write_output(args.out, "\n".join(lines) + "\n")
    return 0


def command_fetch(args: argparse.Namespace) -> int:
    url = _base_url(args.url)
    fetch_page, _ = _load_fetchers()
    data = fetch_page(url)
    _write_output(args.out, json.dumps(data, indent=2, default=str) + "\n")
    return 0


def command_doctor(args: argparse.Namespace) -> int:
    checks = []
    checks.append(("python_version", sys.version.split()[0], sys.version_info >= (3, 8)))
    checks.append(("skill_file", str(PROJECT_DIR / "SKILL.md"), (PROJECT_DIR / "SKILL.md").exists()))
    checks.append(("scripts_dir", str(SCRIPT_DIR), SCRIPT_DIR.exists()))
    checks.append(("schema_dir", str(PROJECT_DIR / "schema"), (PROJECT_DIR / "schema").exists()))
    checks.append(("references_dir", str(PROJECT_DIR / "references"), (PROJECT_DIR / "references").exists()))
    checks.append(("cwd_writable", str(Path.cwd()), _can_write(Path.cwd())))
    for module in ["requests", "bs4", "lxml", "PIL", "reportlab", "flask", "rich", "validators"]:
        checks.append((f"dependency:{module}", _dependency_status(module), _dependency_status(module) == "ok"))
    ok = all(item[2] for item in checks)
    result = {"ok": ok, "checks": [{"name": name, "detail": detail, "ok": passed} for name, detail, passed in checks]}
    if args.json:
        _write_output(args.out, json.dumps(result, indent=2) + "\n")
    else:
        lines = ["# GEO-SEO Codex Doctor", "", f"Overall: {'ok' if ok else 'needs attention'}", ""]
        for item in result["checks"]:
            lines.append(f"- [{'OK' if item['ok'] else 'FAIL'}] {item['name']}: {item['detail']}")
        _write_output(args.out, "\n".join(lines) + "\n")
    return 0 if ok else 1


def _can_write(path: Path) -> bool:
    try:
        with tempfile.NamedTemporaryFile(dir=path, delete=True):
            return True
    except OSError:
        return False


def command_self_test(args: argparse.Namespace) -> int:
    failures: list[str] = []
    doctor_args = argparse.Namespace(json=True, out=None)
    if command_doctor(doctor_args) != 0:
        failures.append("doctor")
    try:
        snapshot = _collect_snapshot(args.url)
        if "overall_score" not in snapshot:
            failures.append("quick")
    except Exception as exc:
        failures.append(f"quick: {exc}")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = str(Path(temp_dir) / "llms.txt")
            llms_args = argparse.Namespace(url=args.url, generate=True, json=False, out=output_path)
            if command_llmstxt(llms_args) != 0 or not Path(output_path).exists():
                failures.append("llmstxt_generate")
    except Exception as exc:
        failures.append(f"llmstxt_generate: {exc}")
    if failures:
        print("SELF_TEST_FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("SELF_TEST_OK")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GEO-SEO Codex command wrapper")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Check local installation health")
    doctor.add_argument("--out", default=None)
    doctor.add_argument("--json", action="store_true")
    doctor.set_defaults(func=command_doctor)

    self_test = subparsers.add_parser("self-test", help="Run installation smoke tests")
    self_test.add_argument("--url", default="https://example.com")
    self_test.set_defaults(func=command_self_test)

    quick = subparsers.add_parser("quick", help="Run a deterministic GEO snapshot")
    quick.add_argument("url")
    quick.add_argument("--out", default=None)
    quick.add_argument("--json", action="store_true")
    quick.set_defaults(func=command_quick)

    audit = subparsers.add_parser("audit", help="Write deterministic audit markdown and JSON")
    audit.add_argument("url")
    audit.add_argument("--out", default="GEO-AUDIT-REPORT.md")
    audit.add_argument("--json-out", default="GEO-AUDIT.json")
    audit.set_defaults(func=command_audit)

    audit_json = subparsers.add_parser("audit-json", help="Write standardized audit JSON")
    audit_json.add_argument("url")
    audit_json.add_argument("--out", default="GEO-AUDIT.json")
    audit_json.set_defaults(func=command_audit_json)

    citability = subparsers.add_parser("citability", help="Score page citability")
    citability.add_argument("url")
    citability.add_argument("--out", default="GEO-CITABILITY-SCORE.md")
    citability.add_argument("--json", action="store_true")
    citability.set_defaults(func=command_citability)

    rewrite = subparsers.add_parser("rewrite", help="Generate citation-ready rewrite starters")
    rewrite.add_argument("url")
    rewrite.add_argument("--out", default="GEO-REWRITE-SUGGESTIONS.md")
    rewrite.add_argument("--limit", type=int, default=5)
    rewrite.set_defaults(func=command_rewrite)

    crawlers = subparsers.add_parser("crawlers", help="Analyze AI crawler access")
    crawlers.add_argument("url")
    crawlers.add_argument("--out", default="GEO-CRAWLER-ACCESS.md")
    crawlers.add_argument("--json", action="store_true")
    crawlers.set_defaults(func=command_crawlers)

    llms = subparsers.add_parser("llmstxt", help="Analyze or generate llms.txt")
    llms.add_argument("url")
    llms.add_argument("--generate", action="store_true")
    llms.add_argument("--out", default=None)
    llms.add_argument("--json", action="store_true")
    llms.set_defaults(func=command_llmstxt)

    schema = subparsers.add_parser("schema", help="Analyze or generate Schema.org JSON-LD")
    schema.add_argument("url")
    schema.add_argument("--generate", choices=sorted(SCHEMA_TEMPLATES), default=None)
    schema.add_argument("--out", default=None)
    schema.set_defaults(func=command_schema)

    compare = subparsers.add_parser("compare-domain", help="Compare two domains")
    compare.add_argument("url")
    compare.add_argument("competitor_url")
    compare.add_argument("--out", default="GEO-DOMAIN-COMPARISON.md")
    compare.add_argument("--json", action="store_true")
    compare.set_defaults(func=command_compare_domain)

    fetch = subparsers.add_parser("fetch", help="Fetch raw page analysis JSON")
    fetch.add_argument("url")
    fetch.add_argument("--out", default=None)
    fetch.set_defaults(func=command_fetch)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
