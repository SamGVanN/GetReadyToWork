#!/bin/bash
# Script de build automatique pour macOS (PyInstaller only)

# Clean previous output
rm -rf dist
rm -rf build
rm -rf release-mac
rm -rf buildspec

# Generate version_info.txt from src/common/version.py
python3 tools/generate_version_info.py

# Build GetReadyToWork (windowed)
pyinstaller --onefile --windowed src/app_launcher/GetReadyToWork.py --name GetReadyToWork --add-data "src/config:i18n_resources.py,scan_paths_windows.py,scan_paths_mac.py,scan_paths_linux.py,scan_paths_user.json" --add-data "runtime:default.json,apps_to_launch.json" --add-data "src/common:utils.py,config_manager.py,__init__.py"
# Build ParametrageGetReadyToWork (windowed)
pyinstaller --onefile --windowed src/app_configurator/ParametrageGetReadyToWork.py --name ParametrageGetReadyToWork --add-data "src/config:i18n_resources.py,scan_paths_windows.py,scan_paths_mac.py,scan_paths_linux.py,scan_paths_user.json" --add-data "runtime:default.json,apps_to_launch.json" --add-data "src/common:utils.py,config_manager.py,__init__.py"

# Create release folder and copy everything needed
mkdir release-mac
cp dist/GetReadyToWork release-mac/
cp dist/ParametrageGetReadyToWork release-mac/
cp -r runtime release-mac/
cp -r src/config release-mac/config
cp -r src/common release-mac/common
cp src/common/version.py release-mac/common/

# Clean up .spec files
rm -f GetReadyToWork.spec
rm -f ParametrageGetReadyToWork.spec

# Optionally remove dist and build folders to avoid confusion
rm -rf dist
rm -rf build

echo "Release folder is ready in release-mac/"
