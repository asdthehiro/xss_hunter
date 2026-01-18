# XSS-Hunter Testing Guide

## Testing the Tool

### Test Against Vulnerable Apps

Before using XSS-Hunter on real targets, test it against known vulnerable applications:

#### 1. DVWA (Damn Vulnerable Web Application)
```bash
# Setup DVWA locally
docker run --rm -it -p 80:80 vulnerables/web-dvwa

# Test XSS-Hunter against it
python3 main.py
# Base URL: http://localhost
# Login URL: http://localhost/login.php
# Username: admin
# Password: password
```

#### 2. bWAPP (buggy Web Application)
```bash
# Setup bWAPP
docker run -d -p 8080:80 raesene/bwapp

# Test against: http://localhost:8080/bWAPP/
```

#### 3. OWASP WebGoat
```bash
# Run WebGoat
docker run -p 8080:8080 -p 9090:9090 webgoat/goatandwolf

# Test against: http://localhost:8080/WebGoat
```

## Architecture Overview

### Module Breakdown

```
xss-hunter/
├── auth/
│   └── login.py          # Handles authentication, session management
│
├── crawler/
│   └── crawler.py        # Discovers authenticated pages
│
├── scanner/
│   ├── payloads.py       # XSS payload definitions
│   ├── detector.py       # Response analysis & detection logic
│   └── scanner.py        # Core scanning engine
│
└── utils/
    ├── csrf.py           # CSRF token extraction
    ├── forms.py          # HTML form parsing
    ├── logger.py         # Output formatting
    └── helpers.py        # Utility functions
```

### Execution Flow

1. **Authentication Phase**
   - Fetch login page
   - Extract CSRF token
   - Parse login form
   - Submit credentials
   - Verify success (logout link, no login form, etc.)

2. **Scope Discovery Phase**
   - Option A: Load URLs from file
   - Option B: Authenticated crawling
   - Filter out logout URLs and static resources
   - Build target list

3. **Scanning Phase**
   - For each URL:
     - Test GET parameters
     - Parse forms
     - Test POST parameters
   - For each parameter:
     - Inject payloads
     - Analyze response
     - Detect reflection
     - Determine context
     - Classify vulnerability

4. **Reporting Phase**
   - Display findings
   - Generate summary
   - Save to file (optional)

## Detection Logic

### How XSS Detection Works

1. **Reflection Check**
   - Does payload appear in response?
   - Is it HTML-encoded?

2. **Context Detection**
   - Tag context: `<div>PAYLOAD</div>`
   - Attribute context: `<input value="PAYLOAD">`
   - Script context: `<script>var x = "PAYLOAD";</script>`
   - Comment context: `<!-- PAYLOAD -->`

3. **Executability Check**
   - Are dangerous tags intact? (`<script>`, `<img>`, etc.)
   - Are event handlers present? (`onerror`, `onload`, etc.)
   - Can we break out of current context?

4. **Classification**
   - Reflected XSS: Immediate response
   - Stored XSS: Persists on re-fetch
   - DOM XSS: JavaScript-based (basic detection)

## Extending the Tool

### Adding New Payloads

Edit [scanner/payloads.py](scanner/payloads.py):

```python
class XSSPayloads:
    CUSTOM = [
        '<custom>payload1</custom>',
        '<custom>payload2</custom>',
    ]
    
    @classmethod
    def get_all_payloads(cls):
        all_payloads = (
            cls.BASIC +
            cls.CUSTOM +  # Add your payloads
            # ...
        )
        return unique_payloads
```

### Custom Detection Logic

Edit [scanner/detector.py](scanner/detector.py):

```python
@staticmethod
def custom_detection(response_text: str, payload: str) -> bool:
    """Add custom detection logic"""
    # Your logic here
    return detected
```

### Adding Report Formats

Edit [utils/logger.py](utils/logger.py):

```python
def export_json(self, vulnerabilities):
    """Export findings as JSON"""
    import json
    # Implementation
```

## Performance Optimization

### Current Rate Limiting

- 0.5 seconds between pages (crawling)
- 0.2 seconds between payloads
- 0.3 seconds between URLs

### Optimization Tips

