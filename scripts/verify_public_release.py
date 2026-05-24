from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "https://qdzsh.dev/geo-seo-codex"


def probe(url: str) -> tuple[int, int]:
    request = urllib.request.Request(url, headers={"User-Agent": "geo-seo-codex-public-release-check"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read()
            return response.status, len(body)
    except urllib.error.HTTPError as exc:
        return exc.code, len(exc.read())
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{url}: {exc}") from exc


def check(base_url: str) -> int:
    base_url = base_url.rstrip("/")
    endpoints = {
        "bootstrap_ps1": f"{base_url}/bootstrap.ps1",
        "bootstrap_sh": f"{base_url}/bootstrap.sh",
        "release_zip": f"{base_url}/latest/geo-seo-codex.zip",
        "release_checksum": f"{base_url}/latest/geo-seo-codex.zip.sha256",
    }

    failures = []
    for name, url in endpoints.items():
        status, size = probe(url)
        ok = status == 200 and size > 0
        marker = "OK" if ok else "FAIL"
        print(f"[{marker}] {name}: status={status} bytes={size} url={url}")
        if not ok:
            failures.append(name)

    if failures:
        print("\nPublic release verification failed:", ", ".join(failures), file=sys.stderr)
        return 1

    print("\nPublic release verification passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify anonymous public access to release install assets.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Public base URL for installer assets.")
    parser.add_argument("--tag", help="Deprecated; accepted for compatibility and ignored.")
    args = parser.parse_args()

    return check(args.base_url)


if __name__ == "__main__":
    raise SystemExit(main())
