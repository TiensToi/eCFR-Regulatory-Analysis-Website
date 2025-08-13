
import os
import json
import hashlib
import re
import datetime
from textstat import flesch_kincaid_grade




def extract_text(data):
    # Recursively extract all text fields from nested sections
    if isinstance(data, dict):
        text = ""
        for v in data.values():
            text += extract_text(v) + " "
        return text.strip()
    elif isinstance(data, list):
        return " ".join([extract_text(item) for item in data])
    elif isinstance(data, str):
        return data
    else:
        return ""





def save_metrics_history(metrics, processed_dir):
    history_path = os.path.join(processed_dir, 'metrics_history.json')
    timestamp = datetime.datetime.now().isoformat()
    entry = {'timestamp': timestamp, 'metrics': metrics}
    # Load existing history
    if os.path.exists(history_path):
        with open(history_path, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = []
    history.append(entry)
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)




def analyze():
    metrics = {}
    base_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..', '..', 'ecfr_analysis', 'data'
        )
    )
    raw_dir = os.path.join(base_dir, 'raw')
    processed_dir = os.path.join(base_dir, 'processed')
  
    os.makedirs(processed_dir, exist_ok=True)
    metrics_path = os.path.join(processed_dir, 'metrics.json')
    for fname in os.listdir(raw_dir):
        if not fname.endswith('.json'):
            continue
        with open(os.path.join(raw_dir, fname), "r", encoding="utf-8") as f:
            data = json.load(f)
        text = extract_text(data)
        wc = len(text.split())
        checksum = hashlib.md5(text.encode()).hexdigest()
        readability = flesch_kincaid_grade(text)
        metrics[fname] = {
            "word_count": wc,
            "checksum": checksum,
            "readability": readability
        }
    # Save metrics to metrics.json
    with open(metrics_path, 'w', encoding='utf-8') as out:
        json.dump(metrics, out, indent=2)
    # Save to metrics_history.json
    save_metrics_history(metrics, processed_dir)





