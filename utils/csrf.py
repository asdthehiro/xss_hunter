"""
CSRF Token Extraction Module
"""
from bs4 import BeautifulSoup
from typing import Optional, Dict
import re


def extract_csrf_token(html_content: str, session_cookies: Dict = None) -> Optional[str]:
    """
    Extract CSRF token from HTML content
    
    Checks multiple common patterns:
    - Hidden input fields (csrf_token, _csrf, authenticity_token, etc.)
    - Meta tags
    - JavaScript variables
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Common CSRF token field names
    csrf_field_names = [
        'csrf_token',
        'csrf',
        '_csrf',
        'csrf-token',
        'csrfmiddlewaretoken',
        'authenticity_token',
        '_token',
        'token',
        'xsrf_token',
        'xsrf-token'
    ]
    
    # 1. Check hidden input fields
    for field_name in csrf_field_names:
        # Case-insensitive search
        token_input = soup.find('input', {'name': re.compile(f'^{field_name}$', re.I)})
        if token_input and token_input.get('value'):
            return token_input.get('value')
    
    # 2. Check meta tags
    for field_name in csrf_field_names:
        meta_tag = soup.find('meta', {'name': re.compile(f'^{field_name}$', re.I)})
        if meta_tag and meta_tag.get('content'):
            return meta_tag.get('content')
    
    # 3. Check JavaScript variables (common pattern)
    script_tags = soup.find_all('script')
    for script in script_tags:
        script_content = script.string
        if script_content:
            # Look for patterns like: var csrf_token = "...";
            for field_name in csrf_field_names:
                pattern = rf'{field_name}\s*[:=]\s*["\']([^"\']+)["\']'
                match = re.search(pattern, script_content, re.I)
                if match:
                    return match.group(1)
    
    # 4. Check cookies for CSRF token
    if session_cookies:
        for field_name in csrf_field_names:
            for cookie_name, cookie_value in session_cookies.items():
                if field_name.lower() in cookie_name.lower():
                    return cookie_value
    
    return None


def extract_all_csrf_data(html_content: str, session_cookies: Dict = None) -> Dict[str, str]:
    """
    Extract all potential CSRF-related fields
    Returns dict with field_name: value
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    csrf_data = {}
    
    csrf_field_names = [
        'csrf_token', 'csrf', '_csrf', 'csrf-token',
        'csrfmiddlewaretoken', 'authenticity_token',
        '_token', 'token', 'xsrf_token', 'xsrf-token'
    ]
    
    # Extract all hidden inputs that might be CSRF tokens
    for field_name in csrf_field_names:
        token_input = soup.find('input', {'name': re.compile(f'^{field_name}$', re.I)})
        if token_input and token_input.get('value'):
            csrf_data[token_input.get('name')] = token_input.get('value')
    
    return csrf_data


def add_csrf_to_data(data: Dict[str, str], csrf_token: Optional[str], 
                     csrf_field_name: str = 'csrf_token') -> Dict[str, str]:
    """
    Add CSRF token to POST data if available
    """
    if csrf_token:
        data[csrf_field_name] = csrf_token
    return data


def extract_csrf_from_form(form_element) -> Optional[tuple]:
    """
    Extract CSRF token from a specific form element
    Returns (field_name, token_value) or None
    """
    csrf_field_names = [
        'csrf_token', 'csrf', '_csrf', 'csrf-token',
        'csrfmiddlewaretoken', 'authenticity_token',
        '_token', 'token', 'xsrf_token', 'xsrf-token'
    ]
    
    for field_name in csrf_field_names:
        token_input = form_element.find('input', {'name': re.compile(f'^{field_name}$', re.I)})
        if token_input and token_input.get('value'):
            return (token_input.get('name'), token_input.get('value'))
    
    return None
