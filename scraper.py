import csv
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

URL = "https://iconicawards.pro"
CSV_FILE = "votes.csv"

CANDIDATES = [
    "HON. MINISTER OF ENJOYMENT",
    "JB ON HIS BIKE",
    "1TRABO",
    "JAWADU SONKO",
]

def scrape_votes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        
        # Wait up to 30 seconds until a number followed by "votes" actually appears on the page
        page.wait_for_function(
            "() => /\\d[\\d,]*\\s*votes/i.test(document.body.innerText)",
            timeout=30000
        )
        page.wait_for_timeout(1500)
        text = page.inner_text("body")
        browser.close()

    results = {}
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for i, line in enumerate(lines):
        upper_line = line.upper()
        for name in CANDIDATES:
            if name in upper_line:
                for lookahead in lines[i : i + 8]:
                    match = re.search(r"([\d,]+)\s*votes?", lookahead, re.IGNORECASE)
                    if match:
                        results[name] = int(match.group(1).replace(",", ""))
                        break
    return results

def main():
    results = {}
    for attempt in range(3):  # Retries up to 3 times if the site is temporarily slow
        try:
            results = scrape_votes()
            if len(results) == len(CANDIDATES):
                break
        except Exception:
            pass

    timestamp = datetime.now(ZoneInfo("Africa/Kampala")).strftime("%Y-%m-%d %H:%M:%S EAT")
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp (EAT)"] + CANDIDATES)
        row = [timestamp] + [results.get(c, "") for c in CANDIDATES]
        writer.writerow(row)

if __name__ == "__main__":
    main()
