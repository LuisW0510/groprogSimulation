#requires -Version 5.1
$ErrorActionPreference = "Stop"

# Script liegt in src/scripts -> Project Root ist zwei Ebenen höher
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

$InputDir    = Join-Path $ProjectRoot "input"
$ResultsDir  = Join-Path $ProjectRoot "example_run_results"
$OutDir      = Join-Path $ProjectRoot "out"

Write-Host "Project root: $ProjectRoot"
Write-Host "Input dir:    $InputDir"
Write-Host "Results dir:  $ResultsDir"
Write-Host ""

# Ergebnisse neu erstellen (optional: löschen auskommentieren, wenn du alte behalten willst)
if (Test-Path $ResultsDir) { Remove-Item $ResultsDir -Recurse -Force }
New-Item -ItemType Directory -Path $ResultsDir | Out-Null

$inputs = Get-ChildItem -Path $InputDir -Filter "*.txt"
if ($inputs.Count -eq 0) {
    throw "Keine .txt Dateien in $InputDir gefunden."
}

foreach ($file in $inputs) {
    $base = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
    $targetDir = Join-Path $ResultsDir $base

    Write-Host "--------------------------------------------"
    Write-Host "Running example: $base"

    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null

    # Ausfuehren im Projektroot, damit Imports/relative Pfade stimmen
    Push-Location $ProjectRoot
    try {
        python -m src.main $file.FullName
    }
    finally {
        Pop-Location
    }

    if (Test-Path $OutDir) {
        Copy-Item -Path (Join-Path $OutDir "*") -Destination $targetDir -Recurse -Force
        Remove-Item $OutDir -Recurse -Force
    }
    else {
        Write-Warning "Kein Output-Ordner '$OutDir' gefunden nach Run $base"
    }
}

Write-Host "--------------------------------------------"
Write-Host "Fertig. Ergebnisse unter: $ResultsDir"
