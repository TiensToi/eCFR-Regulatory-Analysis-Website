import os
import glob
from parse_title1_xml import parse_title1_xml

RAW_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw'))

def parse_all_titles(raw_dir):
    xml_files = glob.glob(os.path.join(raw_dir, 'ECFR-title*.xml'))
    print(f"Found {len(xml_files)} XML files to parse.")
    for xml_path in xml_files:
        title_num = os.path.splitext(os.path.basename(xml_path))[0].replace('ECFR-title', '')
        json_path = os.path.join(raw_dir, f'title{title_num}_parsed.json')
        print(f"Parsing Title {title_num}: {xml_path} -> {json_path}")
        try:
            parse_title1_xml(xml_path, json_path)
            print(f"Parsed and saved: {json_path}")
        except Exception as e:
            print(f"Failed to parse {xml_path}: {e}")

if __name__ == "__main__":
    print("parse_all_titles.py script started")
    parse_all_titles(RAW_DIR)
