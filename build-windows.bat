@echo off
REM Script de build automatique pour Windows
REM Utilise le dossier build/latest pour toujours générer dans le même dossier

python setup.py build --build-exe build/latest

pause
