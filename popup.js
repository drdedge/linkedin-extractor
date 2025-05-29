document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('toggle');
    const msg = document.getElementById('msg');

    chrome.storage.local.get({ autoSaveEnabled: true }, (data) => {
        toggle.checked = data.autoSaveEnabled;
        render();
    });

    toggle.addEventListener('change', () => {
        chrome.storage.local.set({ autoSaveEnabled: toggle.checked }, render);
    });

    function render() {
        msg.textContent = toggle.checked
            ? '✅ Auto-save is ON. Every LinkedIn profile you open will be archived.'
            : '⏸ Auto-save is OFF. No profiles will be saved until you turn it back on.';
    }
});
