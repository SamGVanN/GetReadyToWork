@echo off
REM Script de build automatique pour Windows
REM Utilise le dossier build/latest pour toujours generer dans le meme dossier

echo Cleaning up previous build directory...
if exist build\latest rmdir /s /q build\latest
if exist dist\win rmdir /s /q dist\win

echo Running Windows build...
python setup.py build_exe --build-exe build/latest

REM CX_FREEZE_OUTPUT_PATH is typically build\exe.win-amd64-3.x or similar
REM If the build output is consistently in a subfolder of build/latest,
REM we might need to add a step to move files to build/latest directly or dist/win.
REM For now, assuming build_exe with --build-exe correctly places it.

echo Build for Windows completed. Output is in build/latest
pause
