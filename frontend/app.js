/**
 * Mini Search Engine - Frontend Application Logic
 * Handles tab switching, indexing, search, pagination, stats, and "did you mean".
 */

const API = '';  // Same origin since FastAPI serves frontend
let currentPage = 1;
let lastSearchParams = {};

// ─── Tab Switching ──────────────────────────
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('tab' + capitalize(btn.dataset.tab)).classList.add('active');
        if (btn.dataset.tab === 'stats') loadStats();
    });
});

function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

// ─── Init: Load Formats & Health ────────────
window.addEventListener('DOMContentLoaded', () => {
    loadFormats();
    checkHealth();
});

async function checkHealth() {
    try {
        const res = await fetch(`${API}/api/health`);
        const data = await res.json();
        const el = document.getElementById('healthStatus');
        if (data.status === 'ok') {
            el.innerHTML = `✅ Elasticsearch ${data.elasticsearch.version} connected`;
            el.style.color = 'var(--success)';
        } else {
            el.innerHTML = `❌ Elasticsearch: ${data.message}`;
            el.style.color = 'var(--danger)';
        }
    } catch (e) {
        const el = document.getElementById('healthStatus');
        el.innerHTML = '❌ Cannot connect to backend server';
        el.style.color = 'var(--danger)';
    }
}

async function loadFormats() {
    try {
        const res = await fetch(`${API}/api/formats`);
        const data = await res.json();
        const grid = document.getElementById('formatsGrid');
        grid.innerHTML = data.formats.map(f => `
            <label class="checkbox-label" id="formatLabel_${f.id}">
                <input type="checkbox" value="${f.id}" checked> ${f.label}
            </label>
        `).join('');
    } catch (e) {
        document.getElementById('formatsGrid').innerHTML =
            '<p style="color:var(--danger)">Failed to load formats</p>';
    }
}

// ─── Build Index ────────────────────────────
async function buildIndex() {
    const folder = document.getElementById('folderPath').value.trim();
    if (!folder) {
        showStatus('indexResult', 'Please enter a folder path.', 'error');
        return;
    }

    const checkboxes = document.querySelectorAll('#formatsGrid input[type="checkbox"]:checked');
    const formats = Array.from(checkboxes).map(cb => cb.value);
    if (formats.length === 0) {
        showStatus('indexResult', 'Please select at least one file format.', 'error');
        return;
    }

    const btn = document.getElementById('buildIndexBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="loader"></span> Indexing...';

    try {
        const res = await fetch(`${API}/api/index`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ folder_path: folder, formats })
        });
        const data = await res.json();
        if (res.ok) {
            let html = `<div class="status status-success">
                <strong>✅ ${data.message}</strong><br>`;
            if (data.stats && data.stats.by_type) {
                html += '<div class="type-breakdown" style="margin-top:10px">';
                for (const [type, count] of Object.entries(data.stats.by_type)) {
                    html += `<span class="type-chip">${type.toUpperCase()} <span class="count">${count}</span></span>`;
                }
                html += '</div>';
            }
            if (data.stats && data.stats.errors && data.stats.errors.length > 0) {
                html += `<br><small style="color:var(--warning)">⚠ ${data.stats.errors.length} warning(s)</small>`;
            }
            html += '</div>';
            document.getElementById('indexResult').innerHTML = html;
        } else {
            showStatus('indexResult', data.detail || 'Indexing failed.', 'error');
        }
    } catch (e) {
        showStatus('indexResult', 'Error: ' + e.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '⚡ Build Index';
    }
}

