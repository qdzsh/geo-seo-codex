#Requires -Version 7.0
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repo = "https://github.com/quangdo126/geo-seo-codex.git"
$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("geo-seo-codex-" + [System.Guid]::NewGuid().ToString("N"))

try {
    git clone --depth 1 $repo $tempDir
    Push-Location $tempDir
    try {
        ./install.ps1
    } finally {
        Pop-Location
    }
} finally {
    if (Test-Path $tempDir) {
        Remove-Item -Recurse -Force -LiteralPath $tempDir
    }
}
