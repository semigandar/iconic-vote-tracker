import csv
import json
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

def main():
    api_dumps = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Capture any JSON API responses in the background
        def handle_response(response):
            try:
                if "json" in response.headers.get("content-type", ""):
                    api_dumps.append(response.text())
            except Exception:
                pass

        page.on("response", handle_response)
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(12000)  # Wait 12 full seconds for slow API responses
        text = page.inner_text("body")
        browser.close()

    print("--- VISIBLE PAGE TEXT ---")
    print(text[:1000])

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

    # Fallback: search raw JSON API data if visible text didn't render in time
    if len(results) < len(CANDIDATES):
        combined_json = "\n".join(api_dumps)
        for name in CANDIDATES:
            if name not in results:
                m = re.search(
                    re.escape(name) + r'.{0,300}?"(?:votes|vote_count|total_votes|count)"\s*:\s*(\d+)',
                    combined_json,
                    re.IGNORECASE | re.DOTALL,
                )
                if m:
                    results[name] = int(m.group(1))

    print("--- EXTRACTED RESULTS ---", results)

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
