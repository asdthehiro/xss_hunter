#!/bin/bash
# Setup script for XSS-Hunter

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║              XSS-Hunter Setup Script                     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "[*] Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "[-] Python 3 not found. Please install Python 3.10 or higher."
    exit 1
fi

echo ""
echo "[*] Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "[+] Setup complete!"
    echo ""
    echo "To run XSS-Hunter:"
    echo "  python3 main.py"
    echo ""
    echo "For help:"
    echo "  python3 main.py --help"
else
    echo "[-] Installation failed. Please check the error messages above."
    exit 1
fi
