#!/bin/bash
#
# ARM64 WebDriver Installation Script for Kali Linux
# Automatically installs geckodriver and/or chromium-driver for ARM64 architecture
#

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     XSS-Hunter ARM64 WebDriver Installation Script      ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Detect architecture
ARCH=$(uname -m)
echo "[*] Detected architecture: $ARCH"

if [[ "$ARCH" != "aarch64" && "$ARCH" != "arm64" ]]; then
    echo "[!] Warning: This script is designed for ARM64/aarch64 systems."
    echo "[!] Your system is: $ARCH"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Clean bad webdriver-manager cache
echo ""
echo "[*] Cleaning webdriver-manager cache..."
if [ -d ~/.wdm/drivers ]; then
    rm -rf ~/.wdm/drivers
    echo "[+] Removed ~/.wdm/drivers"
else
    echo "[*] No existing cache found"
fi

# Ask which browser to install
echo ""
echo "[*] Which browser driver would you like to install?"
echo "    1. Firefox (geckodriver) - Recommended"
echo "    2. Chromium (chromedriver)"
echo "    3. Both"
read -p "Select option (1-3) [1]: " BROWSER_CHOICE
BROWSER_CHOICE=${BROWSER_CHOICE:-1}

install_firefox=false
install_chrome=false

case $BROWSER_CHOICE in
    1)
        install_firefox=true
        ;;
    2)
        install_chrome=true
        ;;
    3)
        install_firefox=true
        install_chrome=true
        ;;
    *)
        echo "[!] Invalid choice, installing Firefox only"
        install_firefox=true
        ;;
esac

# Install Firefox + geckodriver
if [ "$install_firefox" = true ]; then
    echo ""
    echo "[*] Installing Firefox and geckodriver..."
    
    # Install Firefox
    sudo apt update
    sudo apt install -y firefox-esr wget tar
    
    # Download and install geckodriver for ARM64
    echo "[*] Downloading geckodriver for ARM64..."
    GECKO_VERSION="v0.36.0"
    GECKO_URL="https://github.com/mozilla/geckodriver/releases/download/${GECKO_VERSION}/geckodriver-${GECKO_VERSION}-linux-aarch64.tar.gz"
    
    cd /tmp
    wget -q --show-progress "$GECKO_URL" -O geckodriver.tar.gz
    tar -xzf geckodriver.tar.gz
    chmod +x geckodriver
    sudo mv geckodriver /usr/local/bin/
    rm geckodriver.tar.gz
    
    # Verify installation
    if command -v geckodriver &> /dev/null; then
        echo "[+] geckodriver installed successfully:"
        geckodriver --version | head -n 1
    else
        echo "[!] Warning: geckodriver not found in PATH"
    fi
fi

# Install Chromium + chromedriver
if [ "$install_chrome" = true ]; then
    echo ""
    echo "[*] Installing Chromium and chromedriver..."
    
    sudo apt update
    sudo apt install -y chromium chromium-driver
    
    # Verify installation
    if command -v chromedriver &> /dev/null; then
        echo "[+] chromedriver installed successfully:"
        chromedriver --version
    else
        echo "[!] Warning: chromedriver not found in PATH"
    fi
fi

# Set environment variables
echo ""
echo "[*] Setting environment variables..."
export WDM_ARCH=arm64
echo "export WDM_ARCH=arm64" >> ~/.bashrc

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                  Installation Complete!                  ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "[+] WebDriver installation completed successfully!"
echo ""
echo "Next steps:"
echo "  1. Reload your shell: source ~/.bashrc"
echo "  2. Activate virtual environment: source venv/bin/activate"
echo "  3. Run XSS-Hunter: python3 main.py"
echo ""
