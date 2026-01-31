# artfish PowerShell Entry Point
# Allows single-line execution from any location.
# Usage: .\artfish.ps1 --goals "create art" "style it"

$ScriptPath = $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path $ScriptPath -Parent

# Ensure we are in the project root
Push-Location $ProjectRoot

try {
    # Check for python
    if (!(Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Error "Python is not installed or not in PATH."
        return
    }

    # Execute artfish via module interface or direct script
    python "$ProjectRoot\main.py" $args
}
finally {
    Pop-Location
}
