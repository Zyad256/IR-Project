"""
FastAPI Backend for Mini Search Engine.

Provides REST API endpoints connecting the web GUI to Elasticsearch.
"""

import os
from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from indexer import get_es_client, index_files, INDEX_NAME
from searcher import search_documents, get_index_stats

app = FastAPI(title="Mini Search Engine", version="1.0.0")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# ─── Request/Response Models ──────────────────────────────────────────

class IndexRequest(BaseModel):
    folder_path: str
    formats: List[str]  # e.g. ["txt", "pdf", "csv", "json", "xlsx"]


class SearchRequest(BaseModel):
    query: str
    page: int = 1
    page_size: int = 5
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    file_types: Optional[List[str]] = None


# ─── API Endpoints ────────────────────────────────────────────────────

@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML page."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Mini Search Engine API is running. Frontend not found."}


@app.get("/api/health")
async def health_check():
    """Check if Elasticsearch is reachable."""
    try:
        es = get_es_client()
        info = es.info()
        return {
            "status": "ok",
            "elasticsearch": {
                "version": info["version"]["number"],
                "cluster_name": info.get("cluster_name", "unknown")
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/index")
async def build_index(request: IndexRequest):
    """Build or rebuild the search index from a folder."""
    folder = request.folder_path.strip()

    if not os.path.isdir(folder):
        raise HTTPException(status_code=400, detail=f"Folder not found: {folder}")

    if not request.formats:
        raise HTTPException(status_code=400, detail="No file formats selected.")

    try:
        es = get_es_client()
        stats = index_files(es, folder, request.formats, force_rebuild=True)
        return {
            "status": "success",
            "message": f"Indexed {stats['total_documents']} documents from {stats['total_files']} files.",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing error: {str(e)}")


@app.post("/api/search")
async def search(request: SearchRequest):
    """Search the index with full query syntax support."""
    try:
        es = get_es_client()

        # Check if index exists
        if not es.indices.exists(index=INDEX_NAME):
            raise HTTPException(
                status_code=400,
                detail="No index found. Please build the index first."
            )

        results = search_documents(
            es,
            query=request.query,
            page=request.page,
            page_size=request.page_size,
            date_from=request.date_from,
            date_to=request.date_to,
            file_types=request.file_types,
        )
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.get("/api/stats")
async def stats():
    """Get index statistics."""
    try:
        es = get_es_client()
        return get_index_stats(es)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")


@app.get("/api/formats")
async def supported_formats():
    """Return the list of supported file formats."""
    return {
        "formats": [
            {"id": "txt", "label": "Text Files (.txt)", "extension": ".txt"},
            {"id": "pdf", "label": "PDF Files (.pdf)", "extension": ".pdf"},
            {"id": "json", "label": "JSON Files (.json)", "extension": ".json"},
            {"id": "csv", "label": "CSV Files (.csv)", "extension": ".csv"},
            {"id": "xlsx", "label": "Excel Files (.xlsx)", "extension": ".xlsx"},
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
