#!/bin/bash
# Script de build automatique pour Linux (AppImage)

echo "Cleaning up previous Linux build directory..."
rm -rf dist/linux
mkdir -p dist/linux

echo "Running Linux build (bdist_appimage)..."
# The bdist_appimage command from cx_Freeze often creates the AppImage in the 'dist' directory by default.
# The 'appimage_path' option in setup.py for bdist_appimage is 'GetReadyToWork.AppImage'.
# We will run the command and then move the AppImage to dist/linux.

python setup.py bdist_appimage

# Default output location for bdist_appimage is usually dist/
# The name is defined in setup.py's bdist_appimage_options as 'GetReadyToWork.AppImage'
if [ -f "dist/GetReadyToWork.AppImage" ]; then
    echo "Moving AppImage to dist/linux/"
    mv dist/GetReadyToWork.AppImage dist/linux/
else
    echo "WARNING: AppImage not found in default dist/ location. Check cx_Freeze output."
fi

echo "Build for Linux (AppImage) completed. Output is in dist/linux"
