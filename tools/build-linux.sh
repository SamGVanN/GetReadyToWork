#!/bin/bash
# Script de build automatique pour Linux (PyInstaller only)
set -e

# Change to project root
cd "$(dirname "$0")/.."

# Clean previous output
rm -rf dist
rm -rf build
rm -rf release-linux
rm -rf buildspec

# Generate version_info.txt from src/common/version.py
python3 tools/generate_version_info.py

# Build GetReadyToWork
pyinstaller --onefile --paths . src/app_launcher/GetReadyToWork.py --name GetReadyToWork
# Build ParametrageGetReadyToWork
pyinstaller --onefile --paths . src/app_configurator/ParametrageGetReadyToWork.py --name ParametrageGetReadyToWork

echo Release will now be created in release-linux/
# Create release folder and copy everything needed
mkdir release-linux
cp dist/GetReadyToWork release-linux/
cp dist/ParametrageGetReadyToWork release-linux/
cp -r runtime release-linux/
cp -r src/config release-linux/config
cp -r src/common release-linux/common
cp src/common/version.py release-linux/common/
cp tools/install-desktop.sh release-linux/
chmod +x release-linux/install-desktop.sh

# Clean up .spec files
rm -f GetReadyToWork.spec
rm -f ParametrageGetReadyToWork.spec

# Optionally remove dist and build folders to avoid confusion
rm -rf dist
rm -rf build

echo "Release folder is ready in release-linux/"
