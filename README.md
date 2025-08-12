# eCFR Regulatory Analysis Website

## Project Overview
This project provides a Python-based pipeline and web application to download, parse, analyze, and visualize regulatory data from the Electronic Code of Federal Regulations (eCFR), starting with Title 1. It exposes REST API endpoints for all processed data and includes a Streamlit dashboard for interactive exploration.

## Setup Instructions
1. **Clone the repository and navigate to the project directory.**
2. **Create and activate a Python virtual environment:**
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
   Ensure you have `textstat`, `flask`, `streamlit`, `pandas`, `networkx`, and `matplotlib` installed.

## Data Pipeline Usage
1. **Fetch and parse the latest eCFR Title 1 data** (see `parse_title1_xml.py`).
2. **Run the analysis pipeline:**
   ```powershell
   python ecfr_analysis/backend/analysis.py
   ```
   This will generate processed data files in `ecfr_analysis/data/processed/`.

## Running the Web Applications
- **Flask REST API:**
  ```powershell
  python ecfr_analysis/backend/app.py
  ```
  The API will be available at `http://localhost:5000`.

- **Streamlit Dashboard:**
  ```powershell
  streamlit run ecfr_analysis/frontend/app.py
  ```
  The dashboard will open in your browser.

## API Endpoints
All endpoints return JSON data:
- `/api/metrics` — Overall metrics (word count, readability, checksum per file)
- `/api/part_section_metrics` — Metrics for each part and section
- `/api/citation_counts` — Citation counts and resolved references
- `/api/cross_references` — Extracted cross-references
- `/api/cross_reference_graph` — Network graph data (nodes and edges)
- `/api/metrics_history` — Historical metrics (timestamped)

Example usage:
```
GET http://localhost:5000/api/metrics
```

## Adding New Titles
- Place new parsed title JSON files in `ecfr_analysis/data/raw/`.
- Update and run the analysis pipeline to process new data.
- The API and dashboard will automatically reflect new processed files.

## Troubleshooting & Tips
- Ensure all dependencies are installed in your virtual environment.
- If you encounter errors, check file paths and data file existence.
- For large data or new titles, adjust scripts as needed for scalability.

---
For questions or contributions, please contact the project maintainer.
