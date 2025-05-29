/* ----------  content.js  ---------- */
(() => {
    /* 1. If we’ve been injected before, just call the existing capture fn ---- */
    if (window.__LPE_CAPTURE__) {
        window.__LPE_CAPTURE__();             // ← fire capture for this profile
        return;                               // no redeclaration errors
    }

    /* 2. First-time set-up ---------------------------------------------------- */
    const DEBUG = false;
    const dbg = (...a) => DEBUG && console.log('[LPE]', ...a);

    chrome.storage.local.get({ autoSaveEnabled: true }, (s) => {
        if (!s.autoSaveEnabled) { dbg('Auto-save OFF – idle'); return; }
        hookRouter();
        captureWhenStable();                  // initial load
    });

    /* ----------------------------------------------------------------------- */
    function hookRouter() {
        let last = location.href;
        const fire = () => {
            if (location.href === last) return;
            last = location.href;
            dbg('URL →', last);
            if (last.includes('/in/')) captureWhenStable();
        };
        ['pushState', 'replaceState'].forEach(fn => {
            const o = history[fn]; history[fn] = function () { const r = o.apply(this, arguments); fire(); return r; };
        });
        window.addEventListener('popstate', fire);
    }

    async function captureWhenStable() {
        const name = (await waitForName())
            .replace(/[^a-z0-9]/gi, '_').toLowerCase() || 'unknown';

        await scrollToBottomAndWait();        // ensure lazy sections loaded

        const html = document.documentElement.outerHTML;
        dbg('Send', html.length, 'bytes for', name);
        chrome.runtime.sendMessage({ action: 'saveHtml', name, html });
    }

    function waitForName(t = 10_000) {
        return new Promise(res => {
            const start = Date.now();
            (function loop() {
                const h1 = document.querySelector('h1');
                if (h1 && h1.textContent.trim()) return res(h1.textContent.trim());
                if (Date.now() - start > t) return res('unknown');
                setTimeout(loop, 100);
            })();
        });
    }

    function scrollToBottomAndWait() {
        return new Promise(res => {
            let lastH = 0;
            (function step() {
                const h = document.body.scrollHeight;
                window.scrollTo(0, h);
                if (h === lastH) { setTimeout(res, 1000); }
                else { lastH = h; setTimeout(step, 400); }
            })();
        });
    }

    /* 3. Expose the capture function for future injections ------------------ */
    window.__LPE_CAPTURE__ = captureWhenStable;
})();
