# Troubleshooting Guide

This guide covers common issues and their solutions when using the LinkedIn Profile Extractor.

## Table of Contents
- [Extension Issues](#extension-issues)
- [Data Extraction Issues](#data-extraction-issues)
- [File Saving Issues](#file-saving-issues)
- [CSV Processing Issues](#csv-processing-issues)
- [Debug Mode](#debug-mode)
- [LinkedIn Layout Changes](#linkedin-layout-changes)

## Extension Issues

### Extension Icon Not Appearing
- Ensure the extension is enabled in `chrome://extensions/`
- Try reloading the extension
- Check if you're in Incognito mode (extensions may be disabled)

### "Please navigate to a LinkedIn profile page" Error
**Cause**: Not on a valid LinkedIn profile URL

**Solution**:
- URL must contain `/in/` (e.g., `linkedin.com/in/username`)
- Wait for the page to fully load
- Try refreshing the page

### Extension Not Loading
**Symptoms**: Errors in chrome://extensions/

**Solutions**:
1. Check file paths in manifest.json
2. Ensure all files are in correct directories
3. Check for JavaScript syntax errors
4. Reload the extension

## Data Extraction Issues

### Missing or Incomplete Data

**Common Causes**:
1. **LinkedIn Connection Level**: You see different content based on connection
2. **Page Not Fully Loaded**: Dynamic content still loading
3. **Collapsed Sections**: "Show more" sections not expanded

**Solutions**:
- Wait 3-5 seconds after page loads
- Click "Show more" in About and Experience sections
- Ensure you're logged in to LinkedIn
- Try with a 1st-degree connection profile

### About Section Not Extracted

**Debug Steps**:
1. Enable debug mode (see below)
2. Check if About section exists on profile
3. Look for this structure in DevTools:
   ```html
   <section>
     <div id="about">
   ```

### Experience Data Issues

**Problem**: Roles/companies mixed up or duplicated

**Common Scenarios**:
- Company with multiple roles showing incorrectly
- Role descriptions in wrong fields
- Missing job descriptions

**Solutions**:
1. Check if all experience items are expanded
2. For complex work histories, manually verify JSON output
3. Report specific profile structures that fail

### Location Shows Duration

**Cause**: LinkedIn's inconsistent HTML structure

**Solution**: The extension tries to filter out duration from location, but some edge cases may slip through. Check the JSON file and manually correct if needed.

## File Saving Issues

### Files Not Downloading

**Check**:
1. Chrome download settings (Settings → Downloads)
2. Popup blockers or security software
3. Disk space availability
4. Download folder permissions

### Files Saving to Wrong Location

**Solution**:
- Files always save to `Downloads/LinkedIn_Profiles/YYYY-MM/`
- Chrome may have a different default download location
- Check Chrome Settings → Downloads → Location

### HTML File Not Saving

**Possible Causes**:
- Very large profiles may exceed size limits
- Special characters in profile causing issues

**Solution**:
- Try with a simpler profile first
- Check browser console for errors

## CSV Processing Issues

### Python Script Not Finding Files

**Common Issues**:
1. **Wrong Downloads folder path**
   ```python
   # Check your actual Downloads path
   downloads_dir = str(Path.home() / "Downloads")
   print(f"Looking in: {downloads_dir}")
   ```

2. **Files in different location**
   - Script looks in Downloads and all subdirectories
   - Ensure files have `linkedin_` prefix

### CSV Fields Empty or Incorrect

**Debug**:
1. Open a JSON file to verify data structure
2. Check for special characters breaking CSV
3. Run script with single file first:
   ```python
   # Test with one file
   test_file = "path/to/your/linkedin_file.json"
   ```

### Unicode/Encoding Errors

**Solution**:
```python
# Already handled in script with utf-8-sig encoding
# If issues persist, check for corrupted JSON files
```

## Debug Mode

### Enabling Debug Mode

1. Edit `extension/content.js`:
   ```javascript
   // Line 4 - Change to true
   const ENABLE_DEBUG = true;
   ```

2. Reload extension in Chrome

3. Open DevTools (F12) on LinkedIn profile

4. Try extraction and check Console tab

### What Debug Mode Shows

- Element selection process
- Data being extracted
- Which methods succeed/fail
- Full extracted data object

### Debug Output Examples

```javascript
// Good extraction
Found top-level experience items: 3
Processing company with sub-roles: TechCorp
Added sub-role: {role: "Senior Engineer", company: "TechCorp", ...}

// Failed extraction
About section: ""  // Empty means extraction failed
Experience extracted: []  // Empty array means no items found
```

## LinkedIn Layout Changes

### Detecting Layout Changes

**Symptoms**:
- Previously working extraction now fails
- Specific fields always empty
- Console errors about null elements

### Temporary Fixes

1. **Inspect Element**: Right-click on missing data → Inspect
2. **Find New Selectors**: Look for unique classes/IDs
3. **Test in Console**:
   ```javascript
   // Test new selector
   document.querySelector('YOUR_NEW_SELECTOR')?.textContent
   ```

### Reporting Issues

When reporting, include:
1. Profile URL (or type: personal/company/premium)
2. What data is missing
3. Debug mode output
4. Screenshot of the profile section

## Quick Fixes Checklist

- [ ] Logged in to LinkedIn
- [ ] On a `/in/username` profile page
- [ ] Page fully loaded (wait 5 seconds)
- [ ] Clicked "Show more" sections
- [ ] Extension reloaded recently
- [ ] Not in Incognito mode
- [ ] Chrome downloads enabled
- [ ] Sufficient disk space

## Getting Help

1. **Check existing issues**: GitHub Issues page
2. **Enable debug mode**: Get detailed error info
3. **Create minimal test case**: Try with public profile
4. **Include details**: Browser version, error messages, screenshots

## Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "Cannot read property 'textContent' of null" | Element not found | LinkedIn layout changed |
| "Downloads.download failed" | Save blocked | Check Chrome settings |
| "No profiles found to process" | Wrong directory | Check file locations |
| "Invalid JSON in file" | Corrupted save | Re-extract profile |

---

Remember: LinkedIn regularly updates their interface. If extraction stops working, check for extension updates or report the issue with details about what changed.