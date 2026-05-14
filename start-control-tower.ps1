param(
    [string]$PythonPath = ""
)

$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

function Resolve-ControlTowerPython {
    param([string]$PreferredPython)

    if ($PreferredPython) {
        if (-not (Test-Path -LiteralPath $PreferredPython)) {
            throw "Specified PythonPath not found: $PreferredPython"
        }
        return $PreferredPython
    }

    $venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $venvPython) {
        return $venvPython
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        return $pythonCommand.Source
    }

    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        return $pyLauncher.Source
    }

    throw "Python was not found. Install Python for Windows or create .venv before starting the server."
}

$pythonExe = Resolve-ControlTowerPython -PreferredPython $PythonPath

Write-Host "[0-a-control] Starting local server from Windows PowerShell..."
Write-Host ""
Write-Host "Repository root:"
Write-Host "  $PSScriptRoot"
Write-Host ""
Write-Host "Python:"
Write-Host "  $pythonExe"
Write-Host ""
Write-Host "Browser URL:"
Write-Host "  http://localhost:4310"
Write-Host ""
Write-Host "Telegram:"
Write-Host "  If TELEGRAM_API_ID / TELEGRAM_API_HASH are configured, sync works directly in 0-a-control."
Write-Host ""

if ((Split-Path -Leaf $pythonExe) -ieq "py.exe") {
    & $pythonExe -3 scripts/server.py
} else {
    & $pythonExe scripts/server.py
}

Write-Host ""
Write-Host "[0-a-control] Server stopped."
