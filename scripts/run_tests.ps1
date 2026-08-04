Set-Location $PSScriptRoot/..
$python = "C:/Program Files/Python314/python3.14t.exe"

if (-not (Test-Path $python)) {
    Write-Error "Python interpreter not found at $python"
    exit 1
}

& $python -m pytest -q tests/test_calendar_service.py
exit $LASTEXITCODE
