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
    """Print colorful ASCII art logo."""
    green = '\033[32m'
    bright_green = '\033[92m'
    reset = '\033[0m'

    logo = f"""
{green}╔══════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║   ██████╗ █████╗  ██████╗██╗  ██╗███████╗██████╗ ███████╗ ██████╗███████╗║
║  ██╔════╝██╔══██╗██╔════╝██║  ██║██╔════╝██╔══██╗██╔════╝██╔════╝██╔════╝║
║  ██║     ███████║██║     ███████║█████╗  ██║  ██║█████╗  ██║     █████╗  ║
║  ██║     ██╔══██║██║     ██╔══██║██╔══╝  ██║  ██║██╔══╝  ██║     ██╔══╝  ║
║  ╚██████╗██║  ██║╚██████╗██║  ██║███████╗██████╔╝███████╗╚██████╗███████╗║
║   ╚═════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝ ╚═════╝╚══════╝║
║                    {bright_green}██╗  ██╗ ██████╗ ██╗   ██╗███╗   ██╗██████╗{green}        ║
║                    {bright_green}██║  ██║██╔═══██╗██║   ██║████╗  ██║██╔══██╗{green}       ║
║                    {bright_green}███████║██║   ██║██║   ██║██╔██╗ ██║██║  ██║{green}       ║
║                    {bright_green}██╔══██║██║   ██║██║   ██║██║╚██╗██║██║  ██║{green}       ║
║                    {bright_green}██║  ██║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝{green}       ║
║                    {bright_green}╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝{green}        ║
║                                                                            ║
║              {bright_green}Web Cache Deception & Poisoning Scanner{green}                    ║
║                                                                            ║
╚══════════════════════════════════════════════════════════════════════════╝
                                                            {bright_green}by gankd{reset}
"""
    print(logo)

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
    """
    Extract static resource directories from response body and root path.
    
    Args:
        response_text: The response text from the original endpoint
        url: The original URL to extract base domain
        headers: Request headers to use
        
    Returns:
        List[str]: List of discovered static directories in the format '/static', '/css', etc.
    """
    static_paths = []

    # Extract paths from 'href=' attributes in the response text
    href_paths_from_response = re.findall(r'href=["\'](\/(?:css|js|images?|static)[^"\'>]*)', response_text)
    static_paths.extend([path for path in href_paths_from_response if path.startswith(('/', '/static', '/css', '/js'))])

    # Make request to root path
    try:
        base_url = urllib.parse.urljoin(url, '/')
        root_response = requests.get(base_url, headers=headers, timeout=15)
        href_paths_from_root = re.findall(r'href=["\'](\/(?:css|js|images?|static)[^"\'>]*)', root_response.text)
        static_paths.extend([path for path in href_paths_from_root if path.startswith(('/', '/static', '/css', '/js'))])
    except requests.exceptions.RequestException as e:
        print(f"\033[33m[!] Warning: Could not fetch root path (/): {str(e)}\033[0m")
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(static_paths))


def create_osn_test_urls(base_url: str, static_dirs: List[str], recursion_depth: int) -> List[str]:
    """Create test URLs for origin server normalization testing, with randomization."""
    parsed_url = urllib.parse.urlparse(base_url)
    original_path = parsed_url.path.strip('/')
    test_urls = []

    for static_dir in static_dirs:
        parts = static_dir.split('/')
        for i in range(min(recursion_depth, len(parts))):
            path_prefix = '/'.join(parts[:i+1])
            random_string = generate_random_chars()
            test_url = f"{parsed_url.scheme}://{parsed_url.netloc}/{path_prefix}/..%2f{original_path}?{random_string}"
            test_urls.append(test_url)

    return test_urls

def create_csn_test_urls(base_url: str, static_dirs: List[str], delimiters: List[str], recursion_depth: int) -> List[str]:
    """Create test URLs for semi-static normalization testing with randomization."""
    parsed_url = urllib.parse.urlparse(base_url)
    original_path = parsed_url.path.strip('/')
    test_urls = []

    for static_dir in static_dirs:
        parts = static_dir.split('/')
        for i in range(min(recursion_depth, len(parts))):
            path_prefix = '/'.join(parts[:i+1])
            for delimiter in delimiters:
                random_chars = generate_random_chars()
                test_url = f"{parsed_url.scheme}://{parsed_url.netloc}/{original_path}{delimiter}%2f%2e%2e%2f{path_prefix}?{random_chars}"
                test_urls.append(test_url)

    return test_urls

