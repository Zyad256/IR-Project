# Mini Search Engine

A full-featured search engine built with **Elasticsearch 8.15.1**, **FastAPI**, and a **HTML/CSS/JS** frontend.

## Features
- **Multi-format indexing**: TXT, PDF, JSON, CSV, Excel (.xlsx)
- **Full query syntax**: Boolean (AND/OR/NOT), phrase, fuzzy, wildcard
- **Filters**: Date range (modification date) and file type
- **Highlighted snippets** in results
- **"Did you mean?"** spell suggestions on zero results
- **Pagination**: 5 results per page
- **Stats dashboard**: Total docs, type breakdown, top 10 terms
- **Kibana integration**: Browse and visualize indexed data via Kibana 8.15.1

## Setup

### Prerequisites
- Python 3.9+
- [Elasticsearch 8.15.1](https://www.elastic.co/downloads/past-releases/elasticsearch-8-15-1) — extract to `elasticsearch-8.15.1/` in the project root
- *(Optional)* [Kibana 8.15.1](https://www.elastic.co/downloads/past-releases/kibana-8-15-1) — extract to `kibana-8.15.1/` for data visualization

### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Configure Elasticsearch
Edit `elasticsearch-8.15.1/config/elasticsearch.yml` and add:
```yaml
xpack.security.enabled: false
xpack.security.enrollment.enabled: false
xpack.security.http.ssl.enabled: false
xpack.security.transport.ssl.enabled: false
```

### Start Elasticsearch
```bash
elasticsearch-8.15.1\bin\elasticsearch.bat
```
Wait ~30 seconds until `localhost:9200` responds.

### Start the App
```bash
cd backend
python main.py
```
Open **http://localhost:8000** in your browser.

### *(Optional)* Start Kibana
```bash
kibana-8.15.1\bin\kibana.bat
```
Open **http://localhost:5601** → Discover → Create a Data View for `search_engine_docs` to browse indexed data.

## File Format Handling
| Format | Strategy |
|--------|----------|
| TXT | Entire file content = 1 document |
| PDF | All pages concatenated = 1 document |
| JSON | List → each object = 1 doc; Single object = 1 doc |
| CSV | Each row = 1 document |
| Excel | Each row = 1 document |

## Architecture
```
Frontend (HTML/JS) → FastAPI (REST API) → Elasticsearch 8.15.1 (Storage & Search)
                                        ↕
                                   Kibana 8.15.1 (Data Visualization)
```

## Project Structure
```
IR-Project/
├── backend/
│   ├── main.py              # FastAPI app & routes
│   ├── indexer.py            # File parsing + ES indexing
│   ├── searcher.py           # Search queries + stats
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── index.html            # Main HTML page (3 tabs)
│   ├── style.css             # Dark-mode CSS
│   └── app.js                # Frontend logic
├── sample_data/              # Sample test files (all 5 formats)
├── .gitignore
├── README.md
└── PROJECT_REPORT.md         # Detailed technical report
```
