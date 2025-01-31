# CacheDecepHound

This tool is designed to test for web cache deception vulnerabilities by exploiting discrepancies in how web servers and caches handle URL paths, delimiters, and static resources. It automates the process of identifying and exploiting these vulnerabilities, making it easier for security researchers and penetration testers to assess the security of web applications.

Additionally, CacheDecepHound employs **discreet web poisoning** by randomizing parameters during tests to avoid detection and minimize the impact on the site's traffic.

## Features

- **Path Delimiter Testing**: Identifies discrepancies in how delimiters are interpreted by the origin server and the cache.
- **Origin Server Normalization (OSN)**: Tests for vulnerabilities where the origin server normalizes URL paths differently than the cache.
- **Cache Server Normalization (CSN)**: Exploits discrepancies in how the cache server normalizes URL paths compared to the origin server.
- **File Name Cache Rules (FNCR)**: Tests for vulnerabilities related to how common files (e.g., `robots.txt`, `index.html`) are cached.
- **Static Resource Detection**: Automatically detects static resource directories and uses them to craft test URLs.
- **Multi-threaded Testing**: Utilizes multiple threads to speed up the testing process.
- **Verbose Output**: Provides detailed information about each test, including response headers and cache behavior.

---

## Installation

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/g4nkd/CacheDecepHound.git
   ```

2. Navigate to the project directory:
   ```bash
   cd CacheDecepHound
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

### Options

- `-H, --header`: Add a custom header to the requests (e.g., `Authorization: Bearer token`).
- `-w, --wordlist`: Path to a custom wordlist of delimiters.
- `-e, --extensions`: Comma-separated list of file extensions to test (default: `.js,.css,.png`).
- `-T, --technique`: Specify the technique to use (`pd`, `osn`, `csn`, `fncr`).
- `-r`: Recursion depth for OSN/CSN testing (default: 1).
- `-v, --verbose`: Enable verbose output.
- `-t, --threads`: Number of threads to use (default: 10).
- `-p, --proxy`: Use a proxy for requests (e.g., `http://127.0.0.1:8080`).

### Example Commands

1. **Basic Test with Default Settings**:
   ```bash
   python cache_poisoning_tool.py https://example.com
   ```

2. **Test with Custom Delimiters and Extensions**:
   ```bash
   python cache_poisoning_tool.py https://example.com -w delimiters.txt -e .js,.css,.html
   ```

3. **Test with Specific Technique (OSN)**:
   ```bash
   python cache_poisoning_tool.py https://example.com -T osn -r 2
   ```

4. **Test with Proxy and Verbose Output**:
   ```bash
   python cache_poisoning_tool.py https://example.com -p http://127.0.0.1:8080 -v
   ```

## Techniques Explained

### Path Delimiter Testing (`pd`)

This technique tests for discrepancies in how delimiters (e.g., `;`, `,`, `#`) are interpreted by the origin server and the cache. If the origin server treats a character as a delimiter but the cache does not, it may be possible to craft a URL that is interpreted differently by each, leading to cache poisoning.

### Origin Server Normalization (OSN)

OSN exploits discrepancies in how the origin server normalizes URL paths compared to the cache. For example, if the origin server resolves path traversal sequences (e.g., `/static/..%2fprofile`) but the cache does not, an attacker can craft a URL that returns sensitive information from the origin server, which is then cached and served to other users.

### Cache Server Normalization (CSN)

CSN is the inverse of OSN. It exploits cases where the cache normalizes URL paths but the origin server does not. By crafting a URL that the cache interprets differently than the origin server, an attacker can cause the cache to store and serve sensitive information.

### File Name Cache Rules (FNCR)

This technique targets cache rules that are based on specific file names (e.g., `robots.txt`, `index.html`). By appending these file names to dynamic URLs, an attacker can cause the cache to store and serve dynamic content as if it were a static file.

## Detection of Cached Responses

The tool checks for cached responses by examining response headers and response times. Key headers to look for include:

- **X-Cache**: Indicates whether the response was served from the cache.
  - `X-Cache: hit` - The response was served from the cache.
  - `X-Cache: miss` - The response was fetched from the origin server.
  - `X-Cache: dynamic` - The content was dynamically generated and is not suitable for caching.
  - `X-Cache: refresh` - The cached content was outdated and needed to be refreshed.

- **Cache-Control**: May include directives like `public` with a `max-age` higher than 0, indicating that the resource is cacheable.

Additionally, a significant difference in response time for the same request may indicate that the faster response is served from the cache.

## Exploitation of Static Extension Cache Rules

Cache rules often target static resources by matching common file extensions like `.css` or `.js`. If there are discrepancies in how the cache and origin server map the URL path to resources, an attacker may be able to craft a request for a dynamic resource with a static extension that is ignored by the origin server but viewed by the cache.

## Path Mapping Discrepancies

URL path mapping is the process of associating URL paths with resources on a server. Discrepancies in how the cache and origin server map the URL path to resources can result in web cache deception vulnerabilities. For example:

- **Traditional URL Mapping**: Represents a direct path to a resource located on the file system (e.g., `/path/in/filesystem/resource.html`).
- **RESTful URL Mapping**: Abstracts file paths into logical parts of the API (e.g., `/path/resource/param1/param2`).

If the cache uses traditional URL mapping while the origin server uses RESTful mapping, an attacker can exploit this discrepancy to cache sensitive information.

## Delimiter Discrepancies

Delimiters specify boundaries between different elements in URLs. Discrepancies in how the cache and origin server use characters and strings as delimiters can result in web cache deception vulnerabilities. For example:

- **Java Spring Framework**: Uses `;` as a delimiter for matrix variables.
- **Ruby on Rails**: Uses `.` as a delimiter to specify the response format.

If the cache does not recognize these delimiters, an attacker can craft a URL that is interpreted differently by the cache and the origin server.

## Normalization Discrepancies

Normalization involves converting various representations of URL paths into a standardized format. Discrepancies in how the cache and origin server normalize the URL can enable an attacker to construct a path traversal payload that is interpreted differently by each parser. For example:

- **Origin Server Normalization**: Decodes encoded characters and resolves dot-segments.
- **Cache Normalization**: Does not decode encoded characters or resolve dot-segments.

By exploiting these discrepancies, an attacker can cause the cache to store and serve sensitive information.

---

For more information on web cache poisoning and deception, refer to the [PortSwigger Web Security Academy](https://portswigger.net/web-security/web-cache-poisoning) and [Gotta Cache ‘em all bending the rules of web cache exploitation](https://www.youtube.com/watch?v=70yyOMFylUA).
