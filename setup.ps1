param(
    [string]$PythonPath = "python"
)

# setup.ps1 — installe les dépendances du projet en utilisant l'interpréteur fourni
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$requirements = Join-Path $scriptDir 'requirements.txt'

Write-Host "Using Python executable: $PythonPath"
& $PythonPath -m pip install --upgrade pip
& $PythonPath -m pip install -r $requirements

Write-Host "Installation complete."