// ─── Search ─────────────────────────────────
async function doSearch(page = 1) {
    const query = document.getElementById('searchQuery').value.trim();
    if (!query) {
        showStatus('resultsContainer', 'Please enter a search query.', 'error');
        return;
    }

    currentPage = page;
    const dateFrom = document.getElementById('dateFrom').value || null;
    const dateTo = document.getElementById('dateTo').value || null;
    const fileType = document.getElementById('fileTypeFilter').value;
    const fileTypes = fileType ? [fileType] : null;

    lastSearchParams = { query, dateFrom, dateTo, fileTypes };

    const btn = document.getElementById('searchBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="loader"></span>';

    try {
        const res = await fetch(`${API}/api/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query,
                page: currentPage,
                page_size: 5,
                date_from: dateFrom,
                date_to: dateTo,
                file_types: fileTypes
            })
        });
        const data = await res.json();
        if (res.ok) {
            renderResults(data);
        } else {
            showStatus('resultsContainer', data.detail || 'Search failed.', 'error');
            document.getElementById('didYouMean').innerHTML = '';
            document.getElementById('resultsHeader').innerHTML = '';
            document.getElementById('pagination').innerHTML = '';
        }
    } catch (e) {
        showStatus('resultsContainer', 'Error: ' + e.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🔎 Search';
    }
}

function renderResults(data) {
    // Did you mean
    const dymEl = document.getElementById('didYouMean');
    if (data.did_you_mean) {
        dymEl.innerHTML = `<div class="did-you-mean">
            💡 Did you mean: <a onclick="searchSuggestion('${escapeHtml(data.did_you_mean)}')">${escapeHtml(data.did_you_mean)}</a>?
        </div>`;
    } else {
        dymEl.innerHTML = '';
    }

    // Results header
    document.getElementById('resultsHeader').innerHTML = data.total > 0
        ? `<div class="results-header"><span>Found <strong>${data.total}</strong> result${data.total !== 1 ? 's' : ''}</span><span>Page ${data.page} of ${data.total_pages}</span></div>`
        : '';

    // Results
    const container = document.getElementById('resultsContainer');
    if (data.documents.length === 0) {
        container.innerHTML = `<div class="empty-state"><div class="icon">🔍</div><p>No results found for "<strong>${escapeHtml(data.query)}</strong>"</p></div>`;
    } else {
        container.innerHTML = data.documents.map(doc => `
            <div class="result-item">
                <div class="result-meta">
                    <span class="result-filename">📄 ${escapeHtml(doc.filename)}</span>
                    <span class="result-badge badge-type">${doc.file_type.toUpperCase()}</span>
                    <span class="result-badge badge-score">Score: ${doc.score}</span>
                    <span class="result-badge badge-date">${formatDate(doc.modification_date)}</span>
                    ${doc.sub_doc_id !== 'main' ? `<span class="result-badge" style="background:rgba(139,92,246,0.15);color:#a78bfa">${doc.sub_doc_id}</span>` : ''}
                </div>
                <div class="result-snippet">${doc.snippet}</div>
            </div>
        `).join('');
    }

    // Pagination
    const pagEl = document.getElementById('pagination');
    if (data.total_pages > 1) {
        pagEl.innerHTML = `<div class="pagination">
            <button onclick="doSearch(${data.page - 1})" ${data.page <= 1 ? 'disabled' : ''} id="prevPageBtn">← Previous</button>
            <span class="page-info">Page ${data.page} of ${data.total_pages}</span>
            <button onclick="doSearch(${data.page + 1})" ${data.page >= data.total_pages ? 'disabled' : ''} id="nextPageBtn">Next →</button>
        </div>`;
    } else {
        pagEl.innerHTML = '';
    }
}

function searchSuggestion(suggested) {
    document.getElementById('searchQuery').value = suggested;
    doSearch(1);
}

// ─── Stats ──────────────────────────────────
async function loadStats() {
    const btn = document.getElementById('loadStatsBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="loader"></span> Loading...';

    try {
        const res = await fetch(`${API}/api/stats`);
        const data = await res.json();
        const container = document.getElementById('statsContainer');

        if (!data.index_exists) {
            container.innerHTML = `<div class="empty-state"><div class="icon">📭</div><p>No index found. Build an index first.</p></div>`;
            return;
        }

        let html = `<div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">${data.total_documents}</div>
                <div class="stat-label">Total Indexed Documents</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${Object.keys(data.by_type).length}</div>
                <div class="stat-label">File Types</div>
            </div>
        </div>`;

        // Type breakdown
        html += `<div class="card"><div class="card-title"><span class="icon">📁</span> Breakdown by File Type</div>
            <div class="type-breakdown">`;
        for (const [type, count] of Object.entries(data.by_type)) {
            html += `<span class="type-chip">${type.toUpperCase()} <span class="count">${count}</span></span>`;
        }
        html += '</div></div>';

        // Top terms
        if (data.top_terms && data.top_terms.length > 0) {
            html += `<div class="card"><div class="card-title"><span class="icon">🏷️</span> Top 10 Most Frequent Terms</div>
                <div class="terms-list">`;
            data.top_terms.forEach(t => {
                html += `<span class="term-tag">${escapeHtml(t.term)} <small>(${t.doc_count})</small></span>`;
            });
            html += '</div></div>';
        }

        container.innerHTML = html;
    } catch (e) {
        document.getElementById('statsContainer').innerHTML =
            `<div class="status status-error">Error loading stats: ${e.message}</div>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = '📊 Load Stats';
    }
}

// ─── Utilities ──────────────────────────────
function showStatus(elementId, message, type) {
    document.getElementById(elementId).innerHTML =
        `<div class="status status-${type}">${message}</div>`;
}

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function formatDate(isoDate) {
    if (!isoDate) return 'N/A';
    try {
        return new Date(isoDate).toLocaleDateString('en-US', {
            year: 'numeric', month: 'short', day: 'numeric'
        });
    } catch { return isoDate; }
}
