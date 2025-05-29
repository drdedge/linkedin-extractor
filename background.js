/* ----------  LinkedIn Profile Extractor – background.js  ---------- */

const DEBUG = true;
const log = (...a) => DEBUG && console.log('[LPE-bg]', ...a);

/* ---- 1. Handle saveHtml messages from content.js ------------------------ */
chrome.runtime.onMessage.addListener((req, sender, sendResponse) => {
    if (req.action !== 'saveHtml') return;

    const ts = new Date().toISOString().replace(/[:.]/g, '-');
    const file = `LinkedIn_Profiles/2025-05/linkedin_${req.name}_${ts}.html`;

    log('Downloading', file);
    chrome.downloads.download(
        {
            url: 'data:text/html;charset=utf-8,' + encodeURIComponent(req.html),
            filename: file,
            saveAs: false,
            conflictAction: 'uniquify'
        },
        (id) => {
            if (chrome.runtime.lastError) {
                log('❌ download failed:', chrome.runtime.lastError.message);
                flashBadge(sender.tab?.id, false);
                sendResponse({ ok: false });
            } else {
                log('✅ download id', id);
                flashBadge(sender.tab?.id, true);
                sendResponse({ ok: true });
            }
        }
    );
    return true;
});

function flashBadge(tabId, ok) {
    if (!tabId) return;
    chrome.action.setBadgeText({ text: ok ? '✓' : '⋯', tabId });
    chrome.action.setBadgeBackgroundColor({ color: ok ? '#4CAF50' : '#E53935', tabId });
    setTimeout(() => chrome.action.setBadgeText({ text: '', tabId }), 1200);
}

/* ---- 2. Re-inject content.js on every SPA navigation -------------------- */
chrome.webNavigation.onHistoryStateUpdated.addListener(
    (d) => {
        if (d.frameId !== 0 || !d.url.includes('/in/')) return;

        chrome.storage.local.get({ autoSaveEnabled: true }, (s) => {
            if (!s.autoSaveEnabled) return;     // switch OFF – do nothing

            chrome.scripting.executeScript(
                { target: { tabId: d.tabId }, files: ['content.js'] },
                () => {
                    if (chrome.runtime.lastError) {
                        log('❌ executeScript:', chrome.runtime.lastError.message);
                    } else {
                        log('🔄 content.js reinjected');
                    }
                }
            );
        });
    },
    { url: [{ hostEquals: 'www.linkedin.com', pathPrefix: '/in/' }] }
);
