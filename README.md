# CacheDecepHound

CacheDecepHound is a Python-based tool designed to identify web cache poisoning vulnerabilities on web servers. It automates the testing of GET URLs using customizable delimiters and extensions, focusing on potential cache poisoning issues, while leveraging multi-threading for fast and efficient scanning.

## Features
- **Custom wordlist support**: Specify your own list of delimiters to test using `-w`.
- **Configurable extensions**: Define extensions to append to test URLs using `-e`.
- **Multi-threading**: Speed up the testing process by running multiple URL checks in parallel using `-t`.
- **Header customization**: Add custom HTTP headers using `-H`.
- **Verbose mode**: Get detailed output for each request and response with `-v`.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/g4nkd/CacheDecepHound.git
   cd CacheDecepHound
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
```bash
python cachedecephound.py <URL>
```

### Options
| Argument               | Description                                                                                  |
|------------------------|----------------------------------------------------------------------------------------------|
| `<URL>`               | The target URL to test.                                                                      |
| `-w`, `--wordlist`     | Path to a custom wordlist for delimiters (default: `/path/to/wordlist.txt`). |
| `-e`, `--extensions`   | Comma-separated list of file extensions to test (default: `.js,.css,.png`).                      |
| `-H`, `--header`       | Add a custom HTTP header in the format `Name: Value`.                                        |
| `-t`, `--threads`      | Number of threads to use for testing (default: 10).                                          |
| `-v`, `--verbose`      | Enable verbose output for detailed request/response logging.                                 |

### Examples

1. Test a URL with default settings:
   ```bash
   python cachedecephound.py https://example.com
   ```

2. Use a custom wordlist and test with additional extensions:
   ```bash
   python cachedecephound.py https://example.com -w /path/to/wordlist.txt -e .html,.php,.json
   ```

3. Add custom headers and increase the number of threads:
   ```bash
   python cachedecephound.py https://example.com -H "X-Test: TestHeader" -t 20
   ```

4. Enable verbose mode to see detailed output:
   ```bash
   python cachedecephound.py https://example.com -v
   ```

## Additional Notes

- **Targeting User-Specific URLs:** It is highly recommended to test URLs that include user-specific information, such as `/profile`, `/dashboard`, or other personalized routes. These URLs are more likely to reveal cache poisoning vulnerabilities due to their dynamic content.

- **PortSwigger Wordlist:** You can use the official PortSwigger Web Cache Deception wordlist for delimiters. Download it here: [PortSwigger WCD Delimiter List](https://portswigger.net/web-security/web-cache-deception/wcd-lab-delimiter-list).

## How It Works

1. **Delimiters and Extensions**: The tool generates test URLs by combining the provided delimiters and extensions with the target URL.
2. **HTTP Requests**: Each generated URL is tested with two requests to observe the `X-Cache` headers and detect cache behavior.
3. **Vulnerability Detection**: If the first request results in a `miss` and the second in a `hit`, the URL is flagged as potentially vulnerable.

## Output
- **Verbose mode**: Displays detailed information for each request, including the status code and `X-Cache` headers.
- **Vulnerable URLs**: Clearly highlighted in the output with details about cache behavior.
