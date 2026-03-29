"""
inspect_aa.py — Diagnostic: dump all interactive elements on aa.com booking page.
Run once to discover real selectors, then update american.py accordingly.

Usage:
    python automation/inspect_aa.py
"""

import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT = Path("automation/aa_elements.json")

def main():
    with sync_playwright() as p:
        launch_args = dict(
            headless=False,
            slow_mo=100,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
        )
        try:
            browser = p.chromium.launch(channel="chrome", **launch_args)
        except Exception:
            browser = p.chromium.launch(**launch_args)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        print("[inspect] Navigating to aa.com/booking/find-flights ...")
        page.goto("https://www.aa.com/booking/find-flights", timeout=30000)

        print("[inspect] Waiting for page to settle (8s) ...")
        time.sleep(8)

        print(f"[inspect] Current URL : {page.url}")
        print(f"[inspect] Page title  : {page.title()}")

        # Dump raw HTML for manual inspection
        html = page.content()
        Path("automation/aa_page.html").write_text(html, encoding="utf-8")
        print(f"[inspect] HTML length : {len(html)} chars -> automation/aa_page.html")

        print("[inspect] Collecting all inputs, buttons, selects, and labels ...")

        elements = page.evaluate("""() => {
            const tags = ['input', 'button', 'select', 'textarea', '[role="combobox"]',
                          '[role="radio"]', '[role="button"]', '[role="listbox"]'];
            const results = [];
            tags.forEach(tag => {
                document.querySelectorAll(tag).forEach(el => {
                    results.push({
                        tag: el.tagName.toLowerCase(),
                        id: el.id || null,
                        name: el.name || null,
                        type: el.type || null,
                        role: el.getAttribute('role') || null,
                        'data-testid': el.getAttribute('data-testid') || null,
                        'aria-label': el.getAttribute('aria-label') || null,
                        'aria-labelledby': el.getAttribute('aria-labelledby') || null,
                        placeholder: el.placeholder || null,
                        value: el.value || null,
                        className: el.className || null,
                        visible: el.offsetParent !== null,
                        text: el.innerText ? el.innerText.trim().slice(0, 80) : null,
                    });
                });
            });
            return results;
        }""")

        OUTPUT.write_text(json.dumps(elements, indent=2))
        print(f"[inspect] Wrote {len(elements)} elements to {OUTPUT}")
        print("[inspect] Review automation/aa_elements.json for real selectors.")
        print("[inspect] Press Enter to close the browser.")
        try:
            input()
        except EOFError:
            pass
        browser.close()

if __name__ == "__main__":
    main()
