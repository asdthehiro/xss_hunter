"""
Helper Functions - General utility functions
"""
from urllib.parse import urlparse, urljoin, parse_qs, urlunparse, urlencode
from typing import Dict, Optional
import re


def normalize_url(url: str, base_url: str = "") -> str:
    """Normalize and validate URL"""
    if not url:
        return ""
    
    # Handle relative URLs
    if not url.startswith(('http://', 'https://')):
        if base_url:
            url = urljoin(base_url, url)
        else:
            return ""
    
    # Remove fragment
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, 
                      parsed.params, parsed.query, ''))


def is_same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs are from the same domain"""
    domain1 = urlparse(url1).netloc
    domain2 = urlparse(url2).netloc
    return domain1 == domain2


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    return urlparse(url).netloc


def url_has_params(url: str) -> bool:
    """Check if URL has query parameters"""
    parsed = urlparse(url)
    return bool(parsed.query)


def get_url_params(url: str) -> Dict[str, list]:
    """Extract parameters from URL"""
    parsed = urlparse(url)
    return parse_qs(parsed.query)


def build_url_with_params(base_url: str, params: Dict[str, str]) -> str:
    """Build URL with query parameters"""
    parsed = urlparse(base_url)
    # Remove existing query
    base = urlunparse((parsed.scheme, parsed.netloc, parsed.path, 
                      parsed.params, '', ''))
    
    if params:
        query_string = urlencode(params)
        return f"{base}?{query_string}"
    return base


def is_valid_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def clean_url(url: str) -> str:
    """Clean URL by removing fragments and normalizing"""
    try:
        parsed = urlparse(url)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, 
                          parsed.params, parsed.query, ''))
    except:
        return url


def extract_base_url(url: str) -> str:
    """Extract base URL (scheme + netloc)"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def is_logout_url(url: str) -> bool:
    """Detect if URL is a logout endpoint"""
    logout_patterns = [
        r'/logout',
        r'/signout',
        r'/sign-out',
        r'/logoff',
        r'/disconnect',
        r'/exit'
    ]
    
    url_lower = url.lower()
    return any(re.search(pattern, url_lower) for pattern in logout_patterns)


def is_static_resource(url: str) -> bool:
    """Check if URL points to static resource"""
    static_extensions = [
        '.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg',
        '.ico', '.woff', '.woff2', '.ttf', '.eot', '.pdf', '.zip',
        '.mp4', '.mp3', '.avi', '.mov', '.wmv'
    ]
    
    url_lower = url.lower()
    return any(url_lower.endswith(ext) for ext in static_extensions)


def truncate_string(s: str, max_length: int = 100) -> str:
    """Truncate string with ellipsis"""
    if len(s) <= max_length:
        return s
    return s[:max_length-3] + "..."


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return filename
