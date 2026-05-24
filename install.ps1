#Requires -Version 7.0
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$codexDir = Join-Path $HOME ".codex"
$skillsDir = Join-Path $codexDir "skills"
$installDir = Join-Path $skillsDir "geo"
$venvDir = Join-Path $installDir ".venv"

function Write-Info($message) { Write-Host "-> $message" -ForegroundColor Cyan }
function Write-Ok($message) { Write-Host "[OK] $message" -ForegroundColor Green }
function Write-Warn($message) { Write-Host "[WARN] $message" -ForegroundColor Yellow }

function Find-Python {
    foreach ($cmd in @("python", "py")) {
        $resolved = Get-Command $cmd -ErrorAction SilentlyContinue
        if (-not $resolved) { continue }
        try {
            $versionOutput = & $cmd --version 2>&1
            if ($versionOutput -match "Python (\d+)\.(\d+)") {
                $major = [int]$Matches[1]
                $minor = [int]$Matches[2]
                if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 8)) {
                    return $cmd
                }
            }
        } catch {
            continue
        }
    }
    throw "Python 3.8+ is required but was not found on PATH."
}

Write-Host ""
Write-Host "GEO-SEO Codex Skill Installer" -ForegroundColor Cyan
Write-Host ""

$pythonCmd = Find-Python
Write-Ok "Python found: $(& $pythonCmd --version)"

$codexCmd = Get-Command codex -ErrorAction SilentlyContinue
if ($codexCmd) {
    Write-Ok "Codex CLI found"
} else {
    Write-Warn "Codex CLI was not found on PATH. Files will still be installed."
}

$sourceDir = Split-Path -Parent $PSCommandPath
if (-not (Test-Path (Join-Path $sourceDir "SKILL.md"))) {
    throw "Run this installer from the GEO-SEO Codex project directory."
}

New-Item -ItemType Directory -Force -Path $installDir | Out-Null
foreach ($child in Get-ChildItem -Force -Path $installDir) {
    Remove-Item -Recurse -Force -LiteralPath $child.FullName
}

Write-Info "Copying Codex skill files"
Copy-Item -Force (Join-Path $sourceDir "SKILL.md") (Join-Path $installDir "SKILL.md")
Copy-Item -Recurse -Force (Join-Path $sourceDir "references") (Join-Path $installDir "references")
Copy-Item -Recurse -Force (Join-Path $sourceDir "agents") (Join-Path $installDir "agents")
if (Test-Path (Join-Path $sourceDir "assets")) {
    Copy-Item -Recurse -Force (Join-Path $sourceDir "assets") (Join-Path $installDir "assets")
}

Write-Info "Copying scripts and schema templates"
Copy-Item -Recurse -Force (Join-Path $sourceDir "scripts") (Join-Path $installDir "scripts")
Copy-Item -Recurse -Force (Join-Path $sourceDir "schema") (Join-Path $installDir "schema")
Copy-Item -Force (Join-Path $sourceDir "requirements.txt") (Join-Path $installDir "requirements.txt")

Write-Info "Creating isolated Python environment"
if (Test-Path $venvDir) {
    Remove-Item -Recurse -Force -LiteralPath $venvDir
}
& $pythonCmd -m venv $venvDir

$venvPython = Join-Path $venvDir "Scripts/python.exe"
Write-Info "Installing Python dependencies"
& $venvPython -m pip install --upgrade pip --quiet
& $venvPython -m pip install -r (Join-Path $installDir "requirements.txt") --quiet

Write-Info "Verifying installation"
$required = @(
    (Join-Path $installDir "SKILL.md"),
    (Join-Path $installDir "scripts/geo_cli.py"),
    (Join-Path $installDir "schema/organization.json"),
    $venvPython
)
foreach ($path in $required) {
    if (-not (Test-Path $path)) {
        throw "Missing expected file: $path"
    }
}

Write-Ok "Installed GEO-SEO Codex skill to $installDir"
Write-Host ""
Write-Host "Try in Codex CLI:" -ForegroundColor Cyan
Write-Host '  $geo quick https://example.com'
Write-Host '  $geo audit https://example.com'
Write-Host ""
