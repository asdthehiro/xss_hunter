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
echo "[*] Creating Python virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "[-] Failed to create virtual environment."
    exit 1
fi

echo "[*] Activating virtual environment..."
source venv/bin/activate

echo ""
echo "[*] Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "[+] Setup complete!"
    echo ""
    echo "To run XSS-Hunter:"
    echo "  source venv/bin/activate"
    echo "  python3 main.py"
    echo ""
    echo "For help:"
    echo "  source venv/bin/activate"
    echo "  python3 main.py --help"
    echo ""
    echo "To deactivate virtual environment:"
    echo "  deactivate"
else
    echo "[-] Installation failed. Please check the error messages above."
    exit 1
fi
