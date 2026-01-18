"""
Logger Module - Professional output formatting
"""
from datetime import datetime
from typing import Optional


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Logger:
    """Professional logging with color and structure"""
    
    def __init__(self, output_file: Optional[str] = None):
        self.output_file = output_file
        
    def _log(self, message: str, color: str = "", to_file: bool = True):
        """Internal logging method"""
        colored_msg = f"{color}{message}{Colors.ENDC}" if color else message
        print(colored_msg)
        
        if to_file and self.output_file:
            with open(self.output_file, 'a') as f:
                # Strip color codes for file
                clean_msg = message
                f.write(f"{clean_msg}\n")
    
    def banner(self):
        """Display tool banner"""
        banner = f"""
{Colors.BOLD}{Colors.OKCYAN}
╔═══════════════════════════════════════════════════════════╗
║                      XSS-HUNTER                          ║
║           Authenticated XSS Scanner v1.0                 ║
║                  Author: dark_hunter                     ║
╚═══════════════════════════════════════════════════════════╝
{Colors.ENDC}
"""
        print(banner)
    
    def info(self, message: str):
        """Info message"""
        self._log(f"[*] {message}", Colors.OKBLUE)
    
    def success(self, message: str):
        """Success message"""
        self._log(f"[+] {message}", Colors.OKGREEN)
    
    def warning(self, message: str):
        """Warning message"""
        self._log(f"[!] {message}", Colors.WARNING)
    
    def error(self, message: str):
        """Error message"""
        self._log(f"[-] {message}", Colors.FAIL)
    
    def xss_found(self, url: str, method: str, parameter: str, payload: str, xss_type: str, context: str = ""):
        """Report XSS vulnerability"""
        msg = f"""
{Colors.BOLD}{Colors.OKGREEN}[+] XSS FOUND{Colors.ENDC}
{Colors.BOLD}URL:{Colors.ENDC} {url}
{Colors.BOLD}Method:{Colors.ENDC} {method}
{Colors.BOLD}Parameter:{Colors.ENDC} {parameter}
{Colors.BOLD}Payload:{Colors.ENDC} {payload}
{Colors.BOLD}Type:{Colors.ENDC} {xss_type}"""
        
        if context:
            msg += f"\n{Colors.BOLD}Context:{Colors.ENDC} {context}"
        
        msg += "\n" + "="*60
        print(msg)
        
        if self.output_file:
            clean_msg = f"""
[+] XSS FOUND
URL: {url}
Method: {method}
Parameter: {parameter}
Payload: {payload}
Type: {xss_type}"""
            if context:
                clean_msg += f"\nContext: {context}"
            clean_msg += "\n" + "="*60
            
            with open(self.output_file, 'a') as f:
                f.write(f"{clean_msg}\n")
    
    def scan_summary(self, urls_tested: int, params_tested: int, xss_found: int):
        """Display scan summary"""
        msg = f"""
{Colors.BOLD}{Colors.HEADER}
╔═══════════════════════════════════════════════════════════╗
║                    SCAN SUMMARY                          ║
╚═══════════════════════════════════════════════════════════╝
{Colors.ENDC}
{Colors.BOLD}URLs Tested:{Colors.ENDC} {urls_tested}
{Colors.BOLD}Parameters Tested:{Colors.ENDC} {params_tested}
{Colors.BOLD}XSS Vulnerabilities Found:{Colors.ENDC} {xss_found}
"""
        print(msg)
        
        if xss_found == 0:
            self.warning("No XSS detected with current payloads and scope")
            self.info("This does not guarantee 100% security")
        
        if self.output_file:
            clean_msg = f"""
SCAN SUMMARY
============
URLs Tested: {urls_tested}
Parameters Tested: {params_tested}
XSS Vulnerabilities Found: {xss_found}
"""
            with open(self.output_file, 'a') as f:
                f.write(f"{clean_msg}\n")
    
    def ethical_warning(self):
        """Display ethical use warning"""
        warning = f"""
{Colors.BOLD}{Colors.WARNING}⚠️  ETHICAL USE WARNING ⚠️{Colors.ENDC}

This tool is for {Colors.BOLD}AUTHORIZED TESTING ONLY{Colors.ENDC}.

By using this tool, you agree that:
  • You have explicit permission to test the target
  • You will not use destructive payloads
  • You will not cause account lockouts or data deletion
  • You accept full responsibility for your actions

{Colors.FAIL}Unauthorized access to computer systems is illegal.{Colors.ENDC}
"""
        print(warning)
