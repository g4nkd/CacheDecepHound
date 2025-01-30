# CacheDecepHound

## Overview
**CacheDecepHound** is a Python-based tool designed to identify **web cache deception vulnerabilities** in web servers. It automates the process of testing potential vulnerabilities through **Origin Server Normalization (OSN)** and **Client-Side Normalization (CSN)** techniques. By leveraging multi-threading, the tool performs efficient scanning to detect caching issues, which may allow attackers to exploit vulnerable caching mechanisms and serve malicious content to users.

Additionally, CacheDecepHound employs **discreet web poisoning** by randomizing parameters during tests to avoid detection and minimize the impact on the site's traffic.

---

## Features
- **Origin Server Normalization (OSN)**: Test for path traversal vulnerabilities via static resource directories.
- **Client-Side Normalization (CSN)**: Test for path traversal vulnerabilities using custom delimiters.
- **Custom Delimiters**: Test URL path manipulations with a customizable wordlist.
- **Multi-threading**: Perform faster scans with configurable thread counts.
- **Proxy Support**: Route requests through a proxy for debugging or anonymity.
- **Verbose Output**: Enable detailed logging for debugging and analysis.
- **Configurable Test Parameters**: Customize recursion depth, extensions, and headers.

---

## Prerequisites
Before running CacheDecepHound, ensure you have the following installed:
- **Python 3.x** or higher.
- **Required Python libraries**: Install them using the provided `requirements.txt`.

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

## Usage

### Basic Command Structure
The basic structure of the command is:
```bash
python cdhound.py <target_url> [options]
```

### Arguments
| Argument              | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| `<target_url>`        | The URL of the target website to test (e.g., `https://example.com`).        |
| `-H`, `--header`      | Add custom headers (e.g., for authentication) in the format `Name: Value`.  |
| `-w`, `--wordlist`    | Path to a custom wordlist for delimiters (default: `delimiters-wordlist.txt`). |
| `-e`, `--extensions`  | Comma-separated list of file extensions to test (default: `.js,.css,.png`). |
| `-T`, `--technique`   | Choose testing technique: `osn`, `csn`, or `default`.                       |
| `-r`                  | Recursion depth for OSN/CSN testing (1, 2, or 3).                          |
| `-v`, `--verbose`     | Show verbose output for debugging.                                          |
| `-t`, `--threads`     | Number of threads to use (default: 10).                                     |
| `-p`, `--proxy`       | Proxy to use for requests (e.g., `http://127.0.0.1:8080`).                  |

---

## Examples

### 1. Basic Testing (Standard Delimiters, Extensions, OSN, and CSN)
```bash
python cdhound.py https://example.com -w delimiters-wordlist.txt -e .js,.css,.png
```

### 2. Testing Only with OSN (Origin Server Normalization)
```bash
python cdhound.py https://example.com -T osn -r 2
```

### 3. Adding Custom Headers (e.g., Authentication)
```bash
python cdhound.py https://example.com -H "Authorization: Bearer <your_token>"
```

### 4. Verbose Output and Multiple Threads
```bash
python cdhound.py https://example.com -v -t 20
```

### 5. Using a Proxy
```bash
python cdhound.py https://example.com -p http://127.0.0.1:8080
```

---

## Additional Notes

### Wordlists
- **Delimiters Wordlist**: Provided by [PortSwigger's Web Cache Deception Delimiter List](https://portswigger.net/web-security/web-cache-deception/wcd-lab-delimiter-list).
- **Extensions Wordlist**: Provided by [PortSwigger's Static Extensions List](https://portswigger.net/research/gotta-cache-em-all).

### Recommendations
- **Target User-Specific URLs**: Test URLs that include user-specific information, such as `/profile`, `/dashboard`, or other personalized routes. These are more likely to reveal cache poisoning vulnerabilities due to their dynamic content.
- **Stealthy Scans**: Use the `-T` option to specify a scanning technique and reduce the number of threads (`-t`) for a more discreet scan.

### Warning
The default scan may generate excessive noise and could potentially crash the application. Use caution when scanning production environments.
