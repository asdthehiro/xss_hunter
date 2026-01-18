"""
Authentication Module - Handle login and session management
"""
import requests
from typing import Optional, Dict, Tuple
from bs4 import BeautifulSoup
import time

from utils.csrf import extract_csrf_token, extract_csrf_from_form
from utils.forms import parse_forms, is_login_form, has_logout_indicator


class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass


class Authenticator:
    """Handles authentication and session management"""
    
    def __init__(self, login_url: str, username: str, password: str, 
                 base_url: str, logger=None):
        """
        Initialize authenticator
        
        Args:
            login_url: URL of the login page
            username: Username for authentication
            password: Password for authentication
            base_url: Base URL of the target application
            logger: Logger instance for output
        """
        self.login_url = login_url
        self.username = username
        self.password = password
        self.base_url = base_url
        self.logger = logger
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
        
        Returns:
            Authenticated requests.Session object
        
        Raises:
            AuthenticationError: If authentication fails
        """
        self._log("info", f"Attempting authentication at {self.login_url}")
        
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
