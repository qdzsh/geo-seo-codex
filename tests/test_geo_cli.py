from __future__ import annotations

import argparse
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import geo_cli


def fake_page(url: str) -> dict:
    return {
        "url": url,
        "status_code": 200,
        "title": "Example Brand - Home",
        "description": "Example Brand helps teams improve AI search visibility.",
        "h1_tags": ["Example Brand"],
        "structured_data": [{"@type": "Organization"}],
        "security_headers": {
            "Strict-Transport-Security": "max-age=31536000",
            "Content-Security-Policy": "default-src 'self'",
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=()",
        },
        "has_ssr_content": True,
    }


def fake_robots(_url: str) -> dict:
    return {
        "exists": True,
        "url": "https://example.com/robots.txt",
        "ai_crawler_status": {
            "GPTBot": "ALLOWED",
            "ChatGPT-User": "ALLOWED",
            "ClaudeBot": "ALLOWED",
            "PerplexityBot": "ALLOWED",
        },
        "errors": [],
    }


def fake_llms(_url: str) -> dict:
    return {
        "exists": True,
        "url": "https://example.com/llms.txt",
        "has_title": True,
        "has_description": True,
        "has_sections": True,
        "has_links": True,
        "section_count": 3,
        "link_count": 8,
        "full_version": {"exists": True},
        "issues": [],
    }


def fake_generate_llms(_url: str) -> dict:
    return {
        "generated_llmstxt": "# Example Brand\n> AI search visibility platform\n",
        "pages_analyzed": 1,
        "sections": {"Main Pages": 1},
    }


def fake_citability(_url: str) -> dict:
    weak_block = {
        "heading": "Overview",
        "total_score": 42,
        "word_count": 80,
        "preview": "Example Brand improves visibility in AI-powered answers",
    }
    return {
        "total_blocks_analyzed": 2,
        "average_citability_score": 72.5,
        "optimal_length_passages": 1,
        "top_5_citable": [
            {
                "heading": "Definition",
                "total_score": 88,
                "word_count": 145,
                "preview": "GEO is the practice of improving AI answer visibility",
            }
        ],
        "bottom_5_citable": [weak_block],
        "all_blocks": [weak_block],
    }


class GeoCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fetch_patch = patch.object(geo_cli, "_load_fetchers", return_value=(fake_page, fake_robots))
        self.llms_patch = patch.object(geo_cli, "_load_llmstxt", return_value=(fake_generate_llms, fake_llms))
        self.cite_patch = patch.object(geo_cli, "_load_citability", return_value=fake_citability)
        self.fetch_patch.start()
        self.llms_patch.start()
        self.cite_patch.start()

    def tearDown(self) -> None:
        patch.stopall()

    def run_quietly(self, func, *args):
        with contextlib.redirect_stdout(io.StringIO()):
            return func(*args)

    def test_quick_json_snapshot(self) -> None:
        snapshot = geo_cli._collect_snapshot("example.com")

        self.assertEqual(snapshot["url"], "https://example.com")
        self.assertGreater(snapshot["overall_score"], 70)
        self.assertEqual(snapshot["signals"]["structured_data_blocks"], 1)
        self.assertTrue(snapshot["signals"]["llms_txt_exists"])

    def test_audit_json_shape(self) -> None:
        audit = geo_cli._audit_json(geo_cli._collect_snapshot("https://example.com"))

        self.assertEqual(audit["schema_version"], "geo-audit/v1")
        self.assertEqual(audit["target"]["domain"], "example.com")
        self.assertIn("ai_citability", audit["scores"])
        self.assertIn("json_report", audit["artifacts"])

    def test_schema_generation_writes_jsonld(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir) / "schema-organization.jsonld"
            args = argparse.Namespace(url="https://example.com", generate="organization", out=str(out))

            code = self.run_quietly(geo_cli.command_schema, args)

            self.assertEqual(code, 0)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["@type"], "Organization")
            self.assertEqual(data["url"], "https://example.com")

    def test_llmstxt_generation_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir) / "llms.txt"
            args = argparse.Namespace(url="example.com", generate=True, json=False, out=str(out))

            code = self.run_quietly(geo_cli.command_llmstxt, args)

            self.assertEqual(code, 0)
            self.assertTrue(out.exists())
            self.assertIn("Example Brand", out.read_text(encoding="utf-8"))

    def test_compare_domain_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir) / "compare.json"
            args = argparse.Namespace(url="example.com", competitor_url="competitor.com", json=True, out=str(out))

            code = self.run_quietly(geo_cli.command_compare_domain, args)

            self.assertEqual(code, 0)
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], "geo-compare/v1")
            self.assertEqual(len(payload["sites"]), 2)


if __name__ == "__main__":
    unittest.main()
