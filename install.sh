#!/usr/bin/env bash
set -euo pipefail

CODEX_DIR="${HOME}/.codex"
SKILLS_DIR="${CODEX_DIR}/skills"
INSTALL_DIR="${SKILLS_DIR}/geo"
VENV_DIR="${INSTALL_DIR}/.venv"

info() { printf '\033[0;34m-> %s\033[0m\n' "$1"; }
ok() { printf '\033[0;32m[OK] %s\033[0m\n' "$1"; }
warn() { printf '\033[1;33m[WARN] %s\033[0m\n' "$1"; }

find_python() {
    for cmd in python3 python; do
        if command -v "$cmd" >/dev/null 2>&1; then
            version="$("$cmd" - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
PY
)"
            major="${version%%.*}"
            minor="${version##*.}"
            if [ "$major" -gt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -ge 8 ]; }; then
                printf '%s\n' "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

printf '\n\033[0;34mGEO-SEO Codex Skill Installer\033[0m\n\n'

PYTHON_CMD="$(find_python)" || {
    echo "Python 3.8+ is required but was not found on PATH." >&2
    exit 1
}
ok "Python found: $($PYTHON_CMD --version)"

if command -v codex >/dev/null 2>&1; then
    ok "Codex CLI found"
else
    warn "Codex CLI was not found on PATH. Files will still be installed."
fi

SCRIPT_DIR=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ "${BASH_SOURCE[0]}" != "bash" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

if [ -z "$SCRIPT_DIR" ] || [ ! -f "$SCRIPT_DIR/SKILL.md" ]; then
    echo "Run this installer from the GEO-SEO Codex project directory." >&2
    exit 1
fi
SOURCE_DIR="$SCRIPT_DIR"

mkdir -p "$INSTALL_DIR"
find "$INSTALL_DIR" -mindepth 1 -maxdepth 1 -exec rm -rf {} +

info "Copying Codex skill files"
cp "$SOURCE_DIR/SKILL.md" "$INSTALL_DIR/SKILL.md"
cp -R "$SOURCE_DIR/references" "$INSTALL_DIR/references"
cp -R "$SOURCE_DIR/agents" "$INSTALL_DIR/agents"
if [ -d "$SOURCE_DIR/assets" ]; then
    cp -R "$SOURCE_DIR/assets" "$INSTALL_DIR/assets"
fi

info "Copying scripts and schema templates"
cp -R "$SOURCE_DIR/scripts" "$INSTALL_DIR/scripts"
cp -R "$SOURCE_DIR/schema" "$INSTALL_DIR/schema"
cp "$SOURCE_DIR/requirements.txt" "$INSTALL_DIR/requirements.txt"

info "Creating isolated Python environment"
rm -rf "$VENV_DIR"
"$PYTHON_CMD" -m venv "$VENV_DIR"
VENV_PY="${VENV_DIR}/bin/python"

info "Installing Python dependencies"
"$VENV_PY" -m pip install --upgrade pip --quiet
"$VENV_PY" -m pip install -r "$INSTALL_DIR/requirements.txt" --quiet

info "Verifying installation"
test -f "$INSTALL_DIR/SKILL.md"
test -f "$INSTALL_DIR/scripts/geo_cli.py"
test -f "$INSTALL_DIR/schema/organization.json"
test -x "$VENV_PY"

ok "Installed GEO-SEO Codex skill to $INSTALL_DIR"
printf '\nTry in Codex CLI:\n'
printf '  $geo quick https://example.com\n'
printf '  $geo audit https://example.com\n\n'
