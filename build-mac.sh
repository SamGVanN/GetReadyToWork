#!/bin/bash
# Script de build automatique pour macOS

echo "Cleaning up previous macOS build directory..."
rm -rf dist/macos
mkdir -p dist/macos

echo "Running macOS build (bdist_mac)..."
python setup.py bdist_mac --dist-dir dist/macos

# The .app bundle will be inside dist/macos/Get Ready To Work.app
# No specific move needed if --dist-dir works as expected for bdist_mac

echo "Build for macOS completed. Output is in dist/macos"
