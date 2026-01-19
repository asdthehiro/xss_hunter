# Quick Reference - XSS-Hunter on Kali Linux

## Installation (One-Time Setup)
```bash
git clone https://github.com/asdthehiro/xss_hunter.git
cd xss_hunter
chmod +x setup.sh
./setup.sh
```

## Every Time You Use
```bash
cd xss_hunter
source venv/bin/activate
python3 main.py
```

## Browser Selection
- **Firefox** = Press 1 or Enter (Default - Recommended)
- **Chrome** = Press 2

## Common Commands
```bash
# Basic scan
python3 main.py

# Scan with URL list
python3 main.py --urls targets.txt

# Enable crawling
python3 main.py --crawl

# Save results
python3 main.py --output results.txt

# Full scan
python3 main.py --crawl --advanced --output full_scan.txt
```

## Troubleshooting Quick Fixes

### Error: Exec format error (ChromeDriver)
```bash
# Solution: Use Firefox instead
When prompted: Select browser (1 or 2) [1]: 1
```

### Error: Firefox not found
```bash
sudo apt install firefox-esr
```

### Error: WebDriver issues
```bash
source venv/bin/activate
pip install --upgrade selenium webdriver-manager
```

### Error: Permission denied
```bash
sudo chmod +x /usr/bin/firefox
```

## Authentication Flow
1. Enter target URL
2. Select method 1 (Browser-based)
3. Select browser 1 (Firefox)
4. Firefox opens automatically
5. Log in manually (including OTP/2FA)
6. Press Enter in terminal
7. Done! Scanning starts

## File Structure
```
xss_hunter/
├── venv/              # Virtual environment (created by setup)
├── main.py            # Main script
├── README.md          # Full documentation
├── KALI_SETUP.md      # Kali-specific guide
├── requirements.txt   # Dependencies
└── setup.sh           # Automated setup
```

## Need Help?
- Full docs: `README.md`
- Kali guide: `KALI_SETUP.md`
- Browser auth: `BROWSER_AUTH_GUIDE.md`
