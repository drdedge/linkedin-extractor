# LinkedIn Profile Extractor Development Guide

## Commands
- **Extension Loading**: `chrome://extensions/` → Developer mode → Load unpacked → select `extension` folder
- **Python Parser**: `python scripts/linkedin_profile_parser.py <HTML_FILE_OR_DIR>`
- **Dependencies**: `pip install beautifulsoup4 click tqdm lxml`

## Code Style
- **JavaScript**: Vanilla JS with IIFE pattern, no semicolons, single quotes, 4-space indentation
- **Naming**: camelCase for variables/functions, UPPER_CASE for constants
- **Error Handling**: Debug messages through `dbg()` wrapper, toggle with `DEBUG = true/false`
- **Chrome API**: Use chrome.* APIs for storage, messaging, and downloads
- **Python**: Use f-strings, type hints, PEP 8 style, 4-space indentation

## Project Structure
- `extension/`: Chrome extension files (content.js, background.js, popup.js)
- `scripts/`: Python scripts for offline processing
- `docs/`: Documentation files