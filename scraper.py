import csv
import os
import re
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

URL = "https://iconicawards.pro"
CSV_FILE = "votes.csv"

CANDIDATES = [
    "HON. MINISTER OF ENJOYMENT",
    "JB ON HIS BIKE",
    "1TRABO",
    "JAWADU SONKO",
]

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(4000)
        text = page.inner_text("body")
        browser.close()

    results = {}
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for i, line in enumerate(lines):
        upper_line = line.upper()
        for name in CANDIDATES:
            if name in upper_line:
                for lookahead in lines[i + 1 : i + 6]:
                    match = re.search(r"([\d,]+)\s*votes?", lookahead, re.IGNORECASE)
                    if match:
                        results[name] = int(match.group(1).replace(",", ""))
                        break

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp (UTC)"] + CANDIDATES)
        row = [timestamp] + [results.get(c, "") for c in CANDIDATES]
        writer.writerow(row)

if __name__ == "__main__":
    main()
