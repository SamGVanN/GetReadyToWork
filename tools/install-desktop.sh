#!/bin/bash
# install-desktop.sh
# Installs GetReadyToWork and creates .desktop entries in the Linux application menu.

set -e

SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="$HOME/.local/share/GetReadyToWork"
DESKTOP_DIR="$HOME/.local/share/applications"

echo "Installing GetReadyToWork to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cp -r "$SOURCE_DIR/"* "$INSTALL_DIR/"
# Ensure executables have correct permissions
chmod +x "$INSTALL_DIR/GetReadyToWork" "$INSTALL_DIR/ParametrageGetReadyToWork"

echo "Creating desktop shortcuts..."
mkdir -p "$DESKTOP_DIR"

# Launcher
cat > "$DESKTOP_DIR/GetReadyToWork.desktop" << EOF
[Desktop Entry]
Name=GetReadyToWork
Comment=Launch all your work apps in one click
Exec="$INSTALL_DIR/GetReadyToWork"
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Utility;
EOF

# Configurator
cat > "$DESKTOP_DIR/GetReadyToWork-Config.desktop" << EOF
[Desktop Entry]
Name=GetReadyToWork Config
Comment=Configure your startup applications
Exec="$INSTALL_DIR/ParametrageGetReadyToWork"
Icon=preferences-system
Terminal=false
Type=Application
Categories=Settings;
EOF

echo "Installation complete!"
echo "GetReadyToWork has been installed to $INSTALL_DIR"
echo "Desktop entries installed in $DESKTOP_DIR"
echo "You can now find the application in your system menu and safely delete this downloaded folder."