def create_test_urls(base_url: str, delimiters: List[str], extensions: List[str]) -> List[str]:
    """Create test URLs with different delimiters and extensions."""
    urls = []

    for delimiter in delimiters:
        for ext in extensions:
            random_chars = generate_random_chars()
            parsed_url = urllib.parse.urlparse(base_url)
            path = parsed_url.path.rstrip('/')

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

def check_cache_behavior(url: str, headers: Dict[str, str], verbose: bool = False) -> Tuple[str, bool, Dict]:
    """
    Check if URL is vulnerable to cache poisoning.
    Returns (URL, is_vulnerable, debug_info)
    """
    try:
        request_headers = {
            'User-Agent': 'r4nd0m'
        }
        request_headers.update(headers)

        debug_info = {}

        # Set a 15-second timeout to avoid long request delays
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
        )
        
        return url, is_vulnerable, debug_info

    except requests.exceptions.Timeout:
        if verbose:
            print(f"\033[33m[!] Timeout: {url} took longer than 15 seconds and was ignored.\033[0m")
        return url, False, {}
    
    except requests.exceptions.RequestException as e:
        if verbose:
            print(f"Error testing {url}: {str(e)}")
        return url, False, {}

def main():
    print_logo()

    parser = argparse.ArgumentParser(description='Test for web cache poisoning vulnerabilities')
    parser.add_argument('url', help='Target URL')
    parser.add_argument('-H', '--header', help='Header in format "Name: Value" -> Used to authenticate the requests')
    parser.add_argument('-w', '--wordlist', help='Path to custom wordlist', default='/path/to/wordlist.txt')
    parser.add_argument('-e', '--extensions', help='Comma-separated list of extensions to test (default: ".js,.css,.png")', default='.js,.css,.png')
    parser.add_argument('-T', '--technique', choices=['osn', 'csn', 'default'], help='Recognition technique (default: standard behavior). If "osn", tests Exploiting origin server normalization. If "csn", tests cache server normalization.')
    parser.add_argument('-r', type=int, choices=[1, 2, 3], help='Recursion depth for OSN/SSN testing (1,2 or 3)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads to use (default: 10)')
    args = parser.parse_args()

    headers = {}
    if args.header:
        headers.update(parse_header(args.header))

    print(f"\n[*] Testing cache behavior for: {args.url}")
    print(f"[*] Using headers: {headers}")

    if args.technique in ['osn', 'csn']:
        if not args.r:
            print(f"[!] Error: When using '-T {args.technique}', you must specify the recursion depth with '-r' (1,2 or 3).")
            sys.exit(1)
        
        try:
            initial_response = requests.get(args.url, headers=headers)
            static_dirs = extract_static_directories(initial_response.text, args.url, headers)
            if static_dirs:
                print(f"\033[32m[*] Found {len(static_dirs)} static resource directories:\033[0m")
                for dir in static_dirs:
                    print(f"   - {dir}")
                
                if args.technique == 'osn':
                    print(f"[*] Testing origin server normalization with recursion depth: {args.r}")
                    test_urls = create_osn_test_urls(args.url, static_dirs, args.r)
                else:  # csn technique
                    print(f"[*] Testing cache server normalization with recursion depth: {args.r}")
                    delimiters = read_delimiters(args.wordlist)
                    print(f"[*] Loaded {len(delimiters)} delimiters from wordlist")
                    test_urls = create_csn_test_urls(args.url, static_dirs, delimiters, args.r)
            else:
                print("[!] No static resource directories found")
                test_urls = []
        except requests.exceptions.RequestException as e:
            print(f"[!] Error making initial request: {str(e)}")
            sys.exit(1)
    else:  # Default technique
        delimiters = read_delimiters(args.wordlist)
        extensions = [ext.strip() for ext in args.extensions.split(',') if ext.strip()]
        print(f"[*] Loaded {len(delimiters)} delimiters from wordlist")
        print(f"[*] Using {len(extensions)} extensions: {extensions}")
        test_urls = create_test_urls(args.url, delimiters, extensions)

    print(f"\033[32m[*] Generated {len(test_urls)} test URLs\033[0m")
    print("-" * 60)

    def process_url(url):
        url, is_vulnerable, debug_info = check_cache_behavior(url, headers, args.verbose)
        if is_vulnerable:
            print(f"\033[32m[!] VULNERABLE URL FOUND!\033[0m")
            print(f"\033[32m[!] URL: {url}\033[0m")
            print(f"[!] Cache behavior: {debug_info.get('first_cache')} -> {debug_info.get('second_cache')}")
            print("[!] Authenticated content leaked to unauthenticated user!")
        elif args.verbose:
            print(f"[+] Tested: {url} | Not vulnerable")

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        executor.map(process_url, test_urls)

if __name__ == "__main__":
    main()
