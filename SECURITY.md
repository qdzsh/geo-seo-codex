# Security Policy

## Supported Versions

Security fixes are provided for the latest tagged release.

| Version | Supported |
|---|---|
| Latest | Yes |
| Older releases | Best effort |

## Reporting a Vulnerability

Please report security issues privately by opening a GitHub security advisory if
available, or by contacting the repository owner directly. Do not open a public
issue for vulnerabilities involving command execution, unsafe downloads, path
traversal, credential exposure, or data leakage.

Include:

- Affected version or commit.
- Operating system and Python version.
- Reproduction steps.
- Expected and actual behavior.
- Any proof-of-concept input or target URL that is safe to share.

## Security Expectations

- Installers must avoid destructive operations outside `~/.codex/skills/geo/`.
- Release archives should include SHA-256 checksums.
- Generated audit reports may contain sensitive client data and are ignored by git.
- The project does not collect telemetry.
- Network requests are limited to user-provided targets, public sources used for
  audits, GitHub repository install assets, release assets, and package installation.
