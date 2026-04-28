#!/bin/bash
set -e

APPNAME="cctv"
VERSION="1.0"
ARCH="amd64"
BUILD_DIR="build-deb"

# Bersihkan
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/share/$APPNAME"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/64x64/apps"

# Deteksi hasil PyInstaller
if [ -d "dist/$APPNAME" ]; then
    echo "📁 Menyalin dari folder dist/$APPNAME ..."
    cp -r dist/$APPNAME/* "$BUILD_DIR/usr/share/$APPNAME/"
elif [ -f "dist/$APPNAME" ]; then
    echo "📦 Menyalin file tunggal dist/$APPNAME ..."
    cp "dist/$APPNAME" "$BUILD_DIR/usr/share/$APPNAME/"
else
    echo "❌ Error: dist/$APPNAME tidak ditemukan. Pastikan sudah build dengan PyInstaller."
    exit 1
fi

# Copy file tambahan
cp cctv.png "$BUILD_DIR/usr/share/icons/hicolor/64x64/apps/$APPNAME.png"
cp README.md before.txt after.txt install.sh uninstall.sh "$BUILD_DIR/usr/share/$APPNAME/"

# Launcher CLI
cat << EOF > "$BUILD_DIR/usr/bin/$APPNAME"
#!/bin/bash
/usr/share/$APPNAME/$APPNAME "\$@"
EOF
chmod +x "$BUILD_DIR/usr/bin/$APPNAME"

# File .desktop
cat << EOF > "$BUILD_DIR/usr/share/applications/$APPNAME.desktop"
[Desktop Entry]
Name=CCTV IP
Comment=Simple RTSP CCTV Viewer
Exec=$APPNAME
Icon=$APPNAME
Terminal=false
Type=Application
Categories=Video;Network;
EOF

# Kontrol Debian
cat << EOF > "$BUILD_DIR/DEBIAN/control"
Package: $APPNAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Depends: ffmpeg, python3-tk
Maintainer: Fajar Julyana <fajarjulyana1@gmail.com>
Description: GUI RTSP CCTV Viewer built with Tkinter and FFplay
EOF

# Build paket
dpkg-deb --build "$BUILD_DIR" "${APPNAME}_${VERSION}_${ARCH}.deb"

echo "✅ Paket Debian berhasil dibuat: ${APPNAME}_${VERSION}_${ARCH}.deb"

