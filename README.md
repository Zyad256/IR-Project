# Mini Search Engine

A full-featured search engine built with **Elasticsearch**, **FastAPI**, and **HTML/JS** frontend.

## Features
- **Multi-format indexing**: TXT, PDF, JSON, CSV, Excel (.xlsx)
- **Full query syntax**: Boolean (AND/OR/NOT), phrase, fuzzy, wildcard
- **Filters**: Date range (modification date) and file type
- **Highlighted snippets** in results
- **"Did you mean?"** spell suggestions on zero results
- **Pagination**: 5 results per page
- **Stats dashboard**: Total docs, type breakdown, top 10 terms

## Setup

### Prerequisites
- Python 3.9+
- Elasticsearch 9.4.0 running on `localhost:9200`

### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Run
```bash
cd backend
python main.py
```
Then open **http://localhost:8000** in your browser.

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
Frontend (HTML/JS) → FastAPI (REST API) → Elasticsearch (Storage & Search)
```
