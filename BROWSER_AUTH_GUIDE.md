# Browser-Based Authentication Guide

## Overview

XSS-Hunter now supports browser-based manual authentication, solving the common problems with automated login systems.

## Why Browser-Based Authentication?

### Problems with Automated Login:
- ❌ Multi-step authentication (email → password)
- ❌ OTP/2FA verification
- ❌ CAPTCHA challenges
- ❌ Social login (Google, Facebook, etc.)
- ❌ Complex JavaScript validation
- ❌ Single-page application forms
- ❌ 405 Method Not Allowed errors

### Browser-Based Solution:
- ✅ You log in manually in a real browser
- ✅ Complete any verification steps naturally
- ✅ Tool captures your authenticated session
- ✅ Works with ANY authentication system
- ✅ No form parsing needed
- ✅ No credential detection required

## How to Use

### 1. Start the Scanner

```bash
source venv/bin/activate
python3 main.py
```

### 2. Enter Target Information

```
Base URL (e.g., https://example.com): https://app.launchdarkly.com
Login URL (press Enter to use base URL + /login): https://app.launchdarkly.com/login
```

### 3. Select Authentication Method

```
[*] Authentication Method:
    1. Browser-based manual login (Recommended for complex flows, OTP, 2FA)
    2. Automated login (Simple username/password forms only)

Select authentication method (1 or 2) [1]: 1
```

### 4. Select Browser

```
[*] Select Browser:
    1. Firefox (Default for Kali Linux)
    2. Chrome/Chromium

Select browser (1 or 2) [1]: 1
```

**Recommendation:** Use Firefox (option 1) on Kali Linux - it's pre-installed and most reliable.

### 5. Browser Opens Automatically

- Firefox (or Chrome) will launch
- You'll see the login page
- Log in as you normally would

### 6. Complete Your Login

- Enter email/username
- Enter password
- Complete OTP/2FA if required
- Solve any CAPTCHA
- Complete any verification steps

### 7. Confirm Authentication

When you're successfully logged in:

```
[?] Have you successfully logged in? (Press Enter to continue, 'n' to wait):
```

Press **Enter** to continue, or type **n** to wait longer.

### 7. Session Captured

```
[+] Session captured successfully! 15 cookies transferred
[+] Authentication successful!
```

The browser closes automatically and scanning begins with your authenticated session.

## Examples

### Example 1: LaunchDarkly (Multi-step with OTP)

```bash
Base URL: https://app.launchdarkly.com
Login URL: https://app.launchdarkly.com/login

1. Browser opens
2. Enter email → Click Continue
3. Enter password → Click Sign In
4. Enter OTP code from authenticator
5. Press Enter in terminal
6. ✅ Session captured!
```

### Example 2: AWS Console (Multi-account)

```bash
Base URL: https://console.aws.amazon.com
Login URL: https://signin.aws.amazon.com

1. Browser opens
2. Select account
3. Enter username
4. Enter password
5. Complete MFA
6. Press Enter in terminal
7. ✅ Session captured!
```

### Example 3: Google Workspace

```bash
Base URL: https://workspace.google.com
Login URL: https://accounts.google.com

1. Browser opens
2. Enter email → Next
3. Enter password → Next
4. Complete 2FA verification
5. Press Enter in terminal
6. ✅ Session captured!
```

## Troubleshooting

### Browser doesn't open

**On Kali Linux:**
```bash
# Firefox should be pre-installed
firefox --version

# If not, install it:
sudo apt update
sudo apt install firefox-esr
```

**For Chrome users:**
```bash
# Install Chrome/Chromium
sudo apt update
sudo apt install chromium-browser

# Or Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt --fix-broken install
```

### ChromeDriver "Exec format error" on Kali

**Solution:** Use Firefox instead!
```
Select browser (1 or 2) [1]: 1
```

Firefox is the default browser on Kali and works more reliably.

### WebDriver error

**Solution:**
```bash
# Reinstall selenium and webdriver-manager
source venv/bin/activate
pip install --upgrade selenium webdriver-manager
```

### Session not captured

**Solution:**
- Make sure you're fully logged in before pressing Enter
- Check that you can see authenticated content (dashboard, profile, etc.)
- Wait a few seconds after logging in
- Type 'n' and wait longer if needed

### Browser closes immediately

**Solution:**
- Don't close the browser manually
- Let the tool close it automatically after session capture
- If it closes too early, the timeout may be too short

## Technical Details

### What Gets Captured?

- All session cookies
- Authentication tokens
- CSRF tokens (if present)
- Domain cookies
- Path-specific cookies

### Session Transfer

Cookies are transferred from Selenium WebDriver to the requests.Session object:
- Cookie name
- Cookie value
- Domain
- Path
- Expiry (if set)

### Security

- Credentials are NOT stored
- Cookies are only in memory
- No data sent to external servers
- Browser runs locally on your machine

## Advanced Tips

### Extending Timeout

The default timeout is 5 minutes. Modify in code if needed:

```python
timeout = 300  # 5 minutes - change this value
```

### Headless Mode

To hide the browser (advanced users):

Uncomment in `auth/login.py`:
```python
chrome_options.add_argument('--headless')
```

Note: Headless mode may not work with all authentication systems.

## Comparison

| Feature | Browser Auth | Automated Auth |
|---------|-------------|----------------|
| Multi-step login | ✅ | ❌ |
| OTP/2FA | ✅ | ❌ |
| CAPTCHA | ✅ | ❌ |
| Social login | ✅ | ❌ |
| SPA forms | ✅ | ⚠️ |
| Simple forms | ✅ | ✅ |
| Speed | Slower | Faster |
| Reliability | Very High | Low-Medium |

## When to Use Automated Auth

Only use automated authentication if:
- Login is a simple HTML form
- No JavaScript validation
- No multi-step process
- No OTP/2FA/CAPTCHA
- You've tested it successfully

For everything else, use browser-based authentication.
