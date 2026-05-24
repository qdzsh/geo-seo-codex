#!/usr/bin/env python3
"""
Codex-friendly GEO command wrapper.

This script exposes deterministic GEO checks that the Codex skill can call
directly, while leaving the higher-judgment audit synthesis to the agent.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

TIER_1_CRAWLERS = ["GPTBot", "ChatGPT-User", "ClaudeBot", "PerplexityBot"]


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


def _crawler_score(robots: dict) -> int:
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


def _llms_score(llms: dict) -> int:
    if not llms.get("exists"):
        return 0
    score = 20
    for key in ("has_title", "has_description", "has_sections", "has_links"):
        if llms.get(key):
            score += 20
    if llms.get("full_version", {}).get("exists"):
        score += 10
    return max(0, min(100, score))


def _schema_score(page: dict) -> int:
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


def _technical_score(page: dict) -> int:
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


def command_quick(args: argparse.Namespace) -> int:
    url = _base_url(args.url)
    fetch_page, fetch_robots_txt = _load_fetchers()
    analyze_page_citability = _load_citability()
    _, validate_llmstxt = _load_llmstxt()

    page = fetch_page(url)
    robots = fetch_robots_txt(url)
    llms = validate_llmstxt(url)
    citability = analyze_page_citability(url)

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

    lines = [
        f"# GEO Quick Snapshot: {url}",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        f"**Approximate GEO Score:** {overall}/100 ({_status_label(overall)})",
        "",
        "## Score Breakdown",
        "",
        "| Category | Score |",
        "|---|---:|",
    ]
    lines.extend(f"| {name} | {score:.1f}/100 |" for name, score in scores.items())
    lines.extend(
        [
            "",
            "## Highest-Impact Gaps",
            "",
        ]
    )
    if blockers:
        lines.extend(f"- {item}" for item in blockers[:5])
    else:
        lines.append("- No critical gaps found in the deterministic quick scan.")

    lines.extend(
        [
            "",
            "## Raw Signals",
            "",
            f"- HTTP status: {page.get('status_code')}",
            f"- Title present: {'yes' if page.get('title') else 'no'}",
            f"- Meta description present: {'yes' if page.get('description') else 'no'}",
            f"- H1 count: {len(page.get('h1_tags') or [])}",
            f"- Structured data blocks: {len(page.get('structured_data') or [])}",
            f"- robots.txt exists: {'yes' if robots.get('exists') else 'no'}",
            f"- llms.txt exists: {'yes' if llms.get('exists') else 'no'}",
            f"- Citability blocks analyzed: {citability.get('total_blocks_analyzed', 0)}",
        ]
    )

    _write_output(args.out, "\n".join(lines) + "\n")
    return 0


def command_citability(args: argparse.Namespace) -> int:
    url = _base_url(args.url)
    analyze_page_citability = _load_citability()
    result = analyze_page_citability(url)
    if args.json:
        _write_output(args.out, json.dumps(result, indent=2, default=str) + "\n")
        return 0

    lines = [
        f"# GEO Citability Score: {url}",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
    ]
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


def command_fetch(args: argparse.Namespace) -> int:
    url = _base_url(args.url)
    fetch_page, _ = _load_fetchers()
    data = fetch_page(url)
    _write_output(args.out, json.dumps(data, indent=2, default=str) + "\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GEO-SEO Codex command wrapper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    quick = subparsers.add_parser("quick", help="Run a deterministic GEO snapshot")
    quick.add_argument("url")
    quick.add_argument("--out", default=None)
    quick.set_defaults(func=command_quick)

    citability = subparsers.add_parser("citability", help="Score page citability")
    citability.add_argument("url")
    citability.add_argument("--out", default="GEO-CITABILITY-SCORE.md")
    citability.add_argument("--json", action="store_true")
    citability.set_defaults(func=command_citability)

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
