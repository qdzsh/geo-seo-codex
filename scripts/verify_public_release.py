from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request


DEFAULT_REPO = "quangdo126/geo-seo-codex"


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


def check(repo: str, tag: str, branch: str) -> int:
    endpoints = {
        "repo_api": f"https://api.github.com/repos/{repo}",
        "raw_bootstrap_ps1": f"https://raw.githubusercontent.com/{repo}/{branch}/bootstrap.ps1",
        "raw_bootstrap_sh": f"https://raw.githubusercontent.com/{repo}/{branch}/bootstrap.sh",
        "release_zip": f"https://github.com/{repo}/releases/download/{tag}/geo-seo-codex.zip",
        "release_checksum": f"https://github.com/{repo}/releases/download/{tag}/geo-seo-codex.zip.sha256",
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
    parser.add_argument("--repo", default=DEFAULT_REPO, help="GitHub repository in owner/name form.")
    parser.add_argument("--tag", default="v0.3.0", help="Release tag to verify.")
    parser.add_argument("--branch", default="main", help="Branch used by raw bootstrap URLs.")
    args = parser.parse_args()

    return check(args.repo, args.tag, args.branch)


if __name__ == "__main__":
    raise SystemExit(main())
