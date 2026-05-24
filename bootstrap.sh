#!/usr/bin/env bash
set -euo pipefail

BASE_URI="https://github.com/quangdo126/geo-seo-codex/releases/latest/download"
TEMP_DIR="$(mktemp -d)"
ZIP_PATH="$TEMP_DIR/geo-seo-codex.zip"
CHECKSUM_PATH="$TEMP_DIR/geo-seo-codex.zip.sha256"
EXTRACT_DIR="$TEMP_DIR/extract"

cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

mkdir -p "$EXTRACT_DIR"
curl -fsSL "$BASE_URI/geo-seo-codex.zip" -o "$ZIP_PATH"
curl -fsSL "$BASE_URI/geo-seo-codex.zip.sha256" -o "$CHECKSUM_PATH"

EXPECTED="$(awk '{print tolower($1)}' "$CHECKSUM_PATH")"
if command -v sha256sum >/dev/null 2>&1; then
    printf '%s  %s\n' "$EXPECTED" "$ZIP_PATH" | sha256sum -c -
else
    ACTUAL="$(shasum -a 256 "$ZIP_PATH" | awk '{print tolower($1)}')"
    if [ "$EXPECTED" != "$ACTUAL" ]; then
        echo "Checksum mismatch for geo-seo-codex.zip. Expected $EXPECTED but got $ACTUAL." >&2
        exit 1
    fi
fi

unzip -q "$ZIP_PATH" -d "$EXTRACT_DIR"
SKILL_FILE="$(find "$EXTRACT_DIR" -name SKILL.md -print -quit)"
if [ -z "$SKILL_FILE" ]; then
    echo "Downloaded archive does not contain SKILL.md." >&2
    exit 1
fi

cd "$(dirname "$SKILL_FILE")"
./install.sh
