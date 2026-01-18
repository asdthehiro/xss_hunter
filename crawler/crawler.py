"""
Authenticated Crawler Module - Discover authenticated pages
"""
from typing import Set, List, Optional
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
import time

from utils.forms import extract_links
from utils.helpers import (
    is_same_domain, is_logout_url, is_static_resource,
    normalize_url, clean_url
)


class AuthenticatedCrawler:
    """Crawl authenticated pages while maintaining session"""
    
    def __init__(self, session: requests.Session, base_url: str, 
                 max_depth: int = 2, max_pages: int = 50, logger=None):
        """
        Initialize crawler
        
        Args:
            session: Authenticated requests.Session
            base_url: Base URL to start crawling from
            max_depth: Maximum crawl depth
            max_pages: Maximum number of pages to crawl
            logger: Logger instance
        """
        self.session = session
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.logger = logger
        
        self.visited: Set[str] = set()
        self.discovered: Set[str] = set()
        self.to_visit: List[tuple] = [(base_url, 0)]  # (url, depth)
    
    def _log(self, level: str, message: str):
        """Internal logging helper"""
        if self.logger:
            if level == "info":
                self.logger.info(message)
            elif level == "success":
                self.logger.success(message)
            elif level == "warning":
                self.logger.warning(message)
    
    def crawl(self) -> List[str]:
        """
        Start crawling and return discovered URLs
        
        Returns:
            List of discovered authenticated URLs
        """
        self._log("info", f"Starting authenticated crawl from {self.base_url}")
        self._log("info", f"Max depth: {self.max_depth}, Max pages: {self.max_pages}")
        
        while self.to_visit and len(self.visited) < self.max_pages:
            url, depth = self.to_visit.pop(0)
            
            # Skip if already visited
            if url in self.visited:
                continue
            
            # Skip if max depth exceeded
            if depth > self.max_depth:
                continue
            
            # Skip logout URLs
            if is_logout_url(url):
                self._log("warning", f"Skipping logout URL: {url}")
                continue
            
            # Skip static resources
            if is_static_resource(url):
                continue
            
            # Crawl this page
            self._crawl_page(url, depth)
            
            # Rate limiting
            time.sleep(0.5)
        
        self._log("success", f"Crawling complete. Discovered {len(self.discovered)} URLs")
        
        return list(self.discovered)
    
    def _crawl_page(self, url: str, depth: int):
        """
        Crawl a single page and extract links
        
        Args:
            url: URL to crawl
            depth: Current depth
        """
        try:
            self._log("info", f"Crawling [{depth}]: {url}")
            
            response = self.session.get(url, timeout=10, allow_redirects=True)
            
            # Mark as visited
            self.visited.add(url)
            
            # Check if we're still authenticated
            if self._is_login_redirect(response):
                self._log("warning", "Session expired or redirected to login")
                return
            
            # Add to discovered URLs
            self.discovered.add(url)
            
            # Extract links if HTML response
            if 'text/html' in response.headers.get('Content-Type', ''):
                links = extract_links(response.text, url)
                
                # Filter and add new links
                for link in links:
                    if self._should_crawl(link):
                        clean_link = clean_url(link)
                        if clean_link not in self.visited and clean_link not in [u for u, d in self.to_visit]:
                            self.to_visit.append((clean_link, depth + 1))
        
        except requests.exceptions.RequestException as e:
            self._log("warning", f"Error crawling {url}: {str(e)}")
        except Exception as e:
            self._log("warning", f"Unexpected error crawling {url}: {str(e)}")
    
    def _should_crawl(self, url: str) -> bool:
        """
        Determine if URL should be crawled
        
        Args:
            url: URL to check
        
        Returns:
            True if should crawl
        """
        # Must be same domain
        if not is_same_domain(url, self.base_url):
            return False
        
        # Skip logout URLs
        if is_logout_url(url):
            return False
        
        # Skip static resources
        if is_static_resource(url):
            return False
        
        # Skip javascript: and mailto: links
        if url.startswith(('javascript:', 'mailto:', 'tel:', '#')):
            return False
        
        return True
    
    def _is_login_redirect(self, response: requests.Response) -> bool:
        """
        Check if response is a redirect to login page
        
        Args:
            response: HTTP response
        
        Returns:
            True if redirected to login
        """
        # Check URL
        if 'login' in response.url.lower():
            return True
        
        # Check for login form in content
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            password_inputs = soup.find_all('input', {'type': 'password'})
            if password_inputs:
                return True
        except:
            pass
        
        return False
    
    def add_manual_urls(self, urls: List[str]):
        """
        Add manually specified URLs to crawl list
        
        Args:
            urls: List of URLs to add
        """
        for url in urls:
            normalized = normalize_url(url, self.base_url)
            if normalized and normalized not in self.visited:
                self.to_visit.append((normalized, 0))
                self._log("info", f"Added manual URL: {normalized}")
