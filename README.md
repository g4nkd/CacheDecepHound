# CacheDecepHound

## Overview
CacheDecepHound is a Python-based tool designed for identifying web cache deception vulnerabilities in web servers. It automates the process of testing potential vulnerabilities through origin server normalization (OSN) and custom delimiters. By leveraging multi-threading, the tool performs efficient scanning to detect caching issues, which may allow attackers to exploit vulnerable caching mechanisms to serve malicious content to users.

Additionally, CacheDecepHound employs discreet web poisoning by randomizing parameters during tests to avoid detection and minimize the impact on the site's traffic.

## Features
- **Origin Server Normalization (OSN)** testing.
- **Cache Server Normalization (CSN)** testing.
- **Custom Delimiters** to test URL path manipulations.
- **Multi-threading** for faster scans.
- **Comprehensive Header Support** for authenticated requests.
- **Verbose Output** for debugging and detailed results.
- **Configurable Test Parameters** for recursion depth, extensions, and headers.

## Prerequisites
Before running CacheDecepHound, ensure that you have the following dependencies installed:

- **Python 3.x** or higher.
- **requests** library: Install with `pip install requests`.

## Installation

To install CacheDecepHound, follow these steps:

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

## Usage

### Basic Command Structure

The basic structure of the command is:

```bash
python cdhound.py <target_url> [options]
```

### Arguments

- **`<target_url>`**: The URL of the target website to test (e.g., `https://example.com`).
- **`-H` or `--header`**: Add custom headers (e.g., for authentication) in the format `Name: Value`.
- **`-w` or `--wordlist`**: Path to a custom wordlist for delimiters (default is `/path/to/wordlist.txt`).
- **`-e` or `--extensions`**: A comma-separated list of file extensions to test (default: `.js,.css,.png`).
- **`-T` or `--technique`**: Choose testing technique. Options: `osn` (Origin Server Normalization), `csn` (Cache Server Normalization) or `default` (standard behavior).
- **`-r`**: Recursion depth for OSN testing (1, 2, or 3).
- **`-v` or `--verbose`**: Show verbose output for debugging.
- **`-t` or `--threads`**: The number of threads to use (default: 10).

## Additional Notes

- **Targeting User-Specific URLs:** It is highly recommended to test URLs that include user-specific information, such as `/profile`, `/dashboard`, or other personalized routes. These URLs are more likely to reveal cache poisoning vulnerabilities due to their dynamic content.

- **PortSwigger Wordlist:** You can use the official PortSwigger Web Cache Deception wordlist for delimiters. Download it here: [PortSwigger WCD Delimiter List](https://portswigger.net/web-security/web-cache-deception/wcd-lab-delimiter-list).

### Examples

#### 1. Basic Testing (Standard Delimiters, Extensions, OSN and CSN)
```bash
python cdhound.py https://example.com -w /path/to/wordlist.txt -e .js,.css,.png
```

#### 2. Testing only with OSN (Origin Server Normalization) Technique
```bash
python cdhound.py https://example.com -T osn -r 2
```

#### 3. Adding Custom Headers (e.g., Authentication)
```bash
python cdhound.py https://example.com -H "Authorization: Bearer <your_token>"
```

#### 4. Verbose Output and Multiple Threads
```bash
python cdhound.py https://example.com -v -t 20
```
