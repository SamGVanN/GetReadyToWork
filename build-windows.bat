@echo off
REM Script de build automatique pour Windows (PyInstaller only)

REM Clean previous output
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist release-windows rmdir /s /q release-windows
if exist buildspec rmdir /s /q buildspec

REM Generate version_info.txt from src/common/version.py
python tools\generate_version_info.py

REM Build GetReadyToWork.exe
pyinstaller --onefile --noconsole --version-file version_info.txt src\app_launcher\GetReadyToWork.py --name GetReadyToWork --add-data "src\\config;i18n_resources.py,scan_paths_windows.py,scan_paths_mac.py,scan_paths_linux.py,scan_paths_user.json" --add-data "runtime;default.json,apps_to_launch.json" --add-data "src\\common;utils.py,config_manager.py,__init__.py"
REM Build ParametrageGetReadyToWork.exe
pyinstaller --onefile --noconsole --version-file version_info.txt src\app_configurator\ParametrageGetReadyToWork.py --name ParametrageGetReadyToWork --add-data "src\\config;i18n_resources.py,scan_paths_windows.py,scan_paths_mac.py,scan_paths_linux.py,scan_paths_user.json" --add-data "runtime;default.json,apps_to_launch.json" --add-data "src\\common;utils.py,config_manager.py,__init__.py"

REM Create release folder and copy everything needed
mkdir release-windows
copy dist\GetReadyToWork.exe release-windows\ >nul
copy dist\ParametrageGetReadyToWork.exe release-windows\ >nul
xcopy runtime release-windows\runtime /E /I /Y >nul
xcopy src\config release-windows\config /E /I /Y >nul
xcopy src\common release-windows\common /E /I /Y >nul

REM Clean up .spec files
if exist GetReadyToWork.spec del GetReadyToWork.spec
if exist ParametrageGetReadyToWork.spec del ParametrageGetReadyToWork.spec

REM Optionally remove dist and build folders to avoid confusion
rmdir /s /q dist
rmdir /s /q build

echo Release folder is ready in release-windows\
pause
