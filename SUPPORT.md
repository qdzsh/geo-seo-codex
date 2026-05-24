# Support

## Supported Use

GEO-SEO Codex is intended for technical users who can run Codex CLI, Python, and
Git locally.

Supported platforms:

- Windows with PowerShell 7
- macOS with Bash or zsh
- Linux with Bash

Supported Python versions are the versions tested by CI. See
`.github/workflows/ci.yml`.

## Getting Help

Before opening an issue:

1. Run `$geo doctor`.
2. Run `$geo self-test`.
3. Confirm `~/.codex/skills/geo/SKILL.md` exists.
4. Confirm the installed venv Python can run:
   `~/.codex/skills/geo/.venv/bin/python ~/.codex/skills/geo/scripts/geo_cli.py --help`

On Windows, use:

```powershell
~/.codex/skills/geo/.venv/Scripts/python.exe ~/.codex/skills/geo/scripts/geo_cli.py --help
```

## Issue Scope

Open a bug report for:

- Installer failures.
- Runtime errors in `geo_cli.py`.
- Incorrect generated artifacts.
- Documentation that causes a failed install or wrong command.

Open a feature request for:

- New GEO checks.
- New report formats.
- New schema templates.
- Better platform-specific analysis.

Do not include private client reports, credentials, API keys, or proprietary URLs
unless they are safe to share publicly.
