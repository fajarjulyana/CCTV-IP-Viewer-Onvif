pyinstaller --noconfirm --onefile --windowed \
 --add-binary "/usr/bin/ffplay:." \
 --icon "cctv.png" \
 cctv.py

