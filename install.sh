#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$DIR/.venv"
APPS="$HOME/.local/share/applications"
DESKTOP="$APPS/Youtube Downloader.desktop"
RUN="$DIR/run.sh"
REQ_FILE="$DIR/src/requirements.txt"

mkdir -p "$APPS"

# 1. Create Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# 2. Activate Virtual Environment
source "$VENV_DIR/bin/activate"
echo "Virtual Environment is activated!"
echo

# 3. Install Packages (MOVED THIS UP!)
echo "Downloading packages..."
PYTHON_BIN="$DIR/.venv/bin/python3"

# Ensure pip is up to date
"$PYTHON_BIN" -m pip install --upgrade pip

# Install from requirements.txt
if [ -f "$REQ_FILE" ]; then
    echo "Installing from requirements.txt..."
    "$PYTHON_BIN" -m pip install -r "$REQ_FILE"
else
    echo "ERROR: $REQ_FILE not found!"
    exit 1
fi
echo

# 4. Verify Packages (NOW THIS RUNS *AFTER* INSTALLATION)
echo "Verifying Python packages..."
PYTHON_PACKAGES=(
    "customtkinter"
    "imageio_ffmpeg"
    "PyQt5"
    "pyautogui"
    "yt_dlp"
)

MISSING_PKGS=()

for pkg in "${PYTHON_PACKAGES[@]}"; do
    # Try to import the module silently
    if ! "$PYTHON_BIN" -c "import $pkg" &> /dev/null; then
        MISSING_PKGS+=("$pkg")
    fi
done

if [ ${#MISSING_PKGS[@]} -ne 0 ]; then
    echo -e "\e[31mError: The following Python packages failed to install:\e[0m"
    for pkg in "${MISSING_PKGS[@]}"; do
        echo "  - $pkg"
    done
    echo "Please check your requirements.txt and try running the installer again."
    exit 1
else
    echo -e "\e[32mAll Python packages are successfully installed!\e[0m"
fi
echo

# 5. Create run.sh
echo "Downloading an Executable file..."
echo

if [ -f "$RUN" ]; then
    echo "An Executable file is already downloaded! path: $RUN"
else
cat > "$RUN" <<'EOF'
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

# 6. Create Desktop File
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