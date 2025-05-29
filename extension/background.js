// Background script for LinkedIn Profile Extractor

// Listen for extension installation
chrome.runtime.onInstalled.addListener(() => {
    chrome.action.setBadgeBackgroundColor({ color: '#0077B5' });
});

// Listen for tab updates to show badge when on LinkedIn profile
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.includes('linkedin.com/in/')) {
        chrome.action.setBadgeText({ text: '●', tabId: tabId });
        chrome.action.setBadgeBackgroundColor({ color: '#0077B5', tabId: tabId });
    } else if (changeInfo.status === 'complete') {
        chrome.action.setBadgeText({ text: '', tabId: tabId });
    }
});

// Listen for messages
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'saveProfile') {
        saveProfileData(request.data, request.html);
        sendResponse({ success: true });
    } else if (request.action === 'pageReady') {
        // Page is ready for extraction
        chrome.action.setBadgeText({ text: '✓', tabId: sender.tab.id });
        chrome.action.setBadgeBackgroundColor({ color: '#4CAF50', tabId: sender.tab.id });
    }
});

// Save profile data as JSON file and HTML with organization
function saveProfileData(profileData, pageHTML) {
    if (!profileData) return;

    // Create organized filename with subfolder
    const date = new Date();
    const yearMonth = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    const timestamp = date.toISOString().replace(/[:.]/g, '-');
    const safeName = profileData.name ? profileData.name.replace(/[^a-z0-9]/gi, '_').toLowerCase() : 'unknown';

    // Base filename without extension
    const baseFilename = `LinkedIn_Profiles/${yearMonth}/linkedin_${safeName}_${timestamp}`;

    // Save JSON file
    const jsonFilename = `${baseFilename}.json`;
    const jsonData = JSON.stringify(profileData, null, 2);
    const jsonDataUrl = 'data:application/json;charset=utf-8,' + encodeURIComponent(jsonData);

    chrome.downloads.download({
        url: jsonDataUrl,
        filename: jsonFilename,
        saveAs: false,
        conflictAction: 'uniquify'
    });

    // Save HTML file if provided
    if (pageHTML) {
        const htmlFilename = `${baseFilename}.html`;
        const htmlDataUrl = 'data:text/html;charset=utf-8,' + encodeURIComponent(pageHTML);

        chrome.downloads.download({
            url: htmlDataUrl,
            filename: htmlFilename,
            saveAs: false,
            conflictAction: 'uniquify'
        });
    }
}