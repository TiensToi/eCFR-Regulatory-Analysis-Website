from flask import Flask, jsonify, send_from_directory
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
    return send_from_directory(DATA_DIR, 'cross_reference_graph.json')

@app.route('/api/metrics_history')
def metrics_history():
    return send_from_directory(DATA_DIR, 'metrics_history.json')

if __name__ == '__main__':
    app.run(debug=True)
