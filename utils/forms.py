"""
Form Parsing Module
"""
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin


class FormData:
    """Represents an HTML form with all its data"""
    
    def __init__(self, action: str, method: str, inputs: Dict[str, str], 
                 form_id: str = "", form_name: str = ""):
        self.action = action
        self.method = method.upper() if method else "GET"
        self.inputs = inputs
        self.form_id = form_id
        self.form_name = form_name
    
    def __repr__(self):
        return f"FormData(action={self.action}, method={self.method}, inputs={len(self.inputs)})"


def parse_forms(html_content: str, base_url: str) -> List[FormData]:
    """
    Parse all forms from HTML content
    
    Args:
        html_content: HTML content to parse
        base_url: Base URL for resolving relative action URLs
    
    Returns:
        List of FormData objects
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    forms = []
    
    for form in soup.find_all('form'):
        # Extract form attributes
        action = form.get('action', '')
        method = form.get('method', 'GET')
        form_id = form.get('id', '')
        form_name = form.get('name', '')
        
        # Resolve action URL
        if not action:
            action = base_url
        elif not action.startswith(('http://', 'https://')):
            action = urljoin(base_url, action)
        
        # Extract all input fields
        inputs = {}
        
        # Text inputs, hidden inputs, passwords, etc.
        for input_tag in form.find_all('input'):
            input_name = input_tag.get('name')
            input_value = input_tag.get('value', '')
            input_type = input_tag.get('type', 'text')
            
            if input_name:
                # Skip submit buttons unless they have meaningful names
                if input_type.lower() in ['submit', 'button', 'image']:
                    continue
                inputs[input_name] = input_value
        
        # Textareas
        for textarea in form.find_all('textarea'):
            textarea_name = textarea.get('name')
            if textarea_name:
                inputs[textarea_name] = textarea.get_text(strip=True)
        
        # Select dropdowns
        for select in form.find_all('select'):
            select_name = select.get('name')
            if select_name:
                # Get first selected option or first option
                selected = select.find('option', selected=True)
                if selected:
                    inputs[select_name] = selected.get('value', '')
                else:
                    first_option = select.find('option')
                    if first_option:
                        inputs[select_name] = first_option.get('value', '')
                    else:
                        inputs[select_name] = ''
        
        # Create FormData object
        form_data = FormData(
            action=action,
            method=method,
            inputs=inputs,
            form_id=form_id,
            form_name=form_name
        )
        
        forms.append(form_data)
    
    return forms


def get_testable_inputs(form_data: FormData) -> List[str]:
    """
    Get list of input names that should be tested for XSS
    Excludes CSRF tokens and other security fields
    """
    excluded_patterns = [
        'csrf', 'token', 'xsrf', 'authenticity',
        '_token', 'csrf_token', 'csrfmiddlewaretoken'
    ]
    
    testable = []
    for input_name in form_data.inputs.keys():
        input_lower = input_name.lower()
        # Exclude CSRF and security tokens
        if not any(pattern in input_lower for pattern in excluded_patterns):
            testable.append(input_name)
    
    return testable


def extract_links(html_content: str, base_url: str) -> List[str]:
    """
    Extract all links from HTML content
    
    Args:
        html_content: HTML content to parse
        base_url: Base URL for resolving relative URLs
    
    Returns:
        List of absolute URLs
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    links = set()
    
    # Extract <a> tags
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if href and not href.startswith(('#', 'javascript:', 'mailto:')):
            absolute_url = urljoin(base_url, href)
            links.add(absolute_url)
    
    return list(links)


def is_login_form(form_data: FormData) -> bool:
    """
    Detect if form is a login form
    """
    # Check action URL
    action_lower = form_data.action.lower()
    if any(keyword in action_lower for keyword in ['login', 'signin', 'auth']):
        return True
    
    # Check input fields
    input_names = [name.lower() for name in form_data.inputs.keys()]
    
    # Look for password field
    has_password = any('password' in name or 'pass' in name for name in input_names)
    
    # Look for username/email field
    has_username = any(
        name in ['username', 'email', 'user', 'login', 'userid']
        for name in input_names
    )
    
    return has_password and has_username


def has_logout_indicator(html_content: str) -> bool:
    """
    Check if page contains logout link (indicates authenticated state)
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check for logout links
    for link in soup.find_all('a', href=True):
        href = link.get('href', '').lower()
        text = link.get_text().lower()
        
        if any(keyword in href or keyword in text 
               for keyword in ['logout', 'signout', 'sign-out', 'logoff']):
            return True
    
    return False
