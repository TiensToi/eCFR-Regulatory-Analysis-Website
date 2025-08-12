import os
import xml.etree.ElementTree as ET
import json

RAW_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'ecfr_analysis','data', 'raw'))
xml_path = os.path.join(RAW_DIR, 'ECFR-title1.xml')
json_path = os.path.join(RAW_DIR, 'title1_parsed.json')

def parse_title1_xml(xml_path, json_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    def get_texts(elem, tag):
        # Get all text from all tags of a certain type under elem
        return [ET.tostring(e, encoding='unicode', method='text').strip() for e in elem.findall(tag)]

    def get_all_text(elem):
        # Recursively get all text in an element and its children
        if elem is None:
            return ''
        text = elem.text or ''
        for child in elem:
            text += get_all_text(child)
            if child.tail:
                text += child.tail
        return text

    def parse_section(section):
        heading = section.findtext('HEAD', default='')
        ps = section.findall('P')
        paras = [get_all_text(p).strip() for p in ps]
        return {
            'heading': heading.strip(),
            'paragraphs': paras
        }

    def parse_part(part):
        part_heading = part.findtext('HEAD', default='')
        sections = []
        for section in part.findall("DIV8[@TYPE='SECTION']"):
            sections.append(parse_section(section))
        return {
            'part_heading': part_heading.strip(),
            'sections': sections
        }

    # Find all PARTs (DIV5 with TYPE='PART')
    parts = []
    for part in root.findall(".//DIV5[@TYPE='PART']"):
        parts.append(parse_part(part))

    # Save as JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({'parts': parts}, f, indent=2)
    print(f"Parsed Title 1 XML and saved to {json_path}")

if __name__ == "__main__":
    parse_title1_xml(xml_path, json_path)
