"""
Core XSS Scanner Module - Test for XSS vulnerabilities
"""
from typing import List, Dict, Set, Optional, Tuple
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import time
from copy import deepcopy

from scanner.payloads import XSSPayloads, PayloadGenerator
from scanner.detector import XSSDetector
from utils.forms import parse_forms, get_testable_inputs, FormData
from utils.csrf import extract_csrf_token
from utils.helpers import build_url_with_params, get_url_params


class VulnerabilityReport:
    """Represents a found XSS vulnerability"""
    
    def __init__(self, url: str, method: str, parameter: str, 
                 payload: str, xss_type: str, context: str = ""):
        self.url = url
        self.method = method
        self.parameter = parameter
        self.payload = payload
        self.xss_type = xss_type
        self.context = context
    
    def __hash__(self):
        return hash((self.url, self.method, self.parameter))
    
    def __eq__(self, other):
        if not isinstance(other, VulnerabilityReport):
            return False
        return (self.url == other.url and 
                self.method == other.method and 
                self.parameter == other.parameter)


class XSSScanner:
    """Main XSS scanning engine"""
    
    def __init__(self, session: requests.Session, logger=None, 
                 use_advanced_payloads: bool = False):
        """
        Initialize XSS scanner
        
        Args:
            session: Authenticated requests.Session
            logger: Logger instance
            use_advanced_payloads: Whether to use advanced payload set
        """
        self.session = session
        self.logger = logger
        self.use_advanced_payloads = use_advanced_payloads
        self.vulnerabilities: Set[VulnerabilityReport] = set()
        self.tested_urls = 0
        self.tested_params = 0
        
        # Get payloads
        if use_advanced_payloads:
            self.payloads = XSSPayloads.get_advanced_payloads()
        else:
            self.payloads = XSSPayloads.get_basic_payloads()
    
    def _log(self, level: str, message: str):
        """Internal logging helper"""
        if self.logger:
            if level == "info":
                self.logger.info(message)
            elif level == "success":
                self.logger.success(message)
            elif level == "warning":
                self.logger.warning(message)
            elif level == "error":
                self.logger.error(message)
    
    def scan_urls(self, urls: List[str]) -> List[VulnerabilityReport]:
        """
        Scan multiple URLs for XSS
        
        Args:
            urls: List of URLs to scan
        
        Returns:
            List of found vulnerabilities
        """
        self._log("info", f"Starting XSS scan on {len(urls)} URLs")
        self._log("info", f"Using {len(self.payloads)} payloads")
        
        for url in urls:
            self._log("info", f"Scanning: {url}")
            self.scan_url(url)
            time.sleep(0.3)  # Rate limiting
        
        self._log("success", f"Scan complete. Found {len(self.vulnerabilities)} vulnerabilities")
        
        return list(self.vulnerabilities)
    
    def scan_url(self, url: str):
        """
        Scan a single URL for XSS
        
        Tests both GET and POST parameters
        
        Args:
            url: URL to scan
        """
        self.tested_urls += 1
        
        try:
            # First, fetch the page to get forms
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                self._log("warning", f"Got status {response.status_code} for {url}")
                return
            
            # Test GET parameters
            self._test_get_parameters(url)
            
            # Test POST parameters from forms
            if 'text/html' in response.headers.get('Content-Type', ''):
                forms = parse_forms(response.text, url)
                for form in forms:
                    self._test_form(form)
        
        except requests.exceptions.RequestException as e:
            self._log("error", f"Error scanning {url}: {str(e)}")
        except Exception as e:
            self._log("error", f"Unexpected error scanning {url}: {str(e)}")
    
    def _test_get_parameters(self, url: str):
        """
        Test GET parameters for XSS
        
        Args:
            url: URL with GET parameters
        """
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if not params:
            return
        
        # Base URL without query string
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Test each parameter
        for param_name in params.keys():
            self._log("info", f"  Testing GET parameter: {param_name}")
            self.tested_params += 1
            
            # Test with each payload
            for payload in self.payloads:
                # Create test parameters
                test_params = {}
                for pname, pvalues in params.items():
                    if pname == param_name:
                        test_params[pname] = payload
                    else:
                        test_params[pname] = pvalues[0] if pvalues else ''
                
                # Build test URL
                test_url = build_url_with_params(base_url, test_params)
                
                # Send request
                try:
                    response = self.session.get(test_url, timeout=10, allow_redirects=True)
                    
                    # Check for XSS
                    is_vulnerable, context, details = XSSDetector.detect_xss(
                        response.text, payload
                    )
                    
                    if is_vulnerable:
                        xss_type = XSSDetector.classify_xss_type("GET", True, False)
                        vuln = VulnerabilityReport(
                            url=test_url,
                            method="GET",
                            parameter=param_name,
                            payload=payload,
                            xss_type=xss_type,
                            context=context
                        )
                        
                        if vuln not in self.vulnerabilities:
                            self.vulnerabilities.add(vuln)
                            self._report_vulnerability(vuln)
                            # One payload per parameter is enough
                            break
                
                except requests.exceptions.RequestException:
                    continue
                
                time.sleep(0.2)  # Rate limiting between payloads
    
    def _test_form(self, form: FormData):
        """
        Test form inputs for XSS
        
        Args:
            form: FormData object
        """
        # Get testable inputs (exclude CSRF tokens)
        testable_inputs = get_testable_inputs(form)
        
        if not testable_inputs:
            return
        
        method = form.method.upper()
        action_url = form.action
        
        self._log("info", f"  Testing {method} form: {action_url}")
        
        # Test each input field
        for input_name in testable_inputs:
            self._log("info", f"    Testing {method} parameter: {input_name}")
            self.tested_params += 1
            
            # Test with each payload
            for payload in self.payloads:
                # Prepare form data
                test_data = form.inputs.copy()
                test_data[input_name] = payload
                
                # Refresh CSRF token if needed
                csrf_token = extract_csrf_token(
                    self._fetch_page(action_url),
                    self.session.cookies.get_dict()
                )
                if csrf_token:
                    # Find CSRF field name
                    for key in test_data.keys():
                        if 'csrf' in key.lower() or 'token' in key.lower():
                            test_data[key] = csrf_token
                            break
                
                # Send request
                try:
                    if method == "POST":
                        response = self.session.post(
                            action_url, 
                            data=test_data, 
                            timeout=10,
                            allow_redirects=True
                        )
                    else:
                        response = self.session.get(
                            action_url,
                            params=test_data,
                            timeout=10,
                            allow_redirects=True
                        )
                    
                    # Check for reflected XSS
                    is_vulnerable, context, details = XSSDetector.detect_xss(
                        response.text, payload
                    )
                    
                    if is_vulnerable:
                        # Check if it's stored XSS
                        is_stored = self._check_stored_xss(action_url, payload)
                        
                        xss_type = XSSDetector.classify_xss_type(
                            method, True, is_stored
                        )
                        
                        vuln = VulnerabilityReport(
                            url=action_url,
                            method=method,
                            parameter=input_name,
                            payload=payload,
                            xss_type=xss_type,
                            context=context
                        )
                        
                        if vuln not in self.vulnerabilities:
                            self.vulnerabilities.add(vuln)
                            self._report_vulnerability(vuln)
                            # One payload per parameter is enough
                            break
                
                except requests.exceptions.RequestException:
                    continue
                
                time.sleep(0.2)  # Rate limiting
    
    def _check_stored_xss(self, url: str, payload: str) -> bool:
        """
        Check if XSS is stored (persistent)
        
        Args:
            url: URL to check
            payload: Payload to look for
        
        Returns:
            True if payload persists
        """
        try:
            # Wait a bit for storage to complete
            time.sleep(1)
            
            # Fetch the page again
            response = self.session.get(url, timeout=10)
            
            # Check if payload is still there
            return XSSDetector.detect_reflection(response.text, payload)
        
        except:
            return False
    
    def _fetch_page(self, url: str) -> str:
        """
        Fetch page content
        
        Args:
            url: URL to fetch
        
        Returns:
            Page HTML content
        """
        try:
            response = self.session.get(url, timeout=10)
            return response.text
        except:
            return ""
    
    def _report_vulnerability(self, vuln: VulnerabilityReport):
        """
        Report found vulnerability to logger
        
        Args:
            vuln: VulnerabilityReport object
        """
        if self.logger:
            self.logger.xss_found(
                url=vuln.url,
                method=vuln.method,
                parameter=vuln.parameter,
                payload=vuln.payload,
                xss_type=vuln.xss_type,
                context=vuln.context
            )
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get scanning statistics
        
        Returns:
            Dictionary with stats
        """
        return {
            'urls_tested': self.tested_urls,
            'params_tested': self.tested_params,
            'vulnerabilities_found': len(self.vulnerabilities)
        }
