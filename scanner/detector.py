"""
XSS Detection Module - Analyze responses for XSS vulnerabilities
"""
from typing import Optional, Tuple, List
from bs4 import BeautifulSoup
import re


class XSSContext:
    """XSS context types"""
    TAG = "tag"
    ATTRIBUTE = "attribute"
    SCRIPT = "script"
    COMMENT = "comment"
    UNKNOWN = "unknown"


class XSSDetector:
    """Detect XSS vulnerabilities in HTTP responses"""
    
    @staticmethod
    def detect_reflection(response_text: str, payload: str) -> bool:
        """
        Check if payload is reflected in response
        
        Args:
            response_text: HTTP response body
            payload: Injected payload
        
        Returns:
            True if payload is reflected
        """
        # Direct reflection
        if payload in response_text:
            return True
        
        # HTML entity encoded reflection
        html_encoded = (payload.replace('&', '&amp;')
                               .replace('<', '&lt;')
                               .replace('>', '&gt;')
                               .replace('"', '&quot;')
                               .replace("'", '&#x27;'))
        
        if html_encoded in response_text:
            return False  # Encoded, so not vulnerable
        
        # Check for partial reflection
        # Remove HTML tags from payload for checking
        payload_text = re.sub(r'<[^>]+>', '', payload)
        if len(payload_text) > 5 and payload_text in response_text:
            return True
        
        return False
    
    @staticmethod
    def detect_xss(response_text: str, payload: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Detect if payload resulted in XSS
        
        Args:
            response_text: HTTP response body
            payload: Injected payload
        
        Returns:
            Tuple of (is_vulnerable, context, details)
        """
        # First check if payload is reflected
        if not XSSDetector.detect_reflection(response_text, payload):
            return (False, None, None)
        
        # Check if payload is properly encoded (escaped)
        if XSSDetector._is_encoded(response_text, payload):
            return (False, XSSContext.UNKNOWN, "Reflected but encoded")
        
        # Detect context of reflection
        context = XSSDetector._detect_context(response_text, payload)
        
        # Check if payload is actually executable
        is_vulnerable = XSSDetector._is_executable(response_text, payload, context)
        
        details = f"Reflected in {context} context"
        
        return (is_vulnerable, context, details)
    
    @staticmethod
    def _is_encoded(response_text: str, payload: str) -> bool:
        """Check if payload is HTML encoded"""
        dangerous_chars = ['<', '>', '"', "'"]
        encoded_chars = ['&lt;', '&gt;', '&quot;', '&#x27;', '&#39;']
        
        # Check if dangerous characters are encoded
        for char in dangerous_chars:
            if char in payload:
                # Look for encoded version near where payload should be
                if any(enc in response_text for enc in encoded_chars):
                    # More sophisticated check: find payload location
                    payload_text = re.sub(r'[<>"\']', '', payload)
                    if payload_text in response_text:
                        # Find that location and check surrounding area
                        idx = response_text.find(payload_text)
                        if idx > 0:
                            surrounding = response_text[max(0, idx-50):idx+len(payload_text)+50]
                            if any(enc in surrounding for enc in encoded_chars):
                                return True
        
        return False
    
    @staticmethod
    def _detect_context(response_text: str, payload: str) -> str:
        """
        Detect the context where payload is reflected
        
        Returns:
            One of XSSContext values
        """
        try:
            soup = BeautifulSoup(response_text, 'html.parser')
            
            # Find payload in HTML
            payload_text = re.sub(r'<[^>]+>', '', payload)
            
            # Check if payload appears in script tag
            for script in soup.find_all('script'):
                if script.string and (payload in script.string or payload_text in script.string):
                    return XSSContext.SCRIPT
            
            # Check if payload appears in HTML comment
            for comment in soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in text):
                if payload in str(comment) or payload_text in str(comment):
                    return XSSContext.COMMENT
            
            # Check if payload appears in tag attribute
            for tag in soup.find_all():
                for attr, value in tag.attrs.items():
                    if isinstance(value, str) and (payload in value or payload_text in value):
                        return XSSContext.ATTRIBUTE
            
            # Check if payload appears as text content (tag context)
            if payload in response_text or payload_text in response_text:
                return XSSContext.TAG
            
        except:
            pass
        
        return XSSContext.UNKNOWN
    
    @staticmethod
    def _is_executable(response_text: str, payload: str, context: str) -> bool:
        """
        Determine if reflected payload is actually executable
        
        Args:
            response_text: HTTP response
            payload: Injected payload
            context: Detected context
        
        Returns:
            True if payload is likely executable
        """
        # If payload contains script tags and they're reflected
        if '<script>' in payload.lower() and '<script>' in response_text.lower():
            # Check if script tag is properly formed
            if re.search(r'<script[^>]*>.*?</script>', response_text, re.IGNORECASE | re.DOTALL):
                return True
        
        # If payload contains event handlers
        event_handlers = [
            'onload', 'onerror', 'onclick', 'onmouseover', 
            'onfocus', 'onblur', 'onchange', 'ontoggle'
        ]
        for handler in event_handlers:
            if handler in payload.lower() and handler in response_text.lower():
                # Check if it's in a valid HTML tag
                pattern = rf'<[^>]*{handler}\s*=\s*["\']?[^"\']*alert\([^)]*\)'
                if re.search(pattern, response_text, re.IGNORECASE):
                    return True
        
        # If payload contains img/svg/iframe with dangerous attributes
        dangerous_tags = ['img', 'svg', 'iframe', 'body', 'input', 'select', 'textarea']
        for tag in dangerous_tags:
            if f'<{tag}' in payload.lower() and f'<{tag}' in response_text.lower():
                return True
        
        # Context-specific checks
        if context == XSSContext.SCRIPT:
            # In script context, even simple expressions can be dangerous
            if 'alert(' in payload and 'alert(' in response_text:
                return True
        
        if context == XSSContext.ATTRIBUTE:
            # Check if we can break out of attribute
            if any(char in payload for char in ['"', "'"]) and \
               any(handler in response_text.lower() for handler in event_handlers):
                return True
        
        if context == XSSContext.TAG:
            # In tag context, check if HTML is interpreted
            if any(tag in response_text.lower() for tag in ['<script', '<img', '<svg', '<iframe']):
                return True
        
        return False
    
    @staticmethod
    def classify_xss_type(method: str, is_reflected: bool, is_stored: bool) -> str:
        """
        Classify XSS type
        
        Args:
            method: HTTP method used
            is_reflected: Whether payload is reflected immediately
            is_stored: Whether payload persists across requests
        
        Returns:
            XSS type string
        """
        if is_stored:
            return "Stored XSS"
        elif is_reflected and method == "GET":
            return "Reflected XSS (GET)"
        elif is_reflected and method == "POST":
            return "Reflected XSS (POST)"
        else:
            return "Potential XSS"
    
    @staticmethod
    def extract_vulnerable_snippet(response_text: str, payload: str, max_length: int = 200) -> str:
        """
        Extract snippet of HTML showing vulnerable reflection
        
        Args:
            response_text: Full response
            payload: Reflected payload
            max_length: Maximum snippet length
        
        Returns:
            HTML snippet
        """
        try:
            # Find payload location
            idx = response_text.find(payload)
            if idx == -1:
                # Try finding payload without tags
                payload_text = re.sub(r'<[^>]+>', '', payload)
                idx = response_text.find(payload_text)
            
            if idx == -1:
                return "Payload reflected but location not found"
            
            # Extract surrounding context
            start = max(0, idx - max_length // 2)
            end = min(len(response_text), idx + len(payload) + max_length // 2)
            
            snippet = response_text[start:end]
            
            # Clean up snippet
            snippet = snippet.replace('\n', ' ').replace('\r', '')
            snippet = re.sub(r'\s+', ' ', snippet)
            
            if start > 0:
                snippet = "..." + snippet
            if end < len(response_text):
                snippet = snippet + "..."
            
            return snippet
        
        except:
            return "Error extracting snippet"
