
import streamlit as st
import json
import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from typing import List


# Set data paths
RAW_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw'))
PROCESSED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed'))

def get_available_titles() -> List[str]:
    files = os.listdir(RAW_DIR)
    titles = [f for f in files if f.startswith('title') and f.endswith('_parsed.json')]
    return sorted(titles)

def get_title_label(fname):
    if fname.startswith('title') and '_parsed' in fname:
        num = fname.split('title')[1].split('_')[0]
        return f'Title {num}'
    return fname

available_titles = get_available_titles()
if not available_titles:
    st.error('No parsed title files found in data/raw/.')
    st.stop()

st.title('eCFR Regulatory Analysis Dashboard')
st.markdown('''
<span title="This dashboard allows you to explore regulatory metrics, trends, and cross-references for eCFR Titles. Use the controls below to select and compare titles, parts, and sections. Tooltips and help icons are available throughout for guidance.">ℹ️</span>
''', unsafe_allow_html=True)

# Title selection for multi-title support
import re
available_titles = sorted(available_titles, key=lambda x: int(re.search(r'title(\d+)_parsed\.json', x).group(1))
)


selected_titles = st.multiselect('Select Title(s) to analyze', available_titles, default=available_titles[:1], format_func=get_title_label, help="Choose one or more titles to view and compare.")
st.info('Currently, only the Metrics Table supports multi-title selection. Other dashboard features are not yet implemented for multi-title and will display informational messages below.')
if not selected_titles:
    st.warning('Please select at least one title.')
    st.stop()

# Load processed data (assume one set for now, but structure for multi-title)

import numpy as np
import hashlib
import re as regex

# Caching for processed data
@st.cache_data(show_spinner=False)
def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# Load and aggregate metrics for selected titles
def flesch_kincaid(text):
    # Basic Flesch-Kincaid grade level calculation
    sentences = regex.split(r'[.!?]+', text)
    sentences = [s for s in sentences if s.strip()]
    num_sentences = max(len(sentences), 1)
    words = regex.findall(r'\w+', text)
    num_words = max(len(words), 1)
    syllables = sum(len(regex.findall(r'[aeiouyAEIOUY]+', w)) for w in words)
    if num_words == 0:
        return np.nan
    return round(0.39 * (num_words / num_sentences) + 11.8 * (syllables / num_words) - 15.59, 2)

def compute_metrics(parsed):
    # Flatten all text from all paragraphs
    all_text = []
    word_count = 0
    if 'parts' in parsed:
        for part in parsed['parts']:
            for section in part.get('sections', []):
                for para in section.get('paragraphs', []):
                    all_text.append(para)
    text = ' '.join(all_text)
    word_count = len(regex.findall(r'\w+', text))
    readability = flesch_kincaid(text) if text else np.nan
    checksum = hashlib.md5(text.encode('utf-8')).hexdigest() if text else ''
    return word_count, readability, checksum

def load_selected_titles_metrics(selected_titles):
    data = []
    for fname in selected_titles:
        path = os.path.join(RAW_DIR, fname)
        parsed = load_json(path)
        if parsed:
            # Compute metrics if missing
            word_count = parsed.get('word_count')
            readability = parsed.get('readability')
            checksum = parsed.get('checksum')
            if word_count is None or readability is None or checksum is None:
                word_count, readability, checksum = compute_metrics(parsed)
            metrics = {
                'Title': get_title_label(fname),
                'Word Count': word_count,
                'Readability': readability,
                'Checksum': checksum,
            }
            data.append(metrics)
    return pd.DataFrame(data)

st.markdown(
    'Displays overall metrics (word count, readability, checksum) for each selected title. '
    '<span title="Word count: total words in the file. Readability: Flesch-Kincaid '
    'grade level. Checksum: MD5 hash for file integrity.">[?]</span>',
    unsafe_allow_html=True

)

# Display metrics table for selected titles
metrics_df = load_selected_titles_metrics(selected_titles)
st.dataframe(metrics_df, use_container_width=True)

 


