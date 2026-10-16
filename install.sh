#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APPS="$HOME/.local/share/applications"
DESKTOP="$APPS/Youtube Downloader.desktop"
RUN="$DIR/run.sh"
mkdir -p "$APPS"

if [ ! -f ".venv/bin/activate" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi


source .venv/bin/activate
echo
echo "Virtual Enviroment is activated!"
echo
echo "Downloading packages..."

python3 -m pip install --upgrade pip
pip install -r "$DIR/src/requirements.txt"

echo
echo "Packages install Complete!"
echo
echo "Downloading an Executable file..."
echo

if [ -f "$RUN" ]; then
    echo "An Executable file is already downloaded! path: $RUN"
else
cat > "$RUN" <<EOF
#!/usr/bin/env bash
# run.sh
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$DIR/.venv/bin/python" "$DIR/src/downloader.py" "$@"
EOF

chmod +x "$RUN"

echo "$RUN was Installed!"
fi
echo
echo "Installing A Desktop File..."
echo

if [ -f "$DESKTOP" ]; then
    echo "A Desktop file is already downloaded! path: $DESKTOP"
else
cat > "$DESKTOP" <<EOF
[Desktop Entry]
Type=Application
Name=Youtube Downloader
Comment=Download videos from youtube!
Exec=$DIR/run.sh
Icon=$DIR/src/icon.png
Terminal=false
Categories=Network;
EOF

chmod +x "$DESKTOP"
update-desktop-database "$APPS" 2>/dev/null || true

echo "$DESKTOP was Installed!"
fi

echo
echo "The Youtube Downloader was installed, enjoy!"
exit 0

