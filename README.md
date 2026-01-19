# XSS-Hunter

**Author:** dark_hunter  
**Platform:** Kali Linux  
**Language:** Python 3 



## Description

Professional-grade authenticated XSS scanning tool designed to detect vulnerabilities that are only reachable after authentication.

## Features

- ✅ **Browser-based authentication** - Manual login support for complex flows
- ✅ **Multi-step login support** - Handles email-first, password-second flows
- ✅ **OTP/2FA compatible** - Complete verification in browser
- ✅ **Session capture** - Automatically transfers cookies to scanner
- ✅ Authenticated session handling
- ✅ CSRF token extraction and bypass
- ✅ GET & POST parameter testing
- ✅ Reflected XSS detection
- ✅ Stored XSS detection
- ✅ Basic DOM XSS detection
- ✅ Authenticated crawling
- ✅ Manual scope control
- ✅ Professional output formatting

## Installation

### Prerequisites

- Python 3.8 or higher
- pip3
- git
- Google Chrome or Chromium browser
- Linux/Unix-based system (Tested on Kali Linux)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/asdthehiro/xss_hunter.git
   cd xss_hunter
   ```

2. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   The setup script will automatically:
   - Create a Python virtual environment
   - Install all dependencies
   - Display activation instructions

3. **Activate the virtual environment**
   ```bash
   source venv/bin/activate
   ```

4. **Verify installation**
   ```bash
   python3 main.py --help
   ```

#### Manual Setup (Alternative)

If you prefer to set up manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Deactivating Virtual Environment

When finished, deactivate the environment:
```bash
deactivate
```

## Quick Start

1. **Activate the virtual environment** (if not already active):
   ```bash
   source venv/bin/activate
   ```

2. **Run the interactive quickstart guide**:
   ```bash
   python3 quickstart.py
   ```

   This will walk you through:
   - Authentication setup
   - Target URL configuration
   - Basic scanning options
   - Output configuration

## Usage

### Activate Virtual Environment

Before running any commands, activate the virtual environment:
```bash
source venv/bin/activate
```

You'll see `(venv)` prefix in your terminal when activated.

### Basic Usage

```bash
python3 main.py
```

The tool will prompt you for:
- Target URL
- Login URL
- **Authentication method selection:**
  - **Option 1 (Recommended):** Browser-based manual login
    - Opens Chrome browser
    - You manually complete the login (including OTP, 2FA, multi-step)
    - Session cookies are automatically captured
    - Works with complex authentication flows
  - **Option 2:** Automated login (simple forms only)
    - Requires username and password
    - Only works with basic login forms
    - May fail with complex authentication

### Authentication Methods

#### Browser-Based Login (Recommended)

Perfect for:
- Multi-step authentication (email first, then password)
- OTP/2FA verification
- CAPTCHA challenges
- Social login redirects
- Complex JavaScript-based login forms

**How it works:**
1. Tool opens Chrome browser
2. You manually log in as you normally would
3. Complete any verification (OTP, 2FA, etc.)
4. Press Enter when logged in
5. Tool captures your session automatically

#### Automated Login

Only use for:
- Simple username/password forms
- No JavaScript validation
- No multi-step process
- No OTP/2FA

**Limitations:**
- Cannot handle OTP/2FA
- May fail with single-page applications
- Cannot handle CAPTCHA

### Advanced Usage

#### Scan with URL List
```bash
python3 main.py --urls example_urls.txt
```

#### Enable Authenticated Crawling
```bash
python3 main.py --crawl
```

#### Save Results to File
```bash
python3 main.py --output results.txt
```

#### Combined Options
```bash
python3 main.py --urls targets.txt --crawl --output scan_results.txt
```

### Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--urls <file>` | Specify a file containing URLs to scan (one per line) | `--urls targets.txt` |
| `--crawl` | Enable authenticated crawling to discover additional endpoints | `--crawl` |
| `--output <file>` | Save scan results to specified file | `--output results.txt` |

### Example Workflow

1. **Prepare your target list**
   ```bash
   cat > my_targets.txt << EOF
   https://example.com/profile
   https://example.com/settings
   https://example.com/dashboard
   EOF
   ```

2. **Run the scanner**
   ```bash
   python3 main.py --urls my_targets.txt --crawl --output results.txt
   ```

3. **Review results**
   ```bash
   cat results.txt
   ```

### URL List Format

Create a text file with one URL per line:
```
https://example.com/page1
https://example.com/page2?param=value
https://example.com/page3
```

See [example_urls.txt](example_urls.txt) for reference.

## Ethical Use

⚠️ **WARNING:** This tool is for authorized testing only. Ensure you have explicit permission before testing any application.

- No destructive payloads
- No account lockouts
- No data deletion
- Use responsibly

## Architecture

```
xss-hunter/
├── main.py                 # CLI entry point
├── auth/                   # Authentication module
│   └── login.py
├── crawler/                # Authenticated crawling
│   └── crawler.py
├── scanner/                # XSS detection engine
│   ├── payloads.py
│   ├── detector.py
│   └── scanner.py
└── utils/                  # Helper functions
    ├── csrf.py
    ├── forms.py
    ├── logger.py
    └── helpers.py
```

## License

For educational and authorized security testing purposes only.

developed with love by Eng:Poula