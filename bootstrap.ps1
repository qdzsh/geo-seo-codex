#Requires -Version 7.0
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$baseUri = "https://github.com/quangdo126/geo-seo-codex/releases/latest/download"
$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("geo-seo-codex-" + [System.Guid]::NewGuid().ToString("N"))
$zipPath = Join-Path $tempDir "geo-seo-codex.zip"
$checksumPath = Join-Path $tempDir "geo-seo-codex.zip.sha256"
$extractDir = Join-Path $tempDir "extract"

try {
    New-Item -ItemType Directory -Force -Path $tempDir, $extractDir | Out-Null
    Invoke-WebRequest -Uri "$baseUri/geo-seo-codex.zip" -OutFile $zipPath
    Invoke-WebRequest -Uri "$baseUri/geo-seo-codex.zip.sha256" -OutFile $checksumPath

    $expected = ((Get-Content -Raw -Path $checksumPath).Trim() -split "\s+")[0].ToLowerInvariant()
    $actual = (Get-FileHash -Algorithm SHA256 -Path $zipPath).Hash.ToLowerInvariant()
    if ($expected -ne $actual) {
        throw "Checksum mismatch for geo-seo-codex.zip. Expected $expected but got $actual."
    }

    Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force
    $skillFile = Get-ChildItem -Path $extractDir -Recurse -Filter SKILL.md | Select-Object -First 1
    if (-not $skillFile) {
        throw "Downloaded archive does not contain SKILL.md."
    }

    Push-Location $skillFile.DirectoryName
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