# Metrics Table for selected titles
st.header('Metrics Table')
metrics_df = load_selected_titles_metrics(selected_titles)
if not metrics_df.empty:
    st.dataframe(metrics_df, use_container_width=True)
    csv = metrics_df.to_csv(index=False).encode('utf-8')
    st.download_button('Download Metrics Table (CSV)', csv, 'metrics.csv', 'text/csv')
else:
    st.warning('No metrics available for selected titles.')


# Part/Section Metrics Table (show Title 1 data only)
st.header('Part and Section Metrics')
st.markdown('Explore metrics for each part and section. Use filters and download the table for further analysis. Outliers are highlighted. <span title="Word count: total words in the part/section. Readability: Flesch-Kincaid grade level.">❓</span>', unsafe_allow_html=True)
part_section_metrics = None
import_path = os.path.join(PROCESSED_DIR, 'part_section_metrics.json')
if os.path.exists(import_path):
    with open(import_path, 'r', encoding='utf-8') as f:
        part_section_metrics = json.load(f)
if part_section_metrics:
    df_ps = pd.DataFrame(part_section_metrics)
    # Filtering
    level_options = df_ps['level'].unique().tolist()
    selected_level = st.selectbox(
        'Show level', ['all'] + level_options,
        help="Choose to view all, part, or section metrics."
    )
    if selected_level != 'all':
        df_ps = df_ps[df_ps['level'] == selected_level]
    part_options = df_ps['part_heading'].unique().tolist()
    selected_part = st.selectbox(
        'Filter by part', ['all'] + part_options,
        help="Filter by part heading."
    )
    if selected_part != 'all':
        df_ps = df_ps[df_ps['part_heading'] == selected_part]
    # Custom readability filter
    min_read = st.number_input(
        'Minimum readability',
        value=float(df_ps['readability'].min()),
        step=0.1,
        help="Show only parts/sections above this readability."
    )
    max_read = st.number_input(
        'Maximum readability',
        value=float(df_ps['readability'].max()),
        step=0.1,
        help="Show only parts/sections below this readability."
    )
    df_ps = df_ps[(df_ps['readability'] >= min_read) & (df_ps['readability'] <= max_read)]
    # Sorting
    sort_col = st.selectbox(
        'Sort by', ['word_count', 'readability'],
        help="Sort by word count or readability."
    )
    sort_asc = st.checkbox('Sort ascending', value=False)
    df_ps = df_ps.sort_values(sort_col, ascending=sort_asc)
    # Show only key columns
    display_cols = [
        'level', 'part_heading', 'section_heading', 'word_count', 'readability'
    ]
    page_size_ps = st.number_input(
        'Rows per page (part/section)',
        min_value=5, max_value=100, value=20, step=5, key='ps_page_size'
    )
    total_rows_ps = len(df_ps)
    total_pages_ps = (total_rows_ps - 1) // page_size_ps + 1
    page_ps = st.number_input(
        'Page (part/section)', min_value=1, max_value=total_pages_ps, value=1, step=1, key='ps_page'
    )
    start_ps = (page_ps - 1) * page_size_ps
    end_ps = start_ps + page_size_ps
    st.dataframe(
        df_ps[display_cols].iloc[start_ps:end_ps],
        hide_index=True,
        use_container_width=True
    )
    st.subheader('Compare Parts/Sections')
    compare_rows = st.multiselect(
        'Select parts/sections to compare',
        df_ps.index,
        format_func=lambda i: (
            f"{df_ps.loc[i, 'part_heading']} | "
            f"{df_ps.loc[i, 'section_heading']}"
        ),
        help="Select multiple rows to compare side by side."
    )
    if compare_rows:
        st.dataframe(
            df_ps.loc[compare_rows][display_cols]
            .set_index(['part_heading', 'section_heading'])
        )
else:
    st.warning('part_section_metrics.json not found.')


# Citation Counts Table (show Title 1 data only)
st.header('Citation Counts')
st.markdown('Shows how often each section or part is cited. Download the table or sort to find the most/least cited.')
citation_data = None
import_path = os.path.join(PROCESSED_DIR, 'citation_counts.json')
if os.path.exists(import_path):
    with open(import_path, 'r', encoding='utf-8') as f:
        citation_data = json.load(f)
