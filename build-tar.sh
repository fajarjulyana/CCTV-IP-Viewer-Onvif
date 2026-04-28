#!/bin/bash
set -e

APPNAME="cctv"
VERSION="1.0"
TAR_DIR="${APPNAME}-${VERSION}"

# Bersihkan
rm -rf "$TAR_DIR"
mkdir -p "$TAR_DIR"

# Deteksi hasil PyInstaller
if [ -d "dist/$APPNAME" ]; then
    # Folder (mode normal)
    echo "📁 Menyalin dari folder dist/$APPNAME ..."
    cp -r dist/$APPNAME/* "$TAR_DIR/"
elif [ -f "dist/$APPNAME" ]; then
    # File tunggal (mode --onefile)
    echo "📦 Menyalin file tunggal dist/$APPNAME ..."
    cp "dist/$APPNAME" "$TAR_DIR/"
else
    echo "❌ Error: dist/$APPNAME tidak ditemukan. Pastikan sudah build dengan PyInstaller."
    exit 1
fi

# Copy file tambahan
cp cctv.png README.md before.txt after.txt install.sh uninstall.sh "$TAR_DIR/"

# Install script
chmod +x "$TAR_DIR/install.sh"

# Tambahkan script launcher
cat << EOF > "$TAR_DIR/run-cctv.sh"
#!/bin/bash
DIR="\$(dirname "\$0")"
"\$DIR/$APPNAME" "\$@"
EOF
chmod +x "$TAR_DIR/run-cctv.sh"

# Buat arsip tar.gz
tar -czvf "${TAR_DIR}.tar.gz" "$TAR_DIR"

echo "✅ Paket TAR.GZ berhasil dibuat: ${TAR_DIR}.tar.gz"

