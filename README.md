# LinkedIn Profile Extractor

A privacy-focused Chrome extension that extracts LinkedIn profile data locally and saves it as structured JSON files, with tools to convert to CSV for CRM import.

![Chrome Extension](https://img.shields.io/badge/Chrome-Extension-green.svg)
![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Quick Start

1. **Install the Extension**
   ```bash
   git clone https://github.com/drdedge/linkedin-profile-extractor.git
   cd linkedin-profile-extractor
   ```
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the `extension` folder

2. **Extract a Profile**
   - Navigate to any LinkedIn profile
   - Click the extension icon
   - Click "Extract Profile Data"
   - Files save to `Downloads/LinkedIn_Profiles/YYYY-MM/`

3. **Convert to CSV**
   ```bash
   python scripts/process_linkedin_data.py
   ```

## 📋 Features

- ✅ **Comprehensive Data Extraction**
  - Name, headline, location
  - About section
  - Complete work experience (handles multiple roles per company)
  - Education history
  - Profile URL and connections count

- ✅ **Smart File Organization**
  - Auto-organizes by year-month folders
  - Timestamps in filenames
  - Saves both JSON and HTML

- ✅ **CRM Ready**
  - Generates Salesforce-compatible CSV
  - Proper field mapping
  - Bulk processing support

- ✅ **Privacy First**
  - All processing happens locally
  - No data sent to external servers
  - No API keys required

## 📁 Project Structure

```
linkedin-profile-extractor/
├── extension/              # Chrome extension files
│   ├── manifest.json
│   ├── content.js
│   ├── background.js
│   ├── popup.html
│   ├── popup.js
│   └── icons/
│       ├── icon16.png
│       ├── icon48.png
│       └── icon128.png
├── scripts/               # Processing scripts
│   └── process_linkedin_data.py
├── docs/                  # Additional documentation
│   └── TROUBLESHOOTING.md
├── README.md
├── LICENSE
└── .gitignore
```

## 🛠️ Installation

### Prerequisites
- Google Chrome browser
- Python 3.6+ (for CSV conversion)
- No additional Chrome permissions needed beyond active tab access

### Detailed Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/drdedge/linkedin-profile-extractor.git
   cd linkedin-profile-extractor
   ```

2. **Install the Chrome Extension**
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)
   - Click "Load unpacked"
   - Select the `extension` folder from this repository
   - The extension icon should appear in your toolbar

3. **Python Dependencies** (for CSV processing)
   ```bash
   # No external dependencies required - uses standard library only
   python --version  # Ensure Python 3.6+
   ```

## 📖 Usage Guide

### Extracting LinkedIn Profiles

1. **Navigate** to a LinkedIn profile (must be logged in to LinkedIn)
2. **Wait** for the page to fully load
3. **Click** the extension icon in your toolbar
4. **Click** "Extract Profile Data" button
5. **Check** your Downloads folder for:
   - `LinkedIn_Profiles/YYYY-MM/linkedin_name_timestamp.json`
   - `LinkedIn_Profiles/YYYY-MM/linkedin_name_timestamp.html`

### Converting to CSV

Run the Python script to process all extracted profiles:

```bash
python scripts/process_linkedin_data.py
```

This creates two CSV files in your current directory:
- `linkedin_profiles_YYYYMMDD_HHMMSS.csv` - All extracted data
- `salesforce_import_YYYYMMDD_HHMMSS.csv` - Salesforce-ready format

### JSON Data Structure

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "url": "https://www.linkedin.com/in/username/",
  "profileId": "username",
  "name": "John Doe",
  "headline": "Senior Software Engineer at TechCorp",
  "location": "San Francisco, CA",
  "about": "Passionate about building scalable systems...",
  "connections": "500+ connections",
  "experience": [
    {
      "role": "Senior Software Engineer",
      "company": "TechCorp",
      "duration": "Jan 2020 - Present",
      "location": "San Francisco, CA",
      "description": "Leading backend development..."
    }
  ],
  "education": [
    {
      "school": "Stanford University",
      "degree": "BS Computer Science",
      "years": "2016 - 2020"
    }
  ]
}
```

## 🐛 Troubleshooting

### Common Issues

1. **"Please navigate to a LinkedIn profile page"**
   - Ensure you're on a profile URL: `linkedin.com/in/username`
   - The page must be fully loaded

2. **Missing Data**
   - LinkedIn shows different content based on connection level
   - Try clicking "Show more" sections before extracting
   - Check if you're logged in to LinkedIn

3. **Extraction Not Working**
   - Enable debug mode in `content.js` (set `ENABLE_DEBUG = true`)
   - Check Chrome DevTools Console for errors
   - LinkedIn may have updated their layout - check for updates

### Debug Mode

To enable detailed logging:

1. Edit `extension/content.js` line 4:
   ```javascript
   const ENABLE_DEBUG = true;
   ```
2. Reload the extension in Chrome
3. Open DevTools (F12) and check Console tab

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Keep data processing local - no external API calls
- Test with various LinkedIn profile types
- Update selectors when LinkedIn changes their layout
- Maintain backward compatibility with existing JSON files

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚖️ Legal Notice

This tool is designed for personal use to export your own LinkedIn connections and profiles you have legitimate access to. Users are responsible for:
- Complying with LinkedIn's Terms of Service
- Respecting rate limits and not automating bulk extraction
- Using extracted data in accordance with privacy laws
- Not using this tool for unauthorized data collection

## 🔒 Privacy

- All data extraction and processing happens locally in your browser
- No data is sent to external servers
- No analytics or tracking
- Your LinkedIn credentials are never accessed or stored

## 🙏 Acknowledgments

- Built with vanilla JavaScript for maximum compatibility
- Uses Chrome Extension Manifest V3 for security
- Python script uses only standard library for easy deployment


---

**Note**: This is an unofficial tool and is not affiliated with LinkedIn. LinkedIn is a trademark of LinkedIn Corporation.