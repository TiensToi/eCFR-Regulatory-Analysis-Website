# eCFR Regulatory Analysis Website

## Overview
This project provides a Python-based web app to download, store, analyze, and visualize data from the Electronic Code of Federal Regulations (eCFR). It fetches all agency titles via the public eCFR API, saves the raw data locally, computes metrics (word counts, historical trends, checksums, readability), and exposes REST endpoints for a frontend UI. Users can review metric tables and charts in their browser to support deregulation insights.

## Repository Structure
```
ecfr_analysis/
│
├── backend/
│   ├── fetch_data.py
│   ├── analysis.py
│   ├── app.py
│   └── requirements.txt
│
├── data/
│   ├── raw/
│   │   └── {agency_id}.json
│   └── processed/
│       └── metrics.json
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── scripts.js
│
├── screenshots/
│   ├── word_count.png
│   ├── history_chart.png
│   └── readability_table.png
│
└── README.md
```

## Backend Implementation
- **fetch_data.py**: Downloads eCFR data for all agencies.
- **analysis.py**: Processes raw data, computes metrics (word count, checksum, readability).
- **app.py**: Flask REST API serving metrics.

## Frontend UI
- **index.html**: Table of agencies, word count, checksum, readability, and a chart (Chart.js).
- **styles.css**: Basic styling.
- **scripts.js**: Fetches API data, renders table and chart, supports search/filter.

## Setup & Usage
# 1. Clone repo.
# 2. `cd ecfr_analysis/backend && pip install -r requirements.txt`
# 3. Run `python fetch_data.py` then `python analysis.py`.
# 4. Start server: `python app.py`.
# 5. Open `frontend/index.html` in your browser (or serve via simple HTTP).

## API Endpoints
- `GET /api/metrics`: All agency metrics
- `GET /api/metrics/{id}`: Metrics for a specific agency

## Custom Metric: Readability Score
Uses Flesch–Kincaid Grade Level to gauge complexity. Lower = simpler language.

## Frontend Access
- Local URL (served): http://localhost:5000

## UI Screenshots
- Word Count Table: screenshots/word_count.png
- Readability Table: screenshots/readability_table.png
- Historical Trend Chart: screenshots/history_chart.png
