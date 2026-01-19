#!/usr/bin/env python3
"""
XSS-Hunter - Authenticated XSS Scanner
Author: dark_hunter
Platform: Kali Linux
Language: Python 3

Professional-grade tool for detecting XSS vulnerabilities
in authenticated web applications.
"""
import argparse
import sys
import os
from typing import List, Optional
import getpass

from auth import Authenticator, AuthenticationError
from crawler import AuthenticatedCrawler
from scanner.scanner import XSSScanner
from utils.logger import Logger
from utils.helpers import is_valid_url


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='XSS-Hunter - Authenticated XSS Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 main.py
  python3 main.py --urls targets.txt --output results.txt
  python3 main.py --crawl --advanced
  
For authorized testing only. Use responsibly.
        """
    )
    
    parser.add_argument(
        '--urls',
        type=str,
        metavar='FILE',
        help='File containing URLs to test (one per line)'
    )
    
    parser.add_argument(
        '--crawl',
        action='store_true',
        help='Enable authenticated crawling to discover URLs'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        metavar='FILE',
        help='Save results to file'
    )
    
    parser.add_argument(
        '--advanced',
        action='store_true',
        help='Use advanced payload set (more thorough but slower)'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        default=2,
        metavar='N',
        help='Maximum crawl depth (default: 2)'
    )
    
    parser.add_argument(
        '--max-pages',
        type=int,
        default=50,
        metavar='N',
        help='Maximum pages to crawl (default: 50)'
    )
    
    return parser.parse_args()


def read_urls_from_file(filepath: str) -> List[str]:
    """
    Read URLs from file
    
    Args:
        filepath: Path to file containing URLs
    
    Returns:
        List of URLs
    """
    urls = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if is_valid_url(line):
                        urls.append(line)
        return urls
    except FileNotFoundError:
        print(f"[-] Error: File not found: {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Error reading file: {e}")
        sys.exit(1)


def get_user_input() -> dict:
    """
    Get required input from user
    
    Returns:
        Dictionary with user input
    """
    print("\n[*] XSS-Hunter requires the following information:\n")
    
    # Base URL
    while True:
        base_url = input("Base URL (e.g., https://example.com): ").strip()
        if is_valid_url(base_url):
            break
        print("[-] Invalid URL format. Please try again.")
    
    # Login URL
    while True:
        login_url = input("Login URL (press Enter to use base URL + /login): ").strip()
        if not login_url:
            login_url = base_url.rstrip('/') + '/login'
        if is_valid_url(login_url):
            break
        print("[-] Invalid URL format. Please try again.")
    
    # Ask about authentication method
    print("\n[*] Authentication Method:")
    print("    1. Browser-based manual login (Recommended for complex flows, OTP, 2FA)")
    print("    2. Automated login (Simple username/password forms only)")
    
    auth_choice = input("\nSelect authentication method (1 or 2) [1]: ").strip() or "1"
    use_browser = auth_choice == "1"
    
    username = ""
    password = ""
    
    # Only ask for credentials if using automated method
    if not use_browser:
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
     
    return {
        'base_url': base_url,
        'login_url': login_url,
        'username': username,
        'password': password,
        'use_browser': use_browser
    }


def confirm_scope(urls: List[str]):
    """
    Display and confirm URLs to be tested
    
    Args:
        urls: List of URLs
    """
    print(f"\n[*] URLs in scope: {len(urls)}")
    if len(urls) <= 10:
        for url in urls:
            print(f"    - {url}")
    else:
        for url in urls[:5]:
            print(f"    - {url}")
        print(f"    ... and {len(urls) - 5} more")
    
    print()


def main():
    """Main execution flow"""
    args = parse_arguments()
    
    # Initialize logger
    logger = Logger(output_file=args.output)
    logger.banner()
    logger.ethical_warning()
    
    # Confirm continuation
    response = input("\nDo you have authorization to test this target? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        logger.error("Authorization not confirmed. Exiting.")
        sys.exit(0)
    
    print()
    
    # Get user input
    user_input = get_user_input()
    
    # Step 1: Authentication
    logger.info("="*60)
    logger.info("STEP 1: AUTHENTICATION")
    logger.info("="*60)
    
    try:
        authenticator = Authenticator(
            login_url=user_input['login_url'],
            username=user_input['username'],
            password=user_input['password'],
            base_url=user_input['base_url'],
            logger=logger,
            use_browser=user_input['use_browser']
        )
        
        session = authenticator.authenticate()
        
    except AuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        sys.exit(1)
    
    # Step 2: Scope Discovery
    logger.info("\n" + "="*60)
    logger.info("STEP 2: SCOPE DISCOVERY")
    logger.info("="*60)
    
    urls_to_test = []
    
    # Manual URLs from file
    if args.urls:
        logger.info(f"Loading URLs from file: {args.urls}")
        urls_to_test = read_urls_from_file(args.urls)
        logger.success(f"Loaded {len(urls_to_test)} URLs from file")
    
    # Authenticated crawling
    if args.crawl:
        logger.info("Starting authenticated crawling...")
        crawler = AuthenticatedCrawler(
            session=session,
            base_url=user_input['base_url'],
            max_depth=args.max_depth,
            max_pages=args.max_pages,
            logger=logger
        )
        
        # Add manual URLs to crawler if provided
        if urls_to_test:
            crawler.add_manual_urls(urls_to_test)
        
        discovered_urls = crawler.crawl()
        urls_to_test.extend(discovered_urls)
    
    # If no URLs, use base URL only
    if not urls_to_test:
        logger.warning("No URLs provided. Will test base URL only.")
        urls_to_test = [user_input['base_url']]
    
    # Remove duplicates
    urls_to_test = list(set(urls_to_test))
    
    # Confirm scope
    confirm_scope(urls_to_test)
    
    # Step 3: XSS Scanning
    logger.info("="*60)
    logger.info("STEP 3: XSS SCANNING")
    logger.info("="*60)
    
    scanner = XSSScanner(
        session=session,
        logger=logger,
        use_advanced_payloads=args.advanced
    )
    
    vulnerabilities = scanner.scan_urls(urls_to_test)
    
    # Step 4: Results Summary
    logger.info("\n" + "="*60)
    logger.info("STEP 4: RESULTS")
    logger.info("="*60)
    
    stats = scanner.get_stats()
    logger.scan_summary(
        urls_tested=stats['urls_tested'],
        params_tested=stats['params_tested'],
        xss_found=stats['vulnerabilities_found']
    )
    
    if args.output:
        logger.success(f"Results saved to: {args.output}")
    
    logger.info("\n[*] Scan completed successfully!")
    
    # Exit with appropriate code
    sys.exit(0 if stats['vulnerabilities_found'] == 0 else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[-] Scan interrupted by user. Exiting...")
        sys.exit(130)
    except Exception as e:
        print(f"\n[-] Unexpected error: {e}")
        sys.exit(1)
