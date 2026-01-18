# XSS-Hunter

**Author:** dark_hunter  
**Platform:** Kali Linux  
**Language:** Python 3 



## Description

Professional-grade authenticated XSS scanning tool designed to detect vulnerabilities that are only reachable after authentication.

## Features

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

```bash
pip install -r requirements.txt
```

## Usage

```bash
python3 main.py
```

### Options

- `--urls file.txt` - Manual scope file (one URL per line)
- `--crawl` - Enable authenticated crawling
- `--output results.txt` - Save results to file

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
developed by Eng: Poula