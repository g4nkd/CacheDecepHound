import requests
import random
import string
import sys
import urllib.parse
from typing import List, Tuple, Dict
import argparse
from concurrent.futures import ThreadPoolExecutor

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

def check_cache_behavior(url: str, headers: Dict[str, str]) -> Tuple[str, bool, Dict]:
    """
    Check if URL is vulnerable to cache poisoning.
    Returns (URL, is_vulnerable, debug_info)
    """
    try:
        # Add default User-Agent to provided headers
        request_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        request_headers.update(headers)

        debug_info = {}

        # First request
        first_response = requests.get(url, headers=request_headers)
        first_cache = first_response.headers.get('X-Cache', '')
        debug_info['first_status'] = first_response.status_code
        debug_info['first_cache'] = first_cache

        # Second request
        second_response = requests.get(url, headers=request_headers)
        second_cache = second_response.headers.get('X-Cache', '')
        debug_info['second_status'] = second_response.status_code
        debug_info['second_cache'] = second_cache

        # Strict check for cache behavior
        is_vulnerable = (
            first_cache and second_cache and  # Both headers must exist
            'miss' in first_cache.lower() and  # First must be a miss
            'hit' in second_cache.lower() and  # Second must be a hit
            first_response.status_code == 200 and  # Both responses should be successful
            second_response.status_code == 200
        )

        return url, is_vulnerable, debug_info

    except requests.exceptions.RequestException as e:
        print(f"Error testing {url}: {str(e)}")
        return url, False, {}

def main():
    parser = argparse.ArgumentParser(description='Test for web cache poisoning vulnerabilities')
    parser.add_argument('url', help='Target URL')
    parser.add_argument('-H', '--header', help='Header in format "Name: Value"')
    parser.add_argument('-w', '--wordlist', help='Path to custom wordlist', default='/path/to/wordlist.txt')
    parser.add_argument('-e', '--extensions', help='Comma-separated list of extensions to test (default: ".js,.css,.png")', default='.js,.css,.png')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads to use (default: 10)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    args = parser.parse_args()

    headers = {}
    if args.header:
        headers.update(parse_header(args.header))

    print(f"[*] Testing cache behavior for: {args.url}")
    print(f"[*] Using headers: {headers}")
    print(f"[*] Reading delimiters from: {args.wordlist}")

    delimiters = read_delimiters(args.wordlist)
    extensions = [ext.strip() for ext in args.extensions.split(',') if ext.strip()]

    print(f"[*] Loaded {len(delimiters)} delimiters from wordlist")
    print(f"[*] Using {len(extensions)} extensions: {extensions}")

    test_urls = create_test_urls(args.url, delimiters, extensions)
    print(f"[*] Generated {len(test_urls)} test URLs")
    print("-" * 60)

    def process_url(url):
        url, is_vulnerable, debug_info = check_cache_behavior(url, headers)
        if is_vulnerable:
            print(f"\n[!] VULNERABLE URL FOUND!\n[!] URL: {url}")
            print(f"[!] Cache behavior: {debug_info.get('first_cache')} -> {debug_info.get('second_cache')}")
        elif args.verbose:
            print(f"[+] Tested: {url} | Not vulnerable")

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        executor.map(process_url, test_urls)

if __name__ == "__main__":
    main()
