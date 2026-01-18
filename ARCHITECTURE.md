# XSS-Hunter Project Structure

```
xss_checker/
│
├── main.py                     # CLI entry point - orchestrates the entire scan
│
├── auth/                       # Authentication module
│   ├── __init__.py
│   └── login.py               # Session management, login handling, CSRF support
│
├── crawler/                    # Authenticated crawling module
│   ├── __init__.py
│   └── crawler.py             # Discover authenticated pages automatically
│
├── scanner/                    # XSS detection engine
│   ├── __init__.py
│   ├── payloads.py            # XSS payload definitions (basic, advanced, polyglot)
│   ├── detector.py            # Response analysis & vulnerability detection
│   └── scanner.py             # Core scanning logic (GET/POST parameter testing)
│
├── utils/                      # Helper utilities
│   ├── __init__.py
│   ├── csrf.py                # CSRF token extraction from multiple sources
│   ├── forms.py               # HTML form parsing and analysis
│   ├── helpers.py             # URL manipulation, validation utilities
│   └── logger.py              # Professional output formatting with colors
│
├── requirements.txt            # Python dependencies
├── setup.sh                    # Quick setup script
│
├── README.md                   # Project overview and features
├── USAGE.md                    # Detailed usage instructions
├── TESTING.md                  # Testing guide and architecture details
└── example_urls.txt            # Sample URL file format

```

## Module Descriptions

### main.py
- Entry point for the application
- Argument parsing
- User input collection
- Orchestrates authentication → crawling → scanning → reporting
- Error handling and graceful exit

### auth/login.py
- Authenticates users via login forms
- Maintains authenticated session
- Extracts and handles CSRF tokens
- Validates successful authentication
- Session validity checking

### crawler/crawler.py
- Authenticated web crawling
- Link extraction and filtering
- Depth-limited traversal
- Domain restriction
- Logout URL detection and avoidance

### scanner/payloads.py
- Comprehensive XSS payload collection
- Basic payloads for quick testing
- Advanced payloads for thorough scanning
- Context-aware payload generation
- Polyglot payloads for multiple contexts

### scanner/detector.py
- Reflection detection
- Context analysis (tag, attribute, script)
- HTML encoding detection
- Executability verification
- XSS type classification

### scanner/scanner.py
- Core scanning engine
- GET parameter testing
- POST form testing
- Payload injection
- Stored XSS verification
- Vulnerability reporting

### utils/csrf.py
- Extract CSRF tokens from:
  - Hidden input fields
  - Meta tags
  - JavaScript variables
  - Cookies
- Form-specific CSRF handling

### utils/forms.py
- Parse HTML forms
- Extract input fields
- Identify form types (login, search, etc.)
- Link extraction
- Authentication state detection

### utils/helpers.py
- URL normalization and validation
- Domain comparison
- URL parameter manipulation
- Static resource detection
- Logout URL detection

### utils/logger.py
- Colored terminal output
- Structured vulnerability reporting
- Scan summary generation
- File output support
- Professional formatting

## File Sizes

```
main.py              ~350 lines
auth/login.py        ~250 lines
crawler/crawler.py   ~150 lines
scanner/payloads.py  ~150 lines
scanner/detector.py  ~250 lines
scanner/scanner.py   ~300 lines
utils/csrf.py        ~100 lines
utils/forms.py       ~200 lines
utils/helpers.py     ~150 lines
utils/logger.py      ~150 lines
```

## Total Lines of Code

**~2,050 lines** of professional, production-ready Python code

## Dependencies

- `requests` - HTTP client
- `beautifulsoup4` - HTML parsing
- `urllib3` - URL utilities
- `lxml` - XML/HTML parser

All standard, well-maintained libraries.

## Key Features Implementation

✅ **Authenticated Session Handling** - auth/login.py
✅ **CSRF Token Support** - utils/csrf.py
✅ **GET Parameter Testing** - scanner/scanner.py
✅ **POST Parameter Testing** - scanner/scanner.py
✅ **Reflected XSS Detection** - scanner/detector.py
✅ **Stored XSS Detection** - scanner/scanner.py
✅ **Basic DOM XSS Detection** - scanner/detector.py
✅ **Authenticated Crawling** - crawler/crawler.py
✅ **Manual Scope Control** - main.py
✅ **Professional Output** - utils/logger.py
✅ **Safety Features** - Throughout all modules

## Design Principles

1. **Modularity** - Each component has a single responsibility
2. **Extensibility** - Easy to add new payloads, detectors, or features
3. **Maintainability** - Clean code, type hints, comprehensive docstrings
4. **Safety** - No destructive operations, rate limiting, logout detection
5. **Professionalism** - Production-ready code quality

## Testing Against

Recommended vulnerable applications for testing:
- DVWA (Damn Vulnerable Web Application)
- bWAPP (buggy Web Application)
- OWASP WebGoat
- Juice Shop

**Never test against unauthorized targets!**
