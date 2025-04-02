#!/usr/bin/env python3
import requests
import re
import hashlib
from urllib.parse import urljoin, urlparse

class StealthShellHunter:
    def __init__(self):
        self.banner = r"""
 
  ____ _______   ___     _____ ___  _  _   
 / ___|_   _\ \ / / |   | ____/ _ \| || |  
 \___ \ | |  \ V /| |   |  _|| | | | || |_ 
  ___) || |   | | | |___| |__| |_| |__   _|
 |____/ |_|   |_| |_____|_____\___/   |_|  
               SHELL BY STYLE04                            
"""
        
        # Signature common shell functions
        self.shell_patterns = [
            r"eval\(base64_decode\(",
            r"system\(\$_GET\['cmd'\]\)",
            r"passthru\(\$_REQUEST\['command'\]\)",
            r"shell_exec\(\$_POST\['execute'\]\)",
            r"<\?php @ini_set\(\'display_errors\'\,\'0\'\)\;",
            r"<\?php \$[a-z]\=\$_GET\['[a-z]'\]\;eval\(\$[a-z]\)\;"
        ]
        
        # Known shell hashes (md5 of common shells)
        self.known_hashes = {
            "c99": "b8e8ae9f9c7b87d3c6f5b6e9d7a8b5c9",
            "r57": "5d4ae4df5c377a7e0a4e5f5c5e4d5f4a",
            "b374k": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"
        }

    def scan_url(self, base_url):
        print(f"\033[1;34m{self.banner}\033[0m")
        print(f"\n\033[1;32m[+] Target: {base_url}\033[0m")
        
        # Get all links from page
        links = self.extract_links(base_url)
        
        print(f"\n\033[1;33m[+] Found {len(links)} pages to scan\033[0m")
        
        for link in links:
            if self.is_suspicious(link):
                print(f"\n\033[1;35m[*] Checking: {link}\033[0m")
                self.deep_scan(link)

    def extract_links(self, url):
        try:
            r = requests.get(url, timeout=5)
            return re.findall(r'href=[\'"]?([^\'" >]+)', r.text)
        except:
            return []

    def is_suspicious(self, url):
        # Check suspicious extensions
        suspicious_ext = ['.php', '.phtml', '.inc', '.phar']
        return any(url.lower().endswith(ext) for ext in suspicious_ext)

    def deep_scan(self, url):
        try:
            r = requests.get(url, timeout=3)
            
            # Check 1: Known hash detection
            file_hash = hashlib.md5(r.content).hexdigest()
            for name, known_hash in self.known_hashes.items():
                if file_hash == known_hash:
                    print(f"\033[1;31m[!] KNOWN SHELL DETECTED: {url} ({name} shell)\033[0m")
                    return
            
            # Check 2: Pattern matching
            content = r.text.lower()
            for pattern in self.shell_patterns:
                if re.search(pattern, content):
                    print(f"\033[1;31m[!] SHELL CODE DETECTED: {url}\033[0m")
                    print(f"    Pattern: {pattern[:50]}...")
                    return
            
            # Check 3: Parameter analysis
            if '?' in url:
                params = urlparse(url).query
                if any(cmd in params.lower() for cmd in ['cmd=', 'exec=', 'command=']):
                    print(f"\033[1;33m[!] SUSPICIOUS PARAMS: {url}\033[0m")
            
        except Exception as e:
            print(f"\033[1;90m[-] Di temukan {url}: {str(e)[:50]}\033[0m")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 shell.py <url>")
        sys.exit(1)
    
    hunter = StealthShellHunter()
    hunter.scan_url(sys.argv[1])
