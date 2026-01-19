"""
Authentication Module - Handle login and session management with browser support
"""
import os
import time
from typing import Optional, Dict, Tuple

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from utils.csrf import extract_csrf_token, extract_csrf_from_form
from utils.forms import parse_forms, is_login_form, has_logout_indicator


class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass


class Authenticator:
    """Handles authentication and session management with browser support"""
    
    def __init__(self, login_url: str, username: str = "", password: str = "", 
                 base_url: str = "", logger=None, use_browser: bool = True, 
                 browser_choice: str = "firefox"):
        """
        Initialize authenticator
        
        Args:
            login_url: URL of the login page
            username: Username for authentication (optional for browser mode)
            password: Password for authentication (optional for browser mode)
            base_url: Base URL of the target application
            logger: Logger instance for output
            use_browser: Whether to use browser-based manual login
            browser_choice: Browser to use ('firefox', 'chrome')
        """
        self.login_url = login_url
        self.username = username
        self.password = password
        self.base_url = base_url or login_url
        self.logger = logger
        self.use_browser = use_browser
        self.browser_choice = browser_choice.lower()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.csrf_token = None
        self.csrf_field_name = 'csrf_token'
    
    def _log(self, level: str, message: str):
        """Internal logging helper"""
        if self.logger:
            if level == "info":
                self.logger.info(message)
            elif level == "success":
                self.logger.success(message)
            elif level == "error":
                self.logger.error(message)
            elif level == "warning":
                self.logger.warning(message)
    
    def authenticate(self) -> requests.Session:
        """
        Perform authentication and return authenticated session
        Uses browser-based manual login for complex authentication flows
        
        Returns:
            Authenticated requests.Session object
        
        Raises:
            AuthenticationError: If authentication fails
        """
        if self.use_browser:
            return self._browser_authenticate()
        else:
            return self._automated_authenticate()
    
    def _browser_authenticate(self) -> requests.Session:
        """
        Open browser for manual login and capture session cookies
        Handles complex authentication: multi-step, OTP, 2FA, etc.
        """
        self._log("info", "Opening browser for manual authentication...")
        self._log("info", "Please complete the login process in the browser window")
        self._log("info", "The browser will close automatically once you're logged in")
        
        driver = None
        try:
            # Initialize WebDriver based on browser choice
            if self.browser_choice == "firefox":
                self._log("info", "Initializing Firefox WebDriver...")
                firefox_options = FirefoxOptions()
                firefox_options.set_preference('dom.webdriver.enabled', False)
                firefox_options.set_preference('useAutomationExtension', False)

                # Try system driver first (env override supported)
                gecko_path = os.environ.get("GECKODRIVER_PATH")
                try:
                    if gecko_path:
                        self._log("info", f"Using geckodriver at {gecko_path}")
                        service = FirefoxService(executable_path=gecko_path)
                        driver = webdriver.Firefox(service=service, options=firefox_options)
                    else:
                        driver = webdriver.Firefox(options=firefox_options)
                except Exception as sys_err:
                    self._log("warning", f"System geckodriver failed: {sys_err}")
                    try:
                        os.environ.setdefault("WDM_ARCH", "arm64")
                        service = FirefoxService(GeckoDriverManager().install())
                        driver = webdriver.Firefox(service=service, options=firefox_options)
                    except Exception as mgr_err:
                        raise AuthenticationError(f"Unable to start Firefox WebDriver: {mgr_err}")

            elif self.browser_choice == "chrome":
                self._log("info", "Initializing Chrome WebDriver...")
                chrome_options = ChromeOptions()
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
                chrome_options.add_experimental_option('useAutomationExtension', False)

                chrome_path = os.environ.get("CHROMEDRIVER_PATH")
                try:
                    if chrome_path:
                        self._log("info", f"Using chromedriver at {chrome_path}")
                        service = ChromeService(executable_path=chrome_path)
                        driver = webdriver.Chrome(service=service, options=chrome_options)
                    else:
                        driver = webdriver.Chrome(options=chrome_options)
                except Exception as sys_err:
                    self._log("warning", f"System chromedriver failed: {sys_err}")
                    try:
                        os.environ.setdefault("WDM_ARCH", "arm64")
                        service = ChromeService(ChromeDriverManager().install())
                        driver = webdriver.Chrome(service=service, options=chrome_options)
                    except Exception as mgr_err:
                        raise AuthenticationError(f"Unable to start Chrome WebDriver: {mgr_err}")
            
            else:
                raise AuthenticationError(f"Unsupported browser: {self.browser_choice}")
            
            # Navigate to login page
            self._log("info", f"Navigating to: {self.login_url}")
            driver.get(self.login_url)
            
            # Wait for user to complete login
            self._log("info", "Waiting for you to complete login...")
            self._log("warning", "Press Enter here after you've successfully logged in")
            
            # Monitor for successful authentication
            authenticated = False
            start_time = time.time()
            timeout = 300  # 5 minutes timeout
            
            while not authenticated and (time.time() - start_time) < timeout:
                try:
                    # Check if URL changed from login page
                    current_url = driver.current_url.lower()
                    
                    # Check for authentication indicators
                    if 'login' not in current_url or self._check_browser_auth(driver):
                        # Prompt user to confirm
                        user_input = input("\n[?] Have you successfully logged in? (Press Enter to continue, 'n' to wait): ").strip().lower()
                        
                        if user_input != 'n':
                            authenticated = True
                            break
                    
                    time.sleep(1)
                except Exception as e:
                    time.sleep(1)
            
            if not authenticated:
                raise AuthenticationError("Authentication timeout - please try again")
            
            # Extract cookies from browser
            self._log("info", "Extracting session cookies from browser...")
            cookies = driver.get_cookies()
            
            # Transfer cookies to requests session
            for cookie in cookies:
                self.session.cookies.set(
                    cookie['name'],
                    cookie['value'],
                    domain=cookie.get('domain', ''),
                    path=cookie.get('path', '/')
                )
            
            # Verify session
            self._log("info", "Verifying captured session...")
            test_response = self.session.get(driver.current_url, timeout=10)
            
            if test_response.status_code == 200:
                self._log("success", f"Session captured successfully! {len(cookies)} cookies transferred")
                return self.session
            else:
                raise AuthenticationError(f"Session verification failed (Status: {test_response.status_code})")
        
        except Exception as e:
            raise AuthenticationError(f"Browser authentication failed: {str(e)}")
        
        finally:
            if driver:
                self._log("info", "Closing browser...")
                driver.quit()
    
    def _check_browser_auth(self, driver) -> bool:
        """Check if browser shows authentication indicators"""
        try:
            page_source = driver.page_source.lower()
            return any(indicator in page_source for indicator in [
                'logout', 'sign out', 'dashboard', 'profile', 'account'
            ])
        except:
            return False
    
    def _automated_authenticate(self) -> requests.Session:
        """
        Automated authentication (legacy method)
        Use browser-based authentication for complex flows
        """
        self._log("info", f"Attempting automated authentication at {self.login_url}")
        
        try:
            # Step 1: Get login page to extract CSRF token and cookies
            self._log("info", "Fetching login page...")
            response = self.session.get(self.login_url, timeout=10, allow_redirects=True)
            
            if response.status_code != 200:
                raise AuthenticationError(f"Failed to fetch login page (Status: {response.status_code})")
            
            # Step 2: Extract CSRF token
            self.csrf_token = extract_csrf_token(
                response.text, 
                self.session.cookies.get_dict()
            )
            
            if self.csrf_token:
                self._log("success", f"CSRF token extracted: {self.csrf_token[:20]}...")
            
            # Step 3: Find login form
            forms = parse_forms(response.text, self.login_url)
            login_form = None
            
            for form in forms:
                if is_login_form(form):
                    login_form = form
                    break
            
            # If no obvious login form, use the first form
            if not login_form and forms:
                login_form = forms[0]
                self._log("warning", "No obvious login form found, using first form")
            
            # Step 4: Prepare login data
            login_data = self._prepare_login_data(login_form, response.text)
            
            # Determine POST URL
            post_url = login_form.action if login_form else self.login_url
            
            self._log("info", f"Submitting credentials to {post_url}")
            
            # Step 5: Submit login form
            response = self.session.post(
                post_url,
                data=login_data,
                timeout=10,
                allow_redirects=True
            )
            
            # Step 6: Verify authentication
            if self._verify_authentication(response):
                self._log("success", "Authentication successful!")
                return self.session
            else:
                raise AuthenticationError("Authentication failed - invalid credentials or detection failed")
        
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Network error during authentication: {str(e)}")
    
    def _prepare_login_data(self, login_form, html_content: str) -> Dict[str, str]:
        """
        Prepare login POST data
        
        Args:
            login_form: FormData object or None
            html_content: HTML content of login page
        
        Returns:
            Dictionary of form data
        """
        login_data = {}
        
        # If we have a form, use its fields
        if login_form:
            login_data = login_form.inputs.copy()
        
        # Try to identify username and password fields
        username_field = self._find_field_name(
            login_data.keys() if login_form else [],
            ['username', 'user', 'email', 'login', 'userid', 'user_name']
        )
        
        password_field = self._find_field_name(
            login_data.keys() if login_form else [],
            ['password', 'pass', 'passwd', 'pwd']
        )
        
        # Set credentials
        if username_field:
            login_data[username_field] = self.username
        else:
            # Fallback to common field names
            login_data['username'] = self.username
        
        if password_field:
            login_data[password_field] = self.password
        else:
            # Fallback
            login_data['password'] = self.password
        
        # Add CSRF token if available
        if self.csrf_token:
            # Try to find actual CSRF field name from form
            if login_form:
                soup = BeautifulSoup(html_content, 'html.parser')
                forms = soup.find_all('form')
                for form in forms:
                    csrf_data = extract_csrf_from_form(form)
                    if csrf_data:
                        self.csrf_field_name = csrf_data[0]
                        login_data[self.csrf_field_name] = self.csrf_token
                        break
            else:
                login_data[self.csrf_field_name] = self.csrf_token
        
        return login_data
    
    def _find_field_name(self, field_names: list, candidates: list) -> Optional[str]:
        """Find matching field name from candidates"""
        field_names_lower = [f.lower() for f in field_names]
        
        for candidate in candidates:
            if candidate in field_names_lower:
                # Return original case
                idx = field_names_lower.index(candidate)
                return list(field_names)[idx]
        
        return None
    
    def _verify_authentication(self, response: requests.Response) -> bool:
        """
        Verify if authentication was successful
        
        Multiple checks:
        1. No redirect back to login page
        2. Presence of logout link
        3. Absence of login form
        4. HTTP status code
        
        Args:
            response: Response object after login POST
        
        Returns:
            True if authenticated, False otherwise
        """
        # Check 1: Status code
        if response.status_code not in [200, 302, 303]:
            self._log("warning", f"Unexpected status code: {response.status_code}")
            return False
        
        # Check 2: Not redirected back to login
        final_url = response.url.lower()
        login_url_lower = self.login_url.lower()
        
        if 'login' in final_url or final_url == login_url_lower:
            self._log("error", "Redirected back to login page")
            return False
        
        # Check 3: Look for logout indicator
        if has_logout_indicator(response.text):
            return True
        
        # Check 4: Check for absence of login form
        forms = parse_forms(response.text, response.url)
        has_login = any(is_login_form(form) for form in forms)
        
        if has_login:
            self._log("error", "Login form still present after authentication")
            return False
        
        # Check 5: Check for common authenticated page indicators
        authenticated_indicators = [
            'dashboard', 'profile', 'account', 'welcome',
            'logout', 'signout', 'my account'
        ]
        
        content_lower = response.text.lower()
        has_indicator = any(indicator in content_lower for indicator in authenticated_indicators)
        
        if has_indicator:
            return True
        
        # If we got here and didn't fail previous checks, consider it successful
        # (Some apps don't have obvious indicators)
        self._log("warning", "Could not definitively verify authentication, assuming success")
        return True
    
    def is_session_valid(self, test_url: Optional[str] = None) -> bool:
        """
        Check if current session is still valid
        
        Args:
            test_url: URL to test (defaults to base_url)
        
        Returns:
            True if session is valid
        """
        if not test_url:
            test_url = self.base_url
        
        try:
            response = self.session.get(test_url, timeout=10, allow_redirects=True)
            
            # Check if redirected to login
            if 'login' in response.url.lower():
                return False
            
            # Check for logout indicator
            return has_logout_indicator(response.text)
        
        except:
            return False
    
    def refresh_csrf_token(self, url: str) -> Optional[str]:
        """
        Refresh CSRF token from a page
        
        Args:
            url: URL to fetch token from
        
        Returns:
            New CSRF token or None
        """
        try:
            response = self.session.get(url, timeout=10)
            token = extract_csrf_token(response.text, self.session.cookies.get_dict())
            if token:
                self.csrf_token = token
            return token
        except:
            return None
