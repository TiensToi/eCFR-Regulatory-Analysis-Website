import json

# Path to your agencies.json file
AGENCIES_PATH = "../ecfr_analysis/data/raw/agencies.json"

CFR_BASE_URL = "https://www.ecfr.gov/api/v1/current/title-1/chapter-{}"

def print_title_1_urls():
    with open(AGENCIES_PATH, "r", encoding="utf-8") as f:
        agencies = json.load(f)
    def process_agency(agency):
        for ref in agency.get("cfr_references", []):
            if str(ref.get("title")) == "1":
                chapter = ref.get("chapter")
                if chapter:
                    url = CFR_BASE_URL.format(chapter)
                    print(url)
        for child in agency.get("children", []):
            process_agency(child)
    for agency in agencies:
        process_agency(agency)

if __name__ == "__main__":
    print_title_1_urls()
