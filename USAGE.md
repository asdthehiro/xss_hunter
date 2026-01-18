# XSS-Hunter Usage Guide

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or use the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Run the scanner:**
   ```bash
   python3 main.py
   ```

3. **Follow the prompts:**
   - Enter target base URL
   - Enter login URL
   - Provide credentials
   - Confirm authorization

## Advanced Usage

### Manual URL List

Test specific URLs from a file:
```bash
python3 main.py --urls targets.txt --output results.txt
```

### Authenticated Crawling

Enable automatic discovery of authenticated pages:
```bash
python3 main.py --crawl
```

### Advanced Payloads

Use comprehensive payload set (slower but more thorough):
```bash
python3 main.py --crawl --advanced
```

### Custom Crawl Settings

Control crawling depth and scope:
```bash
python3 main.py --crawl --max-depth 3 --max-pages 100
```

### Complete Example

```bash
python3 main.py \
  --urls my_urls.txt \
  --crawl \
  --advanced \
  --max-depth 2 \
  --max-pages 50 \
  --output vulnerability_report.txt
```

## URL File Format

Create a text file with one URL per line:
```
https://example.com/dashboard
https://example.com/profile
https://example.com/search?q=test
# Comments start with #
```

## Understanding Results

### Reflected XSS (GET)
- Payload reflected in immediate response
- URL-based injection
- Example: `https://site.com/search?q=<script>alert(1)</script>`

### Reflected XSS (POST)
- Payload reflected after form submission
- Form-based injection
- More difficult to exploit than GET

### Stored XSS
- Payload persists across requests
- Most dangerous type
- Affects multiple users

## Tips for Effective Scanning

1. **Test Authorized Targets Only**
   - Obtain written permission
   - Follow responsible disclosure
   - Stay within scope

2. **Start Small**
   - Begin with basic payloads
   - Test known vulnerable apps first
   - Gradually increase coverage

3. **Review Results Manually**
   - Verify each finding
   - Check false positives
   - Understand the context

4. **Use Authenticated Crawling**
   - Discovers hidden endpoints
   - Tests post-login functionality
   - More comprehensive coverage

5. **Combine with Manual Testing**
   - Automated tools miss edge cases
   - Test complex workflows manually
   - Understand application logic

## Common Issues

### Authentication Fails
- Check credentials
- Verify login URL
- Check for CAPTCHA
- Look for rate limiting

### No Vulnerabilities Found
- Try advanced payloads
- Check scope coverage
- Verify authentication still valid
- Review application security

### False Positives
- Payload reflected but encoded
- Context prevents execution
- Manual verification needed

## Safety Features

XSS-Hunter includes several safety mechanisms:
- No destructive payloads
- Respects logout URLs
- Rate limiting between requests
- Session validation
- CSRF token handling

## Ethical Considerations

✅ **DO:**
- Get written authorization
- Test only in-scope targets
- Report vulnerabilities responsibly
- Follow disclosure timelines

❌ **DON'T:**
- Test without permission
- Use on production systems (without approval)
- Share vulnerabilities publicly before disclosure
- Use for malicious purposes

## Bug Bounty Programs

This tool is designed for:
- HackerOne programs
- Bugcrowd programs
- Private pentests
- Security research

Always read and follow program rules!

## Support

For issues or questions:
1. Check the README.md
2. Review this usage guide
3. Verify your Python environment
4. Check target authentication

## Example Session

```
$ python3 main.py --crawl

╔═══════════════════════════════════════════════════════════╗
║                      XSS-HUNTER                          ║
║           Authenticated XSS Scanner v1.0                 ║
║                  Author: dark_hunter                     ║
╚═══════════════════════════════════════════════════════════╝

⚠️  ETHICAL USE WARNING ⚠️
[...]

Do you have authorization to test this target? (yes/no): yes

[*] XSS-Hunter requires the following information:

Base URL (e.g., https://example.com): https://testsite.com
Login URL (press Enter to use base URL + /login): 
Username: testuser
Password: 
[*] ============================================================
[*] STEP 1: AUTHENTICATION
[*] ============================================================
[*] Attempting authentication at https://testsite.com/login
[*] Fetching login page...
[+] CSRF token extracted: abc123...
[*] Submitting credentials to https://testsite.com/login
[+] Authentication successful!

[*] ============================================================
[*] STEP 2: SCOPE DISCOVERY
[*] ============================================================
[*] Starting authenticated crawling...
[...]

[*] ============================================================
[*] STEP 3: XSS SCANNING
[*] ============================================================
[*] Starting XSS scan on 15 URLs
[...]

[+] XSS FOUND
URL: https://testsite.com/profile
Method: POST
Parameter: bio
Payload: <script>alert(1)</script>
Type: Stored XSS
Context: tag
============================================================

[*] Scan completed successfully!
```
