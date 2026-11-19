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
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()
        page.goto(URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(6000)
        text = page.inner_text("body")
        browser.close()

    print("PAGE TEXT SAMPLE:", text[:500].replace("\n", " | "))

    results = {}
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for i, line in enumerate(lines):
        upper_line = line.upper()
        for name in CANDIDATES:
            if name in upper_line:
                for lookahead in lines[i : i + 10]:
                    match = re.search(r"([\d,]+)\s*votes?", lookahead, re.IGNORECASE)
                    if match:
                        results[name] = int(match.group(1).replace(",", ""))
                        break
    return results

def main():
    results = {}
    for attempt in range(3):
        results = scrape_votes()
        print(f"Attempt {attempt + 1} results:", results)
        if len(results) == len(CANDIDATES):
            break

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
