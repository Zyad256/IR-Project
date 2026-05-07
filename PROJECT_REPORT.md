# Mini Search Engine — Project Report

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [System Architecture](#3-system-architecture)
4. [Project Structure](#4-project-structure)
5. [File Format Handling](#5-file-format-handling)
6. [Indexing Pipeline](#6-indexing-pipeline)
7. [Search Features](#7-search-features)
8. [API Endpoints](#8-api-endpoints)
9. [Frontend GUI](#9-frontend-gui)
10. [Setup & Installation](#10-setup--installation)
11. [Usage Guide](#11-usage-guide)
12. [Screenshots](#12-screenshots)
13. [Code Walkthrough](#13-code-walkthrough)
14. [Design Decisions](#14-design-decisions)

---

## 1. Project Overview

This project is a **Mini Search Engine** that indexes a folder of files in multiple formats and allows users to search through them using advanced query types. The system is built as a full-stack web application with three layers:

- **Elasticsearch 9.4.0** — The core search and storage engine
- **FastAPI (Python)** — REST API backend that bridges the frontend and Elasticsearch
- **HTML/CSS/JavaScript** — A premium web-based graphical user interface

The search engine supports **5 file formats** (TXT, PDF, JSON, CSV, Excel), provides **4 query types** (boolean, phrase, fuzzy, wildcard), and includes features like date/type filtering, highlighted snippets, spell suggestions, pagination, and index statistics.

---

## 2. Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Search Engine | Elasticsearch | 9.4.0 | Document storage, indexing, and full-text search |
| Backend API | FastAPI | 0.115.0 | REST API server connecting frontend to Elasticsearch |
| Web Server | Uvicorn | 0.30.6 | ASGI server to run FastAPI |
| PDF Parsing | PyPDF2 | 3.0.1 | Extract text from PDF files |
| Excel Parsing | openpyxl | 3.1.5 | Read .xlsx spreadsheet files |
| ES Client | elasticsearch-py | 8.15+ | Python client for Elasticsearch |
| Frontend | HTML5 / CSS3 / JavaScript | — | User interface |

### Why Elasticsearch?
Elasticsearch is an industry-standard distributed search engine built on Apache Lucene. It provides:
- **Inverted index** for fast full-text search
- Built-in support for **boolean, phrase, fuzzy, and wildcard** queries via `query_string`
- **Highlighting** of matched terms in results
- **Spell suggestions** via the Term Suggester API
- **Aggregations** for computing statistics (term frequencies, document counts)
- Scales from small datasets to petabytes of data

### Why FastAPI?
FastAPI was chosen because:
- Native **async** support for high performance
- Automatic **API documentation** (Swagger UI at `/docs`)
- Built-in **request validation** with Pydantic models
- Easy **CORS** configuration for frontend communication
- Serves both the API and the static frontend files

---

## 3. System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    USER'S BROWSER                        │
│  ┌────────────────────────────────────────────────────┐  │
│  │           Frontend (HTML / CSS / JS)               │  │
│  │  • Index Tab — select formats, build index         │  │
│  │  • Search Tab — query, filters, results            │  │
│  │  • Stats Tab — document & term statistics          │  │
│  └──────────────────┬─────────────────────────────────┘  │
│                     │  HTTP Requests (JSON)               │
└─────────────────────┼────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│               FastAPI Backend (Python)                   │
│                  http://localhost:8000                    │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │
│  │ /api/    │  │ /api/    │  │ /api/    │  │ /api/   │  │
│  │ index    │  │ search   │  │ stats    │  │ health  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘  │
│       │              │             │              │       │
│  ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐       │       │
│  │ indexer  │  │ searcher │  │ searcher │       │       │
│  │   .py    │  │   .py    │  │   .py    │       │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘       │       │
│       │              │             │              │       │
└───────┼──────────────┼─────────────┼──────────────┼──────┘
        │              │             │              │
        ▼              ▼             ▼              ▼
┌──────────────────────────────────────────────────────────┐
│              Elasticsearch 9.4.0                         │
│              http://localhost:9200                        │
│                                                          │
│  Index: "search_engine_docs"                             │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Fields:                                           │  │
│  │  • content (text, analyzed, fielddata enabled)     │  │
│  │  • filename (keyword)                              │  │
│  │  • filepath (keyword)                              │  │
│  │  • file_type (keyword)                             │  │
│  │  • modification_date (date)                        │  │
│  │  • file_size (long)                                │  │
│  │  • sub_doc_id (keyword)                            │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Indexing**: User selects a folder and file formats → FastAPI reads and parses each file → parsed text is sent as documents to Elasticsearch via bulk API → Elasticsearch builds an inverted index
2. **Searching**: User types a query → FastAPI sends it to Elasticsearch using `query_string` → Elasticsearch returns ranked, highlighted results → FastAPI formats and returns them to the frontend
3. **Stats**: FastAPI queries Elasticsearch aggregations → returns document counts, type breakdown, and top terms

---

## 4. Project Structure

```
IR-Project/
│
├── backend/                    # Python FastAPI backend
│   ├── main.py                 # FastAPI app, routes, and server startup
│   ├── indexer.py              # File parsing + Elasticsearch indexing logic
│   ├── searcher.py             # Search queries + stats + spell suggestions
│   └── requirements.txt        # Python package dependencies
│
├── frontend/                   # Web-based GUI
│   ├── index.html              # Main HTML page (3 tabs: Index, Search, Stats)
│   ├── style.css               # Premium dark-mode CSS styling
│   └── app.js                  # JavaScript application logic
│
├── sample_data/                # Sample test files (all 5 formats)
│   ├── information_retrieval.txt
│   ├── elasticsearch_guide.txt
│   ├── python_data_science.txt
│   ├── ccna topologies.pdf
│   ├── courses.json
│   ├── products.csv
│   └── employees.xlsx
│
├── elasticsearch-9.4.0/        # Elasticsearch installation (not in Git)
├── create_sample_excel.py      # Helper script to generate Excel test data
├── .gitignore                  # Excludes ES binary and cache files
├── README.md                   # Quick-start guide
└── PROJECT_REPORT.md           # This report
```

---

## 5. File Format Handling

The engine supports extracting searchable text from **5 file formats**. The user selects which formats to include before building the index (via checkboxes in the UI).

| Format | Parser | Strategy | Example |
|--------|--------|----------|---------|
| **TXT** | Built-in Python `open()` | Entire file content = **1 document** | A .txt file becomes a single searchable document |
| **PDF** | PyPDF2 `PdfReader` | All pages concatenated = **1 document** | A 10-page PDF becomes one document with all text |
| **JSON** | Built-in `json.load()` | List of objects → **each object = 1 document**; Single object → **1 document**. All string values are recursively extracted and concatenated | A JSON array of 6 course objects → 6 documents |
| **CSV** | Built-in `csv.DictReader` | **Each row = 1 document**. All column values concatenated with headers as prefixes | A CSV with 10 rows → 10 documents, e.g. `"name: Laptop | price: 1299"` |
| **Excel** | openpyxl `load_workbook` | **Each row = 1 document** (skipping header row). All cell values concatenated with header names | An xlsx with 8 data rows → 8 documents |

### JSON Parsing Detail (Design Decision)
For JSON files, all string (and numeric) values are recursively extracted:
```python
# Input JSON object:
{"id": 1, "title": "Machine Learning", "price": 29.99}

# Extracted text (one document):
"id: 1 | title: Machine Learning | price: 29.99"
```
This ensures every piece of data is searchable regardless of JSON structure depth.

### CSV/Excel Parsing Detail
Each row is treated as a separate document with column headers as prefixes:
```
# CSV row:
name,category,price,description
Laptop Pro,Electronics,1299.99,High-performance laptop

# Indexed as:
"name: Laptop Pro | category: Electronics | price: 1299.99 | description: High-performance laptop"
```

---

## 6. Indexing Pipeline

### Elasticsearch Index Configuration
The index `search_engine_docs` uses the following mapping:

```json
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
      "analyzer": {
        "custom_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "stop"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "filename":          { "type": "keyword" },
      "filepath":          { "type": "keyword" },
      "file_type":         { "type": "keyword" },
      "content":           { "type": "text", "analyzer": "custom_analyzer",
                             "term_vector": "with_positions_offsets",
                             "fielddata": true },
      "modification_date": { "type": "date" },
      "file_size":         { "type": "long" },
      "sub_doc_id":        { "type": "keyword" }
    }
  }
}
```

**Key design choices:**
- **Custom analyzer** with `lowercase` + `stop` filters: normalizes text and removes English stop words (the, a, is, etc.) to improve search relevance
- **term_vector: with_positions_offsets**: enables fast highlighting of matched terms in search results
- **fielddata: true** on `content`: allows terms aggregation for the top-10 frequent terms statistics
- **keyword fields** for filename, file_type, etc.: enables exact-match filtering and aggregation

### Indexing Process
1. User provides a folder path and selects formats
2. `scan_folder()` recursively walks the folder, collecting files with matching extensions
3. For each file, the appropriate parser extracts documents
4. Each document gets metadata: `filename`, `filepath`, `file_type`, `modification_date` (from `os.path.getmtime`), `file_size`
5. A unique `_id` is generated via MD5 hash of `filepath + sub_doc_id`
6. All documents are sent to Elasticsearch via the **Bulk API** for efficient indexing
7. Index is refreshed to make documents immediately searchable

---

## 7. Search Features

### 7.1 Query Types
All query types are handled by Elasticsearch's `query_string` query parser. The user types everything in a **single search box** — no separate buttons needed.

#### Boolean Operators: `AND`, `OR`, `NOT`, `()`
```
python AND machine           → documents containing BOTH words
python OR java               → documents containing EITHER word
python NOT java              → documents with python but NOT java
(python OR java) AND search  → grouping with parentheses
```

#### Phrase Queries: `"exact phrase"`
```
"information retrieval"      → exact phrase match in order
"machine learning"           → both words must appear adjacent
```

#### Fuzzy Queries: `word~`, `word~N`
```
retrival~                    → finds "retrieval" (1 edit distance, auto)
retrival~2                   → allows up to 2 character edits
machin~                      → finds "machine"
```
Fuzzy search tolerates typos by matching terms within an edit distance (insertions, deletions, substitutions).

#### Wildcard Queries: `*` and `?`
```
inform*                      → matches "information", "informatics", etc.
?earch                       → matches "search" (? = single character)
data*                        → matches "data", "database", "dataframe"
```

### 7.2 Date Range Filter
Users can filter results by the file's **modification date** (`os.path.getmtime`). The filter uses Elasticsearch's `range` query:
```json
{ "range": { "modification_date": { "gte": "2026-01-01", "lte": "2026-12-31" } } }
```

### 7.3 File Type Filter
Users can restrict results to a specific file type (txt, pdf, json, csv, xlsx) using a dropdown. This uses a `terms` filter on the `file_type` keyword field:
```json
{ "terms": { "file_type": ["csv"] } }
```

### 7.4 Highlighted Snippets
Search results include highlighted text fragments where matched terms are wrapped in `<mark>` tags:
```json
{
  "highlight": {
    "fields": {
      "content": {
        "fragment_size": 200,
        "number_of_fragments": 3,
        "pre_tags": ["<mark>"],
        "post_tags": ["</mark>"]
      }
    }
  }
}
```
This produces snippets like:
> "Academic textbook on **information** **retrieval** systems and search engine design"

### 7.5 "Did You Mean?" Suggestions
When a search returns **zero results**, the system uses Elasticsearch's **Term Suggester** to propose corrections:

```json
{
  "suggest": {
    "text": "machin lerning",
    "spell_suggest": {
      "term": {
        "field": "content",
        "suggest_mode": "popular",
        "sort": "frequency",
        "max_edits": 2
      }
    }
  }
}
```

The system reconstructs the corrected query by replacing each misspelled word with the best suggestion:
- Input: `"machin lerning"` → Suggestion: `"machine learning"`

### 7.6 Pagination
Results are paginated at **5 per page** with Previous/Next navigation:
```json
{ "from": 0, "size": 5 }   // Page 1
{ "from": 5, "size": 5 }   // Page 2
{ "from": 10, "size": 5 }  // Page 3
```

---

## 8. API Endpoints

The FastAPI backend exposes the following REST API:

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|-------------|
| `GET` | `/` | Serves the frontend HTML page | — |
| `GET` | `/api/health` | Checks Elasticsearch connectivity | — |
| `GET` | `/api/formats` | Returns supported file formats | — |
| `POST` | `/api/index` | Builds/rebuilds the search index | `{ folder_path, formats[] }` |
| `POST` | `/api/search` | Searches the index | `{ query, page, page_size, date_from, date_to, file_types[] }` |
| `GET` | `/api/stats` | Returns index statistics | — |

### Example API Calls

**Build Index:**
```bash
curl -X POST http://localhost:8000/api/index \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "C:\\sample_data", "formats": ["txt", "pdf", "csv"]}'
```

**Search:**
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "page": 1, "file_types": ["txt"]}'
```

**Response format:**
```json
{
  "total": 6,
  "page": 1,
  "page_size": 5,
  "total_pages": 2,
  "documents": [
    {
      "filename": "python_data_science.txt",
      "file_type": "txt",
      "score": 2.149,
      "modification_date": "2026-05-07T01:15:46",
      "snippet": "<mark>Python</mark> has become the most popular programming language for data science and <mark>machine</mark> <mark>learning</mark>...",
      "sub_doc_id": "main"
    }
  ],
  "did_you_mean": null
}
```

---

## 9. Frontend GUI

The frontend is a single-page application with **three tabs**:

### Tab 1: Index
- **Folder Path Input**: Enter the path to the folder containing files to index
- **Format Checkboxes**: Select which file formats to include (TXT, PDF, JSON, CSV, XLSX)
- **Build Index Button**: Triggers indexing with a loading spinner
- **Result Display**: Shows success message with document counts by type

### Tab 2: Search
- **Search Box**: Single input for all query types (boolean, phrase, fuzzy, wildcard)
- **Syntax Help**: Visual guide showing supported query syntax
- **Filters Row**:
  - Date From / Date To (date pickers for modification date range)
  - File Type dropdown (All Types / TXT / PDF / JSON / CSV / Excel)
- **Results Display**: Each result shows:
  - 📄 Filename
  - File type badge (colored)
  - Relevance score
  - Modification date
  - Sub-document ID (for CSV/JSON rows)
  - Highlighted snippet with matched terms
- **Did You Mean**: Yellow suggestion bar when zero results found
- **Pagination**: Previous / Page X of Y / Next buttons

### Tab 3: Stats
- **Total Indexed Documents**: Large number display
- **File Types Count**: Number of distinct file types
- **Breakdown by File Type**: Chip badges showing each type and its count
- **Top 10 Most Frequent Terms**: Tag cloud showing the most common terms and their document frequency

### UI Design
- **Dark mode** with glassmorphism effects
- **Gradient accents** (indigo → cyan)
- **Smooth animations** and hover effects
- **Responsive** layout for all screen sizes
- **Google Fonts** (Inter) for professional typography

---

## 10. Setup & Installation

### Prerequisites
- **Python 3.9+** installed
- **Elasticsearch 9.4.0** (included in the project folder)
- **Java 17+** (required by Elasticsearch — bundled JDK is included)

### Step 1: Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure Elasticsearch
The `elasticsearch-9.4.0/config/elasticsearch.yml` is pre-configured with:
```yaml
# Security disabled for local development
xpack.security.enabled: false
xpack.security.enrollment.enabled: false
xpack.security.http.ssl.enabled: false
xpack.security.transport.ssl.enabled: false

# Disk watermark relaxed for nearly-full disks
cluster.routing.allocation.disk.watermark.low: 95%
cluster.routing.allocation.disk.watermark.high: 98%
cluster.routing.allocation.disk.watermark.flood_stage: 99%
```

### Step 3: Start Elasticsearch
```bash
elasticsearch-9.4.0\bin\elasticsearch.bat
```
Wait ~30 seconds until you see `"status":"green"` in the logs.

Verify it's running:
```bash
curl http://localhost:9200
```

### Step 4: Start the FastAPI Server
```bash
cd backend
python main.py
```
Server starts at **http://localhost:8000**

### Step 5: Open the Web GUI
Open your browser and navigate to:
```
http://localhost:8000
```

---

## 11. Usage Guide

### Building the Index
1. Go to the **Index** tab
2. Enter the folder path (e.g., `C:\Users\DELL\Desktop\IR\sample_data`)
3. Check the file formats you want to index
4. Click **⚡ Build Index**
5. See the summary: "Indexed 28 documents from 7 files"

### Searching
1. Go to the **Search** tab
2. Type your query using any supported syntax:
   - `machine learning` — basic search
   - `"information retrieval"` — exact phrase
   - `retrival~` — fuzzy (finds "retrieval")
   - `inform*` — wildcard
   - `python AND learning` — boolean AND
   - `python OR java` — boolean OR
   - `python NOT java` — boolean NOT
3. Optionally set date range and/or file type filter
4. Click **🔎 Search**
5. Browse results with pagination (5 per page)

### Viewing Stats
1. Go to the **Stats** tab
2. Click **📊 Load Stats**
3. View: total documents, type breakdown, top 10 terms

---

## 12. Screenshots

### Index Tab
The Index tab allows users to select a folder path and choose which file formats to include before building the index.

### Search Results
Search results display the filename, file type badge, relevance score, modification date, and a highlighted snippet where matched terms are wrapped in colored markers.

### Fuzzy Search
Typing `retrival~` (with a typo) successfully finds documents containing "retrieval", demonstrating the fuzzy search capability with edit distance tolerance.

### "Did You Mean?" Suggestion
When searching `machin lerning` (typos), the system returns zero results but suggests "Did you mean: machine learning?" — clicking the suggestion reruns the corrected query.

### Stats Dashboard
The Stats tab displays the total number of indexed documents (28), breakdown by file type (CSV: 10, XLSX: 8, JSON: 6, TXT: 3, PDF: 1), and the top 10 most frequent terms in the corpus.

---

## 13. Code Walkthrough

### `backend/indexer.py` — File Parsing & Indexing

**Key functions:**
- `get_es_client()` — Creates an Elasticsearch connection to `localhost:9200`
- `create_index()` — Creates the ES index with custom analyzer and mappings
- `parse_txt()` / `parse_pdf()` / `parse_json()` / `parse_csv()` / `parse_excel()` — Format-specific parsers
- `scan_folder()` — Recursively finds files with allowed extensions
- `index_files()` — Orchestrates the full pipeline: scan → parse → bulk index

**Flow:**
```python
def index_files(es, folder_path, allowed_formats, force_rebuild=True):
    create_index(es, force_rebuild)          # 1. Create/recreate ES index
    files = scan_folder(folder, extensions)   # 2. Find matching files
    for filepath in files:
        documents = parser(filepath)          # 3. Parse each file
        for doc in documents:
            actions.append(bulk_action)       # 4. Prepare bulk actions
    helpers.bulk(es, actions)                 # 5. Bulk index to ES
    es.indices.refresh(index=INDEX_NAME)      # 6. Make searchable
```

### `backend/searcher.py` — Search & Statistics

**Key functions:**
- `search_documents()` — Full search with query_string, filters, highlighting, suggestions, and pagination
- `get_index_stats()` — Returns document count, type breakdown, and top 10 terms

**Search query construction:**
```python
search_body = {
    "query": {
        "bool": {
            "must": [{
                "query_string": {           # Handles AND/OR/NOT/phrase/fuzzy/wildcard
                    "query": user_query,
                    "default_field": "content"
                }
            }],
            "filter": [                     # Date range + file type filters
                {"range": {"modification_date": {"gte": date_from, "lte": date_to}}},
                {"terms": {"file_type": ["csv"]}}
            ]
        }
    },
    "highlight": { ... },                   # Highlighted snippets
    "suggest": { ... },                     # Spell suggestions
    "from": offset, "size": 5              # Pagination
}
```

### `backend/main.py` — FastAPI Application

**Responsibilities:**
- Defines REST API routes (`/api/index`, `/api/search`, `/api/stats`, `/api/health`, `/api/formats`)
- Validates request data with Pydantic models
- Serves the frontend static files
- Handles CORS for cross-origin requests
- Error handling with appropriate HTTP status codes

### `frontend/app.js` — Frontend Logic

**Key functions:**
- `buildIndex()` — Sends indexing request, displays results
- `doSearch(page)` — Sends search request with query + filters + pagination
- `renderResults(data)` — Renders result cards with highlighting
- `searchSuggestion(text)` — Handles "did you mean" click
- `loadStats()` — Fetches and renders statistics

---

## 14. Design Decisions

### Why `query_string` instead of separate query types?
Elasticsearch's `query_string` parser natively understands all required syntax (AND, OR, NOT, "phrase", word~, wild*) in a single query string. This means the user can type any combination in one search box without needing separate buttons or modes.

### Why each CSV/Excel row is a separate document?
Treating each row as a separate document allows:
- Individual rows to appear in search results with their own score
- More granular search — finding specific products/employees
- Better highlighting — the snippet shows the relevant row, not the entire file

### Why `fielddata: true` on the content field?
By default, Elasticsearch doesn't allow terms aggregation on `text` fields (it's memory-intensive). We enable `fielddata` to compute the top-10 most frequent terms. This is acceptable for small-to-medium datasets.

### Why the custom analyzer with stop words?
The `stop` filter removes common English words (the, a, is, are...) from the index. This:
- Reduces index size
- Improves search relevance (stop words don't inflate scores)
- Makes the top-10 terms more meaningful (no stop words in the list)

### Why MD5 for document IDs?
Each document gets a unique ID via `MD5(filepath + sub_doc_id)`. This ensures:
- Rebuilding the index doesn't create duplicate documents
- Each CSV row / JSON object has a deterministic, unique ID
- The same file re-indexed produces the same document IDs

---

## Summary

This Mini Search Engine demonstrates a complete information retrieval pipeline:

1. **Data Ingestion** — Multi-format file parsing (TXT, PDF, JSON, CSV, XLSX)
2. **Indexing** — Elasticsearch inverted index with custom analysis
3. **Querying** — Full query syntax (boolean, phrase, fuzzy, wildcard)
4. **Filtering** — Date range and file type filters
5. **Ranking** — BM25 relevance scoring
6. **Presentation** — Highlighted snippets, pagination, spell suggestions
7. **Analytics** — Document statistics and term frequency analysis

The system is accessible through a modern, responsive web GUI and exposes a clean REST API that could be consumed by any client application.
