import requests
import os

# GPO eCFR bulk XML URL (latest daily edition)
GPO_XML_URL = "https://www.govinfo.gov/bulkdata/ECFR/title-1/ECFR-title1.xml"
# You can change the URL for other titles or editions as needed

RAW_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'ecfr_analysis', 'data', 'raw'))
os.makedirs(RAW_DIR, exist_ok=True)

out_path = os.path.join(RAW_DIR, "ECFR-title1.xml")

print(f"Downloading Title 1 XML from {GPO_XML_URL} ...")
resp = requests.get(GPO_XML_URL)
if resp.status_code == 200:
    with open(out_path, "wb") as f:
        f.write(resp.content)
    print(f"Saved to {out_path}")
else:
    print(f"Failed to download: status {resp.status_code}")
