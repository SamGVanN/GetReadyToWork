@echo off
REM Script d'installation automatique pour Windows

where python >nul 2>nul
if errorlevel 1 (
    echo Python n'est pas installe. Veuillez l'installer d'abord.
    pause
    exit /b 1
)

where pip >nul 2>nul
if errorlevel 1 (
    echo pip n'est pas installe. Veuillez l'installer d'abord.
    pause
    exit /b 1
)

echo Installation des dependances Python...
pip install --user -r installers\requirements-windows.txt

echo Installation terminee. Vous pouvez lancer le parametrage avec :
echo python src\app_configurator\ParametrageGetReadyToWork.py
pause
