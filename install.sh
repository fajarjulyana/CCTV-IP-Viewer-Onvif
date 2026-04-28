#!/bin/bash
# =========================================
# CCTV IP Installer for Linux (no dist folder)
# Created by Fajar Julyana (Bandung, Indonesia)
# =========================================

set -e

APP_NAME="cctv"
APP_DESC="CCTV IP Viewer"
INSTALL_DIR="/usr/local/bin"
ICON_DIR="/usr/local/share/icons/hicolor/256x256/apps"
DESKTOP_DIR="/usr/local/share/applications"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "📦 Menginstal $APP_NAME ..."

# Pastikan file binary ada
if [ ! -f "$SCRIPT_DIR/$APP_NAME" ]; then
    echo "❌ File $APP_NAME tidak ditemukan di folder ini!"
    exit 1
fi

# Pastikan file ikon ada
if [ ! -f "$SCRIPT_DIR/${APP_NAME}.png" ]; then
    echo "❌ Ikon ${APP_NAME}.png tidak ditemukan di folder ini!"
    exit 1
fi

# Buat direktori target bila belum ada
echo "📁 Memastikan direktori instalasi tersedia..."
sudo mkdir -p "$INSTALL_DIR" "$ICON_DIR" "$DESKTOP_DIR"

# Copy binary
echo "➡️  Menyalin binary ke $INSTALL_DIR..."
sudo install -Dm755 "$SCRIPT_DIR/$APP_NAME" "$INSTALL_DIR/$APP_NAME"

# Copy icon
echo "➡️  Menyalin ikon ke $ICON_DIR..."
sudo install -Dm644 "$SCRIPT_DIR/${APP_NAME}.png" "$ICON_DIR/${APP_NAME}.png"

# Buat desktop entry
echo "➡️  Membuat file .desktop..."
sudo tee "$DESKTOP_DIR/${APP_NAME}.desktop" >/dev/null <<EOF
[Desktop Entry]
Name=CCTV IP
Comment=$APP_DESC
Exec=$INSTALL_DIR/$APP_NAME
Icon=$APP_NAME
Terminal=false
Type=Application
Categories=Video;Network;
StartupNotify=true
EOF

# Refresh cache desktop & icon
echo "🔄 Memperbarui database desktop dan ikon..."
sudo update-desktop-database "$DESKTOP_DIR" || true
sudo gtk-update-icon-cache "$ICON_DIR/.." -f || true

# Pesan akhir
echo ""
echo "✅ Instalasi selesai!"
echo "📍 Jalankan dari menu aplikasi (ketik 'CCTV IP') atau via terminal: $APP_NAME"

