#!/usr/bin/env bash
set -euo pipefail

REPO="https://github.com/quangdo126/geo-seo-codex.git"
TEMP_DIR="$(mktemp -d)"

cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

git clone --depth 1 "$REPO" "$TEMP_DIR"
cd "$TEMP_DIR"
./install.sh
