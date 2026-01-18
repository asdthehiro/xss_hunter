#!/usr/bin/env python3
"""
XSS-Hunter - Quick Test Script
Test the tool against a local vulnerable application
"""
import sys

print("""
╔═══════════════════════════════════════════════════════════╗
║              XSS-Hunter Quick Test                       ║
╚═══════════════════════════════════════════════════════════╝

This script helps you test XSS-Hunter against vulnerable apps.

STEP 1: Setup a Vulnerable Application
---------------------------------------

Option A: DVWA (Recommended)
  docker run --rm -it -p 80:80 vulnerables/web-dvwa
  
  Then access: http://localhost
  Default credentials:
    Username: admin
    Password: password
  
  Set security level to LOW in DVWA settings.

Option B: bWAPP
  docker run -d -p 8080:80 raesene/bwapp
  
  Then access: http://localhost:8080/bWAPP/
  Default credentials:
    Username: bee
    Password: bug

Option C: OWASP Juice Shop (for testing only)
  docker run -d -p 3000:3000 bkimminich/juice-shop
  
  Then access: http://localhost:3000


STEP 2: Run XSS-Hunter
----------------------

Basic scan:
  python3 main.py

With crawling:
  python3 main.py --crawl

With advanced payloads:
  python3 main.py --crawl --advanced

Save results:
  python3 main.py --output results.txt


STEP 3: Test Scenarios
-----------------------

1. Test Reflected XSS (GET):
   - Navigate to search page
   - XSS-Hunter should find GET parameter vulnerabilities

2. Test Reflected XSS (POST):
   - Navigate to forms (contact, feedback)
   - XSS-Hunter should find POST parameter vulnerabilities

3. Test Stored XSS:
   - Navigate to profile/comment sections
   - XSS-Hunter should detect persistent payloads


STEP 4: Verify Results
-----------------------

Check the output for:
  [+] XSS FOUND
  URL: ...
  Method: GET/POST
  Parameter: ...
  Payload: ...
  Type: Reflected/Stored XSS

Manual verification:
  1. Copy the URL with payload
  2. Open in browser
  3. Check if alert() fires


SAFETY REMINDERS
----------------
⚠️  Only test on:
  ✓ Local vulnerable apps
  ✓ Authorized targets
  ✓ Bug bounty programs (with permission)

✗ NEVER test on:
  ✗ Production systems without approval
  ✗ Sites you don't own
  ✗ Without written authorization


TROUBLESHOOTING
---------------

Authentication fails:
  → Check credentials
  → Verify login URL
  → Look for CAPTCHA

No XSS found:
  → Try --advanced flag
  → Verify target is actually vulnerable
  → Check security settings (set to LOW in DVWA)

Tool crashes:
  → Check Python version (3.10+)
  → Verify dependencies installed
  → Run: pip install -r requirements.txt


QUICK COMMANDS
--------------

Install dependencies:
  pip install -r requirements.txt

Run basic scan:
  python3 main.py

Full scan with all features:
  python3 main.py --crawl --advanced --output results.txt

Get help:
  python3 main.py --help


EXPECTED RESULTS (DVWA on LOW security)
----------------------------------------

You should find XSS in:
  ✓ XSS (Reflected) page
  ✓ XSS (Stored) page
  
Sample finding:
  [+] XSS FOUND
  URL: http://localhost/vulnerabilities/xss_r/?name=<script>alert(1)</script>
  Method: GET
  Parameter: name
  Payload: <script>alert(1)</script>
  Type: Reflected XSS (GET)
  Context: tag


NEXT STEPS
----------

1. Practice on vulnerable apps
2. Read USAGE.md for advanced features
3. Check TESTING.md for architecture details
4. Join bug bounty platforms when ready
5. Always follow responsible disclosure


Happy (ethical) hunting! 🎯
═══════════════════════════════════════════════════════════

""")

if __name__ == "__main__":
    response = input("Press Enter to continue or Ctrl+C to exit...")
    print("\nTo start scanning, run: python3 main.py\n")
