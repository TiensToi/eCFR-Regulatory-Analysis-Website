
import requests
import os
import json
import time

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'ecfr_analysis', 'data', 'raw'))
AGENCIES_URL = "https://www.ecfr.gov/api/admin/v1/agencies.json"
# Example CFR endpoint: https://www.ecfr.gov/api/v1/current/title-7/chapter-I
CFR_BASE_URL = "https://www.ecfr.gov/api/v1/current/title-{}/chapter-{}"
DELAY_SECONDS = 1.5  # Adjust as needed to avoid rate limiting

def fetch_agencies_and_cfr():
    print(f"OUT_DIR is: {OUT_DIR}")
    os.makedirs(OUT_DIR, exist_ok=True)
    # Fetch agencies list
    r = requests.get(AGENCIES_URL)
    if r.status_code != 200:
        print(f"Failed to fetch agencies: Status {r.status_code}")
        return
    agencies = r.json().get("agencies", [])
    with open(os.path.join(OUT_DIR, "agencies.json"), "w", encoding="utf-8") as f:
        json.dump(agencies, f, indent=2)
    print("Saved agencies list to agencies.json")

    def process_agency(agency):
        # Fetch CFR data for each cfr_reference
        for ref in agency.get("cfr_references", []):
            title = ref.get("title")
            chapter = ref.get("chapter")
            if title and chapter:
                url = CFR_BASE_URL.format(title, chapter)
                print(f"Trying URL: {url}")
                resp = requests.get(url)
                print(f"Status for {url}: {resp.status_code}")
                if resp.status_code == 200:
                    out_file = os.path.join(OUT_DIR, f"title_{title}_chapter_{chapter}.json")
                    with open(out_file, "w", encoding="utf-8") as f:
                        json.dump(resp.json(), f)
                    print(f"Saved Title {title} Chapter {chapter} to {out_file}")
                elif resp.status_code == 404:
                    print(f"Not found: Title {title} Chapter {chapter} (404)")
                elif resp.status_code == 429:
                    print(f"Rate limited (429). Waiting {DELAY_SECONDS*2} seconds and retrying...")
                    time.sleep(DELAY_SECONDS*2)
                    resp = requests.get(url)
                    print(f"Retry status for {url}: {resp.status_code}")
                    if resp.status_code == 200:
                        out_file = os.path.join(OUT_DIR, f"title_{title}_chapter_{chapter}.json")
                        with open(out_file, "w", encoding="utf-8") as f:
                            json.dump(resp.json(), f)
                        print(f"Saved Title {title} Chapter {chapter} to {out_file}")
                    else:
                        print(f"Failed after retry: Title {title} Chapter {chapter}: Status {resp.status_code}")
                else:
                    print(f"Failed to fetch Title {title} Chapter {chapter}: Status {resp.status_code}")
                time.sleep(DELAY_SECONDS)
        # Recursively process children
        for child in agency.get("children", []):
            process_agency(child)

    # Only process agencies with a cfr_reference for title 1
    for agency in agencies:
        has_title_1 = any(ref.get("title") == "1" for ref in agency.get("cfr_references", []))
        if has_title_1:
            process_agency(agency)
    # Commented out: process all agencies for all titles
    # for agency in agencies:
    #     process_agency(agency)

if __name__ == "__main__":
    fetch_agencies_and_cfr()