def extract_cross_references(parsed_json_path, output_path):
    part_ref_re = re.compile(r"part\s*\d+", re.IGNORECASE)
    with open(parsed_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    cross_refs = []
    # Improved regex patterns with word boundaries and expanded types
    section_ref_re = re.compile(
        r"\b(?:§|section)\s*\d+(?:\.\d+)?\b", re.IGNORECASE
    )
    subpart_ref_re = re.compile(r"\bsubpart\s*[A-Z]+\b", re.IGNORECASE)
    appendix_ref_re = re.compile(r"\bappendix\s*[A-Z]+\b", re.IGNORECASE)

    title_ref_re = re.compile(r"\btitle\s*\d+\b", re.IGNORECASE)
    usc_ref_re = re.compile(
        r"\b\d+\s*U\.S\.C\.(?:\s*§)?\s*\d+\b", re.IGNORECASE
    )
    context_re = re.compile(
        r"(see|as provided in|as described in|according to|under|pursuant to|in accordance with)",
        re.IGNORECASE
    )
    for part in data.get('parts', []):
        part_heading = part.get('part_heading', '')
  
        for section in part.get('sections', []):
            section_heading = section.get('heading', '')
            for para in section.get('paragraphs', []):
                # Only extract if a contextual phrase is present
                if not context_re.search(para):
                    continue
                refs = set()
                refs.update(section_ref_re.findall(para))
                refs.update(part_ref_re.findall(para))
                refs.update(subpart_ref_re.findall(para))
                refs.update(appendix_ref_re.findall(para))
                refs.update(title_ref_re.findall(para))
                refs.update(usc_ref_re.findall(para))
                if refs:
                    cross_refs.append({
                        'part_heading': part_heading,
                        'section_heading': section_heading,
                        'paragraph': para,
                        'references': sorted(refs)
                    })
    with open(output_path, 'w', encoding='utf-8') as out:
        json.dump(cross_refs, out, indent=2)





def resolve_and_count_citations(parsed_json_path, crossref_path, output_path):
    with open(parsed_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(crossref_path, 'r', encoding='utf-8') as f:
        cross_refs = json.load(f)
    # Build lookup for section and part headings
    section_lookup = {}
    part_lookup = {}
    for part in data.get('parts', []):
        part_heading = part.get('part_heading', '')
        part_num_match = re.search(r'PART\s*(\d+)', part_heading, re.IGNORECASE)
        if part_num_match:
            part_num = part_num_match.group(1)
            part_lookup[f'part {part_num}'] = part_heading
        for section in part.get('sections', []):
            section_heading = section.get('heading', '')
            sect_num_match = re.search(r'§\s*(\d+(?:\.\d+)?)', section_heading)
            if sect_num_match:
                sect_num = sect_num_match.group(1)
                section_lookup[f'section {sect_num}'] = section_heading
                section_lookup[f'§ {sect_num}'] = section_heading
    # Count citations
    citation_counts = {}
    resolved_refs = []
    for ref in cross_refs:
        for r in ref['references']:
            resolved = None
            if r.lower() in section_lookup:
                resolved = section_lookup[r.lower()]
                citation_counts[resolved] = citation_counts.get(resolved, 0) + 1
            elif r.lower() in part_lookup:
                resolved = part_lookup[r.lower()]
                citation_counts[resolved] = citation_counts.get(resolved, 0) + 1
            else:
                citation_counts[r] = citation_counts.get(r, 0) + 1
            resolved_refs.append({
                'reference': r,
                'resolved_to': resolved
            })
    # Output
    with open(output_path, 'w', encoding='utf-8') as out:
        json.dump({
            'citation_counts': citation_counts,
            'resolved_references': resolved_refs
        }, out, indent=2)


  


def generate_cross_reference_graph(parsed_json_path, crossref_path, output_path):
    with open(parsed_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(crossref_path, 'r', encoding='utf-8') as f:
        cross_refs = json.load(f)
    # Build nodes for all sections and parts
    nodes = []
    node_ids = set()
    for part in data.get('parts', []):
        part_heading = part.get('part_heading', '')
        if part_heading and part_heading not in node_ids:
            nodes.append({'id': part_heading, 'type': 'part'})
            node_ids.add(part_heading)
        for section in part.get('sections', []):
            section_heading = section.get('heading', '')
            if section_heading and section_heading not in node_ids:
                nodes.append({
                    'id': section_heading,
                    'type': 'section',
                    'part': part_heading
                })
                node_ids.add(section_heading)
    # Build edges from cross-references
    edges = []
    for ref in cross_refs:
        source = ref['section_heading']
        for target in ref['references']:
            # Try to resolve to a node id (section or part)
            target_id = None
            for n in nodes:
                if n['id'].lower().startswith(target.lower()):
                    target_id = n['id']
                    break
            if target_id:
                edges.append({
                    'source': source,
                    'target': target_id,
                    'label': f"{source} references {target_id}"
                })
            else:
                edges.append({
                    'source': source,
                    'target': target,
                    'label': f"{source} references {target}"
                })
    with open(output_path, 'w', encoding='utf-8') as out:
        json.dump({'nodes': nodes, 'edges': edges}, out, indent=2)





def compute_part_section_metrics(parsed_json_path, output_path):
    with open(parsed_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    results = []
    for part in data.get('parts', []):
        part_heading = part.get('part_heading', '')
        part_text = ''
        for section in part.get('sections', []):
            for para in section.get('paragraphs', []):
                part_text += para + ' '
        part_word_count = len(part_text.split())
        part_readability = (
            flesch_kincaid_grade(part_text) if part_text else 0
        )
        results.append({
            'level': 'part',
            'part_heading': part_heading,
            'section_heading': '',
            'word_count': part_word_count,
            'readability': part_readability
        })
        for section in part.get('sections', []):
            section_heading = section.get('heading', '')
            section_text = ' '.join(section.get('paragraphs', []))
            section_word_count = len(section_text.split())
            section_readability = (
                flesch_kincaid_grade(section_text) if section_text else 0
            )
            results.append({
                'level': 'section',
                'part_heading': part_heading,
                'section_heading': section_heading,
                'word_count': section_word_count,
                'readability': section_readability
            })
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)



if __name__ == "__main__":
    analyze()
    # Cross-reference extraction for title1_parsed.json
    base_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..', '..', 'ecfr_analysis', 'data'
        )
    )
    parsed_json_path = os.path.join(
        base_dir, 'raw', 'title1_parsed.json'
    )
    crossref_output_path = os.path.join(
        base_dir, 'processed', 'cross_references.json'
    )
    extract_cross_references(parsed_json_path, crossref_output_path)
    citation_counts_path = os.path.join(
        base_dir, 'processed', 'citation_counts.json'
    )
    resolve_and_count_citations(
        parsed_json_path, crossref_output_path, citation_counts_path
    )
    graph_output_path = os.path.join(
        base_dir, 'processed', 'cross_reference_graph.json'
    )
    generate_cross_reference_graph(
        parsed_json_path, crossref_output_path, graph_output_path
    )
    part_section_metrics_path = os.path.join(
        base_dir, 'processed', 'part_section_metrics.json'
    )
    compute_part_section_metrics(
        parsed_json_path, part_section_metrics_path
    )