1. **Reduce Payloads**
   - Use basic payloads for initial scan
   - Target specific contexts
   - Remove duplicates

2. **Smart Crawling**
   - Limit depth and page count
   - Skip static resources
   - Cache responses

3. **Parallel Scanning**
   - Use threading (not implemented)
   - Test multiple parameters simultaneously
   - Balance speed vs. detection accuracy

## Security Considerations

### Built-in Safety Features

1. **No Destructive Payloads**
   - All payloads use `alert(1)`
   - No data deletion
   - No account modification

2. **Logout Detection**
   - Automatically skips logout URLs
   - Prevents accidental logouts

3. **Rate Limiting**
   - Prevents server overload
   - Reduces detection risk

4. **Session Management**
   - Maintains valid authentication
   - Handles CSRF tokens properly

### Responsible Use

```python
# GOOD: Testing authorized target
python3 main.py
# Enter legitimate test credentials

# BAD: Testing without permission
# DON'T DO THIS!
```

## Debugging

### Enable Verbose Logging

Modify [utils/logger.py](utils/logger.py) to add debug level:

```python
def debug(self, message: str):
    """Debug message"""
    if self.debug_mode:
        self._log(f"[DEBUG] {message}", Colors.OKCYAN)
```

### Common Issues

1. **Authentication Fails**
   - Add debug prints in `auth/login.py`
   - Check CSRF extraction
   - Verify form parsing

2. **No XSS Found**
   - Check if payloads are reaching target
   - Verify reflection detection
   - Review response encoding

3. **False Positives**
   - Improve context detection
   - Add encoding checks
   - Manual verification step

## Code Quality

### Current Standards

- ✅ Type hints
- ✅ Docstrings
- ✅ Modular design
- ✅ Error handling
- ✅ Clean separation of concerns

### Future Improvements

1. **Testing**
   - Unit tests for each module
   - Integration tests
   - Test with mock responses

2. **Documentation**
   - API documentation
   - Architecture diagrams
   - Video tutorials

3. **Features**
   - DOM XSS engine (dynamic analysis)
   - Blind XSS detection
   - WebSocket support
   - Multi-threaded scanning

## Contributing

To contribute improvements:

1. **Code Style**
   - Follow PEP 8
   - Add type hints
   - Write docstrings
   - Handle errors gracefully

2. **Testing**
   - Test against DVWA
   - Verify no false positives
   - Check edge cases

3. **Documentation**
   - Update README
   - Add usage examples
   - Document new features

## Performance Benchmarks

Typical performance on test system:

- Authentication: 2-3 seconds
- Crawling (50 pages, depth 2): 30-60 seconds
- Scanning (10 URLs, 15 payloads): 2-5 minutes
- Total scan time: 3-7 minutes (varies by target)

## Legal & Ethical Framework

### Before You Scan

- [ ] Written authorization obtained
- [ ] Scope clearly defined
- [ ] Contact information confirmed
- [ ] Disclosure process understood
- [ ] Legal implications reviewed

### During Scanning

- [ ] Stay within defined scope
- [ ] Monitor for errors/issues
- [ ] Stop if problems occur
- [ ] Document findings properly
- [ ] Avoid production disruption

### After Scanning

- [ ] Report vulnerabilities responsibly
- [ ] Follow disclosure timeline
- [ ] Provide clear reproduction steps
- [ ] Suggest remediation
- [ ] Maintain confidentiality

## Resources

### Learn More About XSS

- OWASP XSS Guide: https://owasp.org/www-community/attacks/xss/
- PortSwigger Web Security Academy: https://portswigger.net/web-security/cross-site-scripting
- HackerOne Reports: https://www.hackerone.com/

### Similar Tools

- Burp Suite (Commercial)
- OWASP ZAP (Free)
- XSStrike (Python)
- Dalfox (Go)

### Bug Bounty Platforms

- HackerOne: https://www.hackerone.com/
- Bugcrowd: https://www.bugcrowd.com/
- Intigriti: https://www.intigriti.com/
- YesWeHack: https://www.yeswehack.com/

---

**Remember: With great power comes great responsibility. Use this tool ethically and legally.**
