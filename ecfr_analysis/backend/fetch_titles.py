

import os
import requests

def download_all_titles(raw_dir):
    titles_url = "https://www.ecfr.gov/api/versioner/v1/titles"
    r = requests.get(titles_url)
    r.raise_for_status()
    titles = r.json().get("titles", [])
    not_found = []
    saved = 0
    for title in titles:
        title_num = title.get("number")
        if not title_num:
            print(f"No title number in entry: {title}")
            continue
        xml_url = f"https://www.govinfo.gov/bulkdata/ECFR/title-{title_num}/ECFR-title{title_num}.xml"
        out_path = os.path.join(raw_dir, f"ECFR-title{title_num}.xml")
        print(f"Downloading Title {title_num} XML from {xml_url} ...", end=" ")
        resp = requests.get(xml_url, allow_redirects=True)
        print(f"Status code: {resp.status_code}")
        if resp.ok and resp.content and len(resp.content) > 1000:
            with open(out_path, "wb") as f:
                f.write(resp.content)
            print(f"Saved to {out_path}")
            saved += 1
        else:
            print(f"Not found or empty (status {resp.status_code}) for Title {title_num}")
            not_found.append(title_num)
    print("\nSummary:")
    print(f"  Titles saved: {saved}")
    print(f"  Titles not found: {len(not_found)} -> {not_found}")

if __name__ == "__main__":
    print("fetch_titles.py script started")
    try:
        raw_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'data', 'raw'))
        print(f"Raw directory: {raw_dir}")
        os.makedirs(raw_dir, exist_ok=True)
        download_all_titles(raw_dir)
    except Exception as e:
        print(f"Exception occurred: {e}")