if citation_data:
    counts = citation_data.get('citation_counts', {})
    df_citations = pd.DataFrame(list(counts.items()), columns=['Section/Part', 'Citations'])
    def extract_title(fname):
        if fname.startswith('title') and '_parsed' in fname:
            num = fname.split('title')[1].split('_')[0]
            return f'Title {num}'
        return fname
    df_citations['Title'] = df_citations['Section/Part'].apply(lambda x: extract_title('title1_parsed.json'))
    df_citations = df_citations[['Title', 'Section/Part', 'Citations']]
    st.dataframe(df_citations.sort_values('Citations', ascending=False), hide_index=True)
    csv_cit = df_citations.to_csv(index=False).encode('utf-8')
    st.download_button('Download Citation Counts (CSV)', csv_cit, 'citation_counts.csv', 'text/csv')
else:
    st.warning('citation_counts.json not found.')


# Cross-Reference Network Graph (show Title 1 data only)
st.header('Cross-Reference Network')
st.markdown('Visualizes how sections and parts reference each other. Nodes with many connections may be central to the regulation.')
graph_data = None
import requests

# Load available parts and sections for selection
all_parts = []
all_sections = []
if part_section_metrics:
    df_ps = pd.DataFrame(part_section_metrics)
    all_parts = df_ps['part_heading'].dropna().unique().tolist()
    all_sections = df_ps['section_heading'].dropna().unique().tolist()

selected_parts = st.multiselect('Select Parts for Network Graph', all_parts)
selected_sections = st.multiselect('Select Sections for Network Graph', all_sections)

params = []
for part in selected_parts:
    params.append(f"part={part}")
for section in selected_sections:
    params.append(f"section={section}")
query_string = "&".join(params)
api_url = f"http://localhost:5000/api/cross_reference_graph"
if query_string:
    api_url += f"?{query_string}"

response = requests.get(api_url)
if response.ok:
    graph_data = response.json()
else:
    graph_data = None
if graph_data:
    G = nx.DiGraph()
    for node in graph_data['nodes']:
        G.add_node(node['id'], type=node.get('type', ''))
    for edge in graph_data['edges']:
        # Add edge with label as an attribute
        G.add_edge(edge['source'], edge['target'], label=edge.get('label', ''))
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    nx.draw(G, pos, with_labels=True, node_size=500, font_size=8, arrows=True)
    # Draw edge labels
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
    st.pyplot(plt)
    import io
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    st.download_button('Download Network Graph (PNG)', buf.getvalue(), 'cross_reference_network.png', 'image/png')
else:
    st.warning('cross_reference_graph.json not found.')

# Historical Trends (show Title 1 data only)
st.header('Historical Trends')
st.markdown('Track changes in word count and readability over time for each file.')
metrics_history = None
import_path = os.path.join(PROCESSED_DIR, 'metrics_history.json')
if os.path.exists(import_path):
    with open(import_path, 'r', encoding='utf-8') as f:
        metrics_history = json.load(f)
if metrics_history:
    records = []
    for entry in metrics_history:
        ts = entry['timestamp']
        for fname, metrics in entry['metrics'].items():
            records.append({
                'timestamp': ts,
                'file': fname,
                'word_count': metrics.get('word_count', 0),
                'readability': metrics.get('readability', 0)
            })
    df_hist = pd.DataFrame(records)
    files = df_hist['file'].unique()
    selected_file = st.selectbox('Select file for trend analysis', files)
    df_file = df_hist[df_hist['file'] == selected_file].sort_values('timestamp')
    st.line_chart(df_file.set_index('timestamp')[['word_count', 'readability']])
    csv_hist = df_file.to_csv(index=False).encode('utf-8')
    st.download_button('Download Historical Trends (CSV)', csv_hist, 'metrics_history.csv', 'text/csv')
else:
    st.warning('metrics_history.json not found.')

st.markdown('---')
st.caption('eCFR Regulatory Analysis Website | Streamlit Prototype')
