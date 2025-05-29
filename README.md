# LinkedIn Profile Extractor Chrome Extension

A Chrome extension that extracts LinkedIn profile data and saves it as JSON files for import into Salesforce. Also saves the full HTML page for future reference.

## Features

- Extracts key profile information:
  - Name
  - Headline
  - Location
  - About section
  - Experience (all positions with proper role hierarchy)
  - Education
  - Profile URL
  - Number of connections
- Saves data as timestamped JSON files
- Saves full HTML page for future extraction needs
- Organizes files in year-month subfolders
- Python script to convert JSON files to CSV for Salesforce import

## Installation

1. Create a new folder for the extension (e.g., `linkedin-extractor`)

2. Add these files to the folder:
   - `manifest.json`
   - `content.js`
   - `background.js`
   - `popup.html`
   - `popup.js`
   - `icon16.png`, `icon48.png`, `icon128.png` (create simple icon images or use placeholders)

3. Load the extension in Chrome:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" (top right)
   - Click "Load unpacked"
   - Select your extension folder

## Usage

### Extracting Profiles

1. Navigate to any LinkedIn profile (e.g., https://www.linkedin.com/in/username/)
2. Wait for the page to fully load
3. Click the extension icon in your toolbar
4. Click "Extract Profile Data"
5. Files will be automatically saved to:
   - `Downloads/LinkedIn_Profiles/YYYY-MM/linkedin_name_timestamp.json`
   - `Downloads/LinkedIn_Profiles/YYYY-MM/linkedin_name_timestamp.html`

### Processing JSON Files

1. Save the `process_linkedin_data.py` script
2. Run the script:
   ```bash
   python process_linkedin_data.py
   ```
3. The script will:
   - Find all LinkedIn JSON files in your Downloads folder (including subfolders)
   - Create a general CSV with all data
   - Create a Salesforce-ready CSV with mapped fields

## File Organization

Files are automatically organized by year and month:
```
Downloads/
└── LinkedIn_Profiles/
    ├── 2024-01/
    │   ├── linkedin_john_doe_2024-01-15T10-30-00.json
    │   ├── linkedin_john_doe_2024-01-15T10-30-00.html
    │   ├── linkedin_jane_smith_2024-01-15T11-00-00.json
    │   └── linkedin_jane_smith_2024-01-15T11-00-00.html
    └── 2024-02/
        └── ...
```

## JSON File Format

Each extracted profile creates a JSON file with this structure:

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "url": "https://www.linkedin.com/in/username/",
  "profileId": "username",
  "name": "John Doe",
  "headline": "Senior Software Engineer at Company",
  "location": "San Francisco, CA",
  "about": "Professional summary...",
  "connections": "500+ connections",
  "experience": [
    {
      "role": "Senior Software Engineer",
      "company": "Company Name",
      "duration": "Jan 2020 - Present",
      "location": "San Francisco, CA",
      "description": "Job description..."
    }
  ],
  "education": [
    {
      "school": "University Name",
      "degree": "Bachelor of Science - Computer Science",
      "years": "2012 - 2016"
    }
  ]
}
```

## Salesforce Import

The `salesforce_import_*.csv` file is formatted for Salesforce Lead import with these fields:
- FirstName
- LastName
- Title (Current Role)
- Company (Current Company)
- Description (About section)
- LeadSource (set to "LinkedIn")
- Website (LinkedIn URL)

## Debugging

If extraction isn't working properly:

1. Open `content.js` and change line 4:
   ```javascript
   const ENABLE_DEBUG = true;
   ```

2. Reload the extension in Chrome Extensions page
3. Open Chrome DevTools (F12) on the LinkedIn profile page
4. Click the extension and try extracting again
5. Check the Console tab for detailed logs showing:
   - What elements are being found
   - What data is being extracted
   - Any errors that occur

Remember to set `ENABLE_DEBUG = false` when done debugging.

## Notes

- The extension handles complex LinkedIn profile structures, including companies with multiple roles
- HTML files are saved for future reference or additional extraction needs
- LinkedIn's layout may change, requiring updates to the selectors in `content.js`
- Respect LinkedIn's terms of service and rate limits
- Add email addresses and phone numbers manually or through enrichment services

## Troubleshooting

- **"Please navigate to a LinkedIn profile page"**: Make sure you're on a profile URL (contains `/in/`)
- **No data extracted**: Ensure the page is fully loaded before clicking extract
- **Missing data**: LinkedIn shows different content based on your connection level with the profile
- **Experience roles mixed up**: The extension now properly handles nested company/role structures