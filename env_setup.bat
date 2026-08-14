@echo off
REM env_setup.bat — installe les dépendances du projet
REM Usage: double-cliquez ou exécutez depuis PowerShell/CMD dans le dossier du projet

REM Utilise `python -m pip` pour garantir l'interpréteur actif
python -m pip install --upgrade pip
python -m pip install -r "%~dp0requirements.txt"
echo.
echo Install complete. If a command failed, try running this script from a terminal with administrator rights or use the PowerShell script `setup.ps1`.
pause
