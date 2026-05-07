"""
Searcher Module - Handles all search operations against Elasticsearch.

Supports:
- Boolean queries (AND, OR, NOT, grouping)
- Phrase queries ("exact phrase")
- Fuzzy queries (word~, word~2)
- Wildcard queries (inform*, ?earch)
- Date range filtering
- File type filtering
- Highlighted snippets
- "Did you mean?" suggestions
- Pagination
"""

import re
from typing import Dict, List, Optional
from elasticsearch import Elasticsearch

INDEX_NAME = "search_engine_docs"


def search_documents(
    es: Elasticsearch,
    query: str,
    page: int = 1,
    page_size: int = 5,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    file_types: Optional[List[str]] = None,
) -> Dict:
    """
    Search documents with full query support.
    
    The query string supports Elasticsearch query_string syntax:
    - Boolean: term1 AND term2, term1 OR term2, NOT term1, (a OR b) AND c
    - Phrase: "information retrieval"
    - Fuzzy: retrival~, retrival~2
    - Wildcard: inform*, ?earch
    """
    from_offset = (page - 1) * page_size

    # Build the query
    must_clauses = []
    filter_clauses = []

    # Main search query using query_string for full syntax support
    if query and query.strip():
        must_clauses.append({
            "query_string": {
                "query": query,
                "default_field": "content",
                "default_operator": "OR",
                "allow_leading_wildcard": True,
                "analyze_wildcard": True,
                "fuzzy_prefix_length": 1,
                "fuzzy_max_expansions": 50,
                "phrase_slop": 0
            }
        })
    else:
        must_clauses.append({"match_all": {}})

    # Date range filter
    if date_from or date_to:
        date_range = {}
        if date_from:
            date_range["gte"] = date_from
        if date_to:
            date_range["lte"] = date_to
        filter_clauses.append({
            "range": {
                "modification_date": date_range
            }
        })

    # File type filter
    if file_types and len(file_types) > 0:
        filter_clauses.append({
            "terms": {
                "file_type": [ft.lower().strip('.') for ft in file_types]
            }
        })

    # Assemble the bool query
    bool_query = {"must": must_clauses}
    if filter_clauses:
        bool_query["filter"] = filter_clauses

    # Build the search body
    search_body = {
        "query": {
            "bool": bool_query
        },
        "highlight": {
            "fields": {
                "content": {
                    "fragment_size": 200,
                    "number_of_fragments": 3,
                    "pre_tags": ["<mark>"],
                    "post_tags": ["</mark>"]
                }
            }
        },
        "from": from_offset,
        "size": page_size,
        "sort": [
            {"_score": {"order": "desc"}},
            {"modification_date": {"order": "desc"}}
        ],
        # Suggest for "did you mean?"
        "suggest": {
            "text": query if query else "",
            "spell_suggest": {
                "term": {
                    "field": "content",
                    "suggest_mode": "popular",
                    "sort": "frequency",
                    "string_distance": "internal",
                    "max_edits": 2
                }
            }
        }
    }

    # Execute search
    result = es.search(index=INDEX_NAME, body=search_body)

    # Parse results
    hits = result.get("hits", {})
    total = hits.get("total", {}).get("value", 0)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    documents = []
    for hit in hits.get("hits", []):
        source = hit["_source"]
        highlight = hit.get("highlight", {}).get("content", [])
        documents.append({
            "id": hit["_id"],
            "filename": source.get("filename", ""),
            "filepath": source.get("filepath", ""),
            "file_type": source.get("file_type", ""),
            "score": round(hit["_score"], 4) if hit["_score"] else 0,
            "modification_date": source.get("modification_date", ""),
            "file_size": source.get("file_size", 0),
            "sub_doc_id": source.get("sub_doc_id", "main"),
            "snippet": " ... ".join(highlight) if highlight else source.get("content", "")[:300],
        })

    # Parse suggestions
    suggestions = []
    suggest_data = result.get("suggest", {}).get("spell_suggest", [])
    for entry in suggest_data:
        for option in entry.get("options", []):
            suggestions.append(option.get("text", ""))

    # Build "did you mean" string
    did_you_mean = None
    if total == 0 and suggestions:
        # Rebuild the query with suggestions
        corrected_query = query
        for entry in suggest_data:
            original = entry.get("text", "")
            if entry.get("options"):
                best = entry["options"][0]["text"]
                corrected_query = corrected_query.replace(original, best)
        if corrected_query != query:
            did_you_mean = corrected_query

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "documents": documents,
        "did_you_mean": did_you_mean,
        "query": query
    }


def get_index_stats(es: Elasticsearch) -> Dict:
    """Get statistics about the indexed documents."""
    if not es.indices.exists(index=INDEX_NAME):
        return {
            "total_documents": 0,
            "by_type": {},
            "top_terms": [],
            "index_exists": False
        }

    # Total count
    count = es.count(index=INDEX_NAME)["count"]

    # Breakdown by file type
    by_type = {}
    try:
        type_agg = es.search(
            index=INDEX_NAME,
            body={
                "size": 0,
                "aggs": {
                    "file_types": {
                        "terms": {
                            "field": "file_type",
                            "size": 20
                        }
                    }
                }
            }
        )
        for bucket in type_agg["aggregations"]["file_types"]["buckets"]:
            by_type[bucket["key"]] = bucket["doc_count"]
    except Exception as e:
        print(f"Error getting type breakdown: {e}")

    # Top 10 most frequent terms using terms aggregation
    top_terms = []
    try:
        # Use a regex exclude to filter out common stop words and field names
        stop_pattern = "name|description|category|price|stock|department|role|skills|experience_years|difficulty|col_.*|row_.*"
        result = es.search(
            index=INDEX_NAME,
            body={
                "size": 0,
                "aggs": {
                    "frequent_terms": {
                        "terms": {
                            "field": "content",
                            "size": 10,
                            "exclude": stop_pattern
                        }
                    }
                }
            }
        )
        for bucket in result["aggregations"]["frequent_terms"]["buckets"]:
            top_terms.append({
                "term": bucket["key"],
                "doc_count": bucket["doc_count"]
            })
    except Exception as e:
        print(f"Top terms aggregation failed: {e}")

    return {
        "total_documents": count,
        "by_type": by_type,
        "top_terms": top_terms,
        "index_exists": True
    }

