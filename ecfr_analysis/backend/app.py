from flask import Flask, jsonify, send_from_directory, request
import json
import os

app = Flask(__name__)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed'))

@app.route('/')
def index():
    return jsonify({
        'endpoints': [
            '/api/metrics',
            '/api/part_section_metrics',
            '/api/citation_counts',
            '/api/cross_references',
            '/api/cross_reference_graph',
            '/api/metrics_history'
        ]
    })

@app.route('/api/metrics')
def all_metrics():
    return send_from_directory(DATA_DIR, 'metrics.json')

@app.route('/api/part_section_metrics')
def part_section_metrics():
    return send_from_directory(DATA_DIR, 'part_section_metrics.json')

@app.route('/api/citation_counts')
def citation_counts():
    return send_from_directory(DATA_DIR, 'citation_counts.json')

@app.route('/api/cross_references')
def cross_references():
    return send_from_directory(DATA_DIR, 'cross_references.json')

@app.route('/api/cross_reference_graph')
def cross_reference_graph():
    graph_path = os.path.join(DATA_DIR, 'cross_reference_graph.json')
    selected_parts = request.args.getlist('part')
    selected_sections = request.args.getlist('section')
    with open(graph_path, 'r', encoding='utf-8') as f:
        graph = json.load(f)
    if selected_parts or selected_sections:
        filtered_nodes = [
            node for node in graph['nodes']
            if (not selected_parts or node.get('part') in selected_parts or (node.get('type') == 'part' and node.get('id') in selected_parts))
            and (not selected_sections or node.get('section') in selected_sections or (node.get('type') == 'section' and node.get('id') in selected_sections))
        ]
        filtered_node_ids = {node['id'] for node in filtered_nodes}
        filtered_edges = [
            edge for edge in graph['edges']
            if edge['source'] in filtered_node_ids and edge['target'] in filtered_node_ids
        ]
        filtered_graph = {
            'nodes': filtered_nodes,
            'edges': filtered_edges
        }
        return jsonify(filtered_graph)
    else:
        return jsonify(graph)

@app.route('/api/metrics_history')
def metrics_history():
    return send_from_directory(DATA_DIR, 'metrics_history.json')

if __name__ == '__main__':
    app.run(debug=True)
    