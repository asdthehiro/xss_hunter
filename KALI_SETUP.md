# Kali Linux Setup Guide

## Quick Start for Kali Linux

XSS-Hunter is optimized for Kali Linux and uses **Firefox by default** (pre-installed on Kali).

### Installation

```bash
# Clone repository
git clone https://github.com/asdthehiro/xss_hunter.git
cd xss_hunter

# Run setup (creates virtual environment automatically)
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Verify installation
python3 main.py --help
```

## Browser Configuration

### Firefox (Recommended for Kali)

Firefox is pre-installed on Kali Linux and is the **default browser** for XSS-Hunter.

**Why Firefox on Kali?**
- ✅ Pre-installed, no setup needed
- ✅ Native geckodriver support
- ✅ Better compatibility with Kali's security tools
- ✅ More reliable WebDriver
- ✅ Works out of the box

**No additional setup required!** Just run the tool and select Firefox.

### Chrome/Chromium (Alternative)

If you prefer Chrome, install it first:

```bash
# Option 1: Chromium (recommended for Kali)
sudo apt update
sudo apt install chromium chromium-driver

# Option 2: Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt --fix-broken install
```

## Running on Kali

```bash
# Activate virtual environment
source venv/bin/activate

# Run scanner
python3 main.py
```

### Browser Selection

When prompted:

```
[*] Select Browser:
    1. Firefox (Default for Kali Linux)
    2. Chrome/Chromium

Select browser (1 or 2) [1]:
```

- Press **Enter** or type **1** for Firefox (recommended)
- Type **2** for Chrome/Chromium

## Troubleshooting

### Issue: "Exec format error" with chromedriver

**Cause:** ChromeDriver incompatibility on Kali Linux

**Solution:** Use Firefox instead (default option)
```bash
# When prompted for browser, select option 1 (Firefox)
Select browser (1 or 2) [1]: 1
```

### Issue: Firefox not found

**Solution:** Firefox should be pre-installed, but if missing:
```bash
sudo apt update
sudo apt install firefox-esr
```

### Issue: Geckodriver error

**Solution:** Install geckodriver manually:
```bash
# Download latest geckodriver
wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz

# Extract
tar -xvzf geckodriver-v0.33.0-linux64.tar.gz

# Move to system path
sudo mv geckodriver /usr/local/bin/
sudo chmod +x /usr/local/bin/geckodriver

# Verify
geckodriver --version
```

### Issue: WebDriver not working

**Solution:** Reinstall Selenium and webdriver-manager:
```bash
source venv/bin/activate
pip install --upgrade selenium webdriver-manager
```

### Issue: Permission denied

**Solution:** Make sure Firefox can be launched:
```bash
# Test Firefox
firefox --version

# If permission issues
sudo chmod +x /usr/bin/firefox
```

### Issue: Display error (headless system)

If running on a headless Kali system (no GUI):

**Solution:** Install Xvfb for virtual display:
```bash
sudo apt install xvfb

# Run with virtual display
xvfb-run python3 main.py
```

Or modify the code to use headless mode (see Advanced Configuration below).

## Advanced Configuration

### Headless Mode (No GUI)

For servers or systems without a display, enable headless mode:

Edit `auth/login.py`:

**For Firefox:**
```python
firefox_options.add_argument('--headless')  # Uncomment this line
```

**For Chrome:**
```python
chrome_options.add_argument('--headless')  # Uncomment this line
```

**Note:** Headless mode may not work with all authentication systems, especially those with bot detection.

### System-wide Geckodriver

If webdriver-manager fails, use system geckodriver:

```bash
# Install via apt
sudo apt install firefox-geckodriver
```

The tool will automatically fall back to system geckodriver if webdriver-manager fails.

## Kali-Specific Tips

### Running as Root

If running as root (not recommended):
```bash
# Firefox may refuse to run as root
# Use this workaround:
export MOZ_FORCE_DISABLE_E10S=1
python3 main.py
```

### Firewall Configuration

Ensure outbound connections are allowed:
```bash
# Check if firewall is blocking
sudo iptables -L

# Allow outbound HTTP/HTTPS if needed
sudo iptables -A OUTPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT
```

### Proxy Configuration

If using Burp Suite or other proxy:

Set environment variables before running:
```bash
export HTTP_PROXY="http://127.0.0.1:8080"
export HTTPS_PROXY="http://127.0.0.1:8080"
python3 main.py
```

## Complete Example

```bash
# Start from home directory
cd ~

# Clone and setup
git clone https://github.com/asdthehiro/xss_hunter.git
cd xss_hunter
chmod +x setup.sh
./setup.sh

# Activate environment
source venv/bin/activate

# Run tool
python3 main.py

# Follow prompts:
Base URL: https://app.launchdarkly.com
Login URL: [Press Enter for default]
Authentication Method: 1 [Browser-based]
Select Browser: 1 [Firefox - Default]

# Firefox opens automatically
# Log in manually (including OTP if needed)
# Press Enter when logged in
# ✅ Session captured! Scanning begins...
```

## Verification

Test your setup:

```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check Firefox
firefox --version

# Check virtual environment
source venv/bin/activate
python3 -c "import selenium; print(selenium.__version__)"
python3 -c "from selenium import webdriver; print('Selenium OK')"

# Check geckodriver (optional)
geckodriver --version
```

## Performance Tips

### Optimize for Kali

```bash
# Disable unnecessary Firefox features for faster scanning
# Create Firefox profile with minimal features
firefox -CreateProfile "xss_hunter"

# Use this profile in the tool
# Edit auth/login.py and add:
firefox_options.add_argument('-profile')
firefox_options.add_argument('/path/to/profile')
```

### Resource Management

```bash
# Monitor resource usage
htop

# If system is slow, limit concurrent scans
# Edit main.py and reduce max_pages:
--max-pages 25  # Instead of default 50
```

## Common Workflows

### Standard Pentest

```bash
source venv/bin/activate
python3 main.py --crawl --output results.txt
```

### Quick Single-Page Test

```bash
source venv/bin/activate
python3 main.py --urls target.txt --output scan.txt
```

### Comprehensive Scan

```bash
source venv/bin/activate
python3 main.py --crawl --advanced --max-depth 3 --output full_scan.txt
```

## Support

If you encounter issues:

1. Check Firefox is working: `firefox --version`
2. Verify virtual environment: `source venv/bin/activate`
3. Test Selenium: `python3 -c "from selenium import webdriver; print('OK')"`
4. Use Firefox (option 1) instead of Chrome
5. Check [BROWSER_AUTH_GUIDE.md](BROWSER_AUTH_GUIDE.md) for authentication help
6. See [README.md](README.md) for general usage

## Why Firefox on Kali?

| Feature | Firefox on Kali | Chrome on Kali |
|---------|----------------|----------------|
| Pre-installed | ✅ Yes | ❌ No |
| Native support | ✅ Yes | ⚠️ Limited |
| WebDriver issues | ✅ Rare | ❌ Common |
| Security tools | ✅ Integrated | ⚠️ Basic |
| Setup needed | ✅ None | ❌ Manual install |
| Reliability | ✅ High | ⚠️ Medium |

**Recommendation:** Always use Firefox on Kali Linux unless you have a specific reason to use Chrome.
