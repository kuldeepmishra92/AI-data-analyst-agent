// Frontend Application State
const state = {
    activeFilename: null,
    activeReportPath: null,
    filesQueue: [],
};

// DOM Elements
const elements = {
    // Navigation
    navUpload: document.getElementById('btn-nav-upload'),
    navCleaning: document.getElementById('btn-nav-cleaning'),
    navCharts: document.getElementById('btn-nav-charts'),
    navSql: document.getElementById('btn-nav-sql'),
    navInsights: document.getElementById('btn-nav-insights'),
    navHistory: document.getElementById('btn-nav-history'),
    
    // Page Sections
    panels: document.querySelectorAll('.panel'),
    pageTitle: document.getElementById('page-title'),
    pageSubtitle: document.getElementById('page-subtitle'),
    
    // Action buttons
    btnTriggerPipeline: document.getElementById('btn-trigger-pipeline'),
    btnDownloadReport: document.getElementById('btn-download-report'),
    
    // Toast
    toast: document.getElementById('toast-notification'),
    toastMessage: document.getElementById('toast-message'),
    
    // Upload Panel
    dropzone: document.getElementById('file-dropzone'),
    fileInput: document.getElementById('file-input'),
    uploadProgress: document.getElementById('upload-progress-container'),
    uploadStatus: document.getElementById('upload-status-label'),
    uploadPercent: document.getElementById('upload-percent'),
    uploadProgressFill: document.getElementById('upload-progress-fill'),
    filesEmpty: document.getElementById('uploaded-files-empty'),
    filesList: document.getElementById('uploaded-files-list'),
    
    // Data Preview Table
    previewEmpty: document.getElementById('table-preview-empty'),
    previewTable: document.getElementById('data-preview-table'),
    previewThead: document.getElementById('data-preview-thead'),
    previewTbody: document.getElementById('data-preview-tbody'),
    badgeSheet: document.getElementById('badge-sheet-name'),
    
    // Cleaning & Profiling Panel
    valFinalShape: document.getElementById('val-final-shape'),
    valDuplicatesRemoved: document.getElementById('val-duplicates-removed'),
    valMissingImputed: document.getElementById('val-missing-imputed'),
    valEmptyRows: document.getElementById('val-empty-rows'),
    cleaningEmpty: document.getElementById('cleaning-actions-empty'),
    cleaningList: document.getElementById('cleaning-actions-list'),
    profilingEmpty: document.getElementById('profiling-table-empty'),
    profilingTable: document.getElementById('profiling-table'),
    profilingTbody: document.getElementById('profiling-tbody'),
    
    // Charts Panel
    chartsEmpty: document.getElementById('charts-gallery-empty'),
    chartsGallery: document.getElementById('charts-gallery'),
    
    // SQL Panel
    sqlExamplesEmpty: document.getElementById('sql-examples-empty'),
    sqlExamplesList: document.getElementById('sql-examples-list'),
    sqlNlInput: document.getElementById('sql-nl-input'),
    btnRunQuery: document.getElementById('btn-run-query'),
    querySqlBox: document.getElementById('query-sql-box'),
    querySqlCode: document.getElementById('query-sql-code'),
    queryOutputEmpty: document.getElementById('query-output-empty'),
    queryOutputContainer: document.getElementById('query-output-container'),
    queryAnswerText: document.getElementById('query-answer-text'),
    queryResultsTable: document.getElementById('query-results-table'),
    queryResultsThead: document.getElementById('query-results-thead'),
    queryResultsTbody: document.getElementById('query-results-tbody'),
    
    // Insights Panel
    insightsEmpty: document.getElementById('insights-empty'),
    insightsContainer: document.getElementById('insights-container'),
    listKeyObservations: document.getElementById('list-key-observations'),
    listDataQuality: document.getElementById('list-data-quality'),
    listRecommendations: document.getElementById('list-recommendations'),
    
    // Power BI Panel
    pbiEmpty: document.getElementById('pbi-empty'),
    pbiContainer: document.getElementById('pbi-container'),
    pbiKpiList: document.getElementById('pbi-kpi-list'),
    pbiVisualList: document.getElementById('pbi-visual-list'),
    pbiFilterList: document.getElementById('pbi-filter-list'),
    pbiLayoutAdvice: document.getElementById('pbi-layout-advice'),
    
    // History Panel
    historyEmpty: document.getElementById('history-empty'),
    historyTable: document.getElementById('history-table'),
    historyTbody: document.getElementById('history-tbody'),
};

// Event Listeners for Navigation
const menuConfig = {
    'btn-nav-upload': { title: 'Upload Excel Datasets', subtitle: 'Add Excel tables to clean, profile, and search using AI-generated SQL queries.' },
    'btn-nav-cleaning': { title: 'Scrub & Profile Summary', subtitle: 'View duplicates removed, null formatting inputs, and automatic type mapping.' },
    'btn-nav-charts': { title: 'AI-Generated Charts Gallery', subtitle: 'Browse structural visual patterns identified across dataset dimensions.' },
    'btn-nav-sql': { title: 'Natural Language SQL Sandbox', subtitle: 'Construct SQL scripts from natural language questions or run suggestions.' },
    'btn-nav-insights': { title: 'AI Insights & Recommendations', subtitle: 'Inspect professional summaries and recommended Power BI layouts.' },
    'btn-nav-history': { title: 'Analysis Logs & Runs', subtitle: 'View previous SQLite run history logs and download reports.' }
};

document.querySelectorAll('.sidebar-menu a').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Navigation active styling
        document.querySelectorAll('.sidebar-menu a').forEach(el => el.classList.remove('active'));
        link.classList.add('active');
        
        // Show target panel
        const targetId = link.getAttribute('href').substring(1);
        elements.panels.forEach(panel => {
            if (panel.id === targetId) {
                panel.classList.add('active');
            } else {
                panel.classList.remove('active');
            }
        });
        
        // Set titles
        const config = menuConfig[link.id];
        if (config) {
            elements.pageTitle.textContent = config.title;
            elements.pageSubtitle.textContent = config.subtitle;
        }
        
        // If history is loaded
        if (targetId === 'history-section') {
            loadHistory();
        }
    });
});

// Toast Helper
function showToast(message, type = 'success') {
    elements.toastMessage.textContent = message;
    elements.toast.className = `toast ${type === 'error' ? 'badge-danger' : ''}`;
    elements.toast.classList.remove('hidden');
    setTimeout(() => {
        elements.toast.classList.add('hidden');
    }, 4000);
}

// Drag & Drop Handlers
elements.dropzone.addEventListener('click', () => elements.fileInput.click());

elements.dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    elements.dropzone.classList.add('dragover');
});

elements.dropzone.addEventListener('dragleave', () => {
    elements.dropzone.classList.remove('dragover');
});

elements.dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    elements.dropzone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFilesUpload(files);
    }
});

elements.fileInput.addEventListener('change', (e) => {
    const files = e.target.files;
    if (files.length > 0) {
        handleFilesUpload(files);
    }
});

// Handle File Upload Process
async function handleFilesUpload(files) {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }
    
    // UI state upload
    elements.uploadProgress.classList.remove('hidden');
    elements.uploadStatus.textContent = 'Uploading files to server...';
    elements.uploadPercent.textContent = '20%';
    elements.uploadProgressFill.style.width = '20%';
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            elements.uploadPercent.textContent = '100%';
            elements.uploadProgressFill.style.width = '100%';
            
            // Show successful uploads in target queue
            showToast('Files uploaded and validated successfully!');
            setTimeout(() => {
                elements.uploadProgress.classList.add('hidden');
            }, 1000);
            
            updateFilesQueue(data.results);
        } else {
            throw new Error(data.message || 'Failed to upload files.');
        }
    } catch (err) {
        elements.uploadPercent.textContent = '0%';
        elements.uploadProgressFill.style.width = '0%';
        elements.uploadStatus.textContent = 'Upload failed.';
        showToast(err.message, 'error');
    }
}

// Update Target Queue UI
function updateFilesQueue(results) {
    elements.filesEmpty.classList.add('hidden');
    elements.filesList.classList.remove('hidden');
    elements.filesList.innerHTML = '';
    
    state.filesQueue = results.filter(r => r.success);
    
    if (state.filesQueue.length === 0) {
        elements.filesEmpty.classList.remove('hidden');
        elements.filesList.classList.add('hidden');
        elements.btnTriggerPipeline.disabled = true;
        return;
    }
    
    state.filesQueue.forEach((file, index) => {
        const li = document.createElement('li');
        li.className = 'file-item';
        li.innerHTML = `
            <div class="file-item-info">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <span>${file.filename} (${(file.file_size / 1024).toFixed(1)} KB)</span>
            </div>
            <span class="badge bg-success">${file.sheets_count} Sheets</span>
        `;
        li.style.cursor = 'pointer';
        
        // Active click shows table preview of that file
        li.addEventListener('click', () => {
            document.querySelectorAll('.file-item').forEach(el => el.style.borderColor = 'var(--border)');
            li.style.borderColor = 'var(--primary)';
            selectActiveFile(file);
        });
        
        elements.filesList.appendChild(li);
    });
    
    // Select first file automatically
    selectActiveFile(state.filesQueue[0]);
    elements.btnTriggerPipeline.disabled = false;
}

// Select Target File & Show Preview
function selectActiveFile(file) {
    state.activeFilename = file.filename;
    elements.badgeSheet.textContent = `${file.filename} > ${file.sheets[0]}`;
    
    // Render Preview
    const preview = file.preview;
    if (preview && preview.columns.length > 0) {
        elements.previewEmpty.classList.add('hidden');
        elements.previewTable.classList.remove('hidden');
        
        // Header
        elements.previewThead.innerHTML = `<tr>${preview.columns.map(c => `<th>${c}</th>`).join('')}</tr>`;
        // Body
        elements.previewTbody.innerHTML = preview.rows.map(row => 
            `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`
        ).join('');
    } else {
        elements.previewEmpty.classList.remove('hidden');
        elements.previewTable.classList.add('hidden');
    }
}

// Trigger Agentic Analysis Pipeline
elements.btnTriggerPipeline.addEventListener('click', async () => {
    if (!state.activeFilename) return;
    
    elements.btnTriggerPipeline.disabled = true;
    elements.btnTriggerPipeline.innerHTML = `<span class="spinner"></span> Analyzing dataset...`;
    showToast('AI analysis started. Chaining LangGraph agents...', 'info');
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: state.activeFilename })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('AI analysis completed successfully!');
            populateAnalysisResults(data);
        } else {
            throw new Error(data.detail || 'Pipeline analysis execution failed.');
        }
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        elements.btnTriggerPipeline.disabled = false;
        elements.btnTriggerPipeline.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
            </svg>
            Run Complete AI Analysis
        `;
    }
});

// Populate Analysis Data into UI panels
function populateAnalysisResults(data) {
    state.activeReportPath = data.report_path;
    elements.btnDownloadReport.disabled = false;
    elements.btnRunQuery.disabled = false;
    
    // 1. Cleaning summary cards
    elements.valFinalShape.textContent = `${data.profile_summary.total_rows} x ${data.profile_summary.total_columns}`;
    elements.valDuplicatesRemoved.textContent = data.cleaning_summary.duplicates_removed;
    elements.valMissingImputed.textContent = data.cleaning_summary.missing_values_imputed;
    elements.valEmptyRows.textContent = data.cleaning_summary.empty_rows_removed;
    
    // Cleaning action list
    elements.cleaningEmpty.classList.add('hidden');
    elements.cleaningList.classList.remove('hidden');
    elements.cleaningList.innerHTML = data.cleaning_summary.actions_taken.map(act => 
        `<li>${act}</li>`
    ).join('') || '<li>No major changes required. Dataset clean.</li>';
    
    // 2. Profiling Table
    elements.profilingEmpty.classList.add('hidden');
    elements.profilingTable.classList.remove('hidden');
    elements.profilingTbody.innerHTML = data.profile_summary.columns.map(col => {
        let statsStr = '';
        if (col.statistics) {
            statsStr = Object.entries(col.statistics)
                .map(([k, v]) => `<strong>${k}:</strong> ${typeof v === 'number' ? v.toFixed(2) : v}`)
                .join(' | ');
        }
        return `
            <tr>
                <td><strong>${col.name}</strong></td>
                <td><span class="badge">${col.type}</span></td>
                <td>${col.non_null_count}</td>
                <td>${col.null_count}</td>
                <td>${col.unique_count}</td>
                <td><div style="font-size:11px; max-width:400px; white-space:normal;">${statsStr}</div></td>
            </tr>
        `;
    }).join('');
    
    // 3. Charts Gallery
    elements.chartsEmpty.classList.add('hidden');
    elements.chartsGallery.classList.remove('hidden');
    data.charts.forEach((url, i) => {
        const titleEl = document.getElementById(`chart-title-${i}`);
        const imgEl = document.getElementById(`chart-img-${i}`);
        if (imgEl && titleEl) {
            // Append timestamp cache buster
            imgEl.src = `${url}?t=${new Date().getTime()}`;
            
            // Extract nice title from name
            const basename = url.substring(url.lastIndexOf('/') + 1);
            const cleanedName = basename.split('.')[0].replace(data.table_name + '_', '').replace(/_/g, ' ');
            titleEl.textContent = cleanedName.charAt(0).toUpperCase() + cleanedName.slice(1);
        }
    });
    
    // 4. SQL Queries Suggestions
    elements.sqlExamplesEmpty.classList.add('hidden');
    elements.sqlExamplesList.classList.remove('hidden');
    elements.sqlExamplesList.innerHTML = data.default_queries.map((q, i) => `
        <div class="sql-example-card" onclick="selectSqlQuery('${q.query.replace(/'/g, "\\'")}')">
            <h4>${q.title}</h4>
            <pre><code>${q.query}</code></pre>
        </div>
    `).join('');
    
    // 5. Insights Panels
    elements.insightsEmpty.classList.add('hidden');
    elements.insightsContainer.classList.remove('hidden');
    elements.listKeyObservations.innerHTML = data.insights.key_observations.map(obs => `<li>${obs}</li>`).join('');
    elements.listDataQuality.innerHTML = data.insights.data_quality_notes.map(note => `<li>${note}</li>`).join('');
    elements.listRecommendations.innerHTML = data.insights.recommendations.map(rec => `<li>${rec}</li>`).join('');
    
    // 6. Power BI recommendations
    elements.pbiEmpty.classList.add('hidden');
    elements.pbiContainer.classList.remove('hidden');
    elements.pbiKpiList.innerHTML = data.dashboard_recommendations.kpis.map(kpi => `
        <li><strong>${kpi.name}</strong>: ${kpi.description} <code class="badge bg-success" style="float:right;">DAX: ${kpi.formula}</code></li>
    `).join('');
    elements.pbiVisualList.innerHTML = data.dashboard_recommendations.visuals.map(vis => `
        <li><strong>${vis.title} (${vis.type})</strong>: ${vis.description}</li>
    `).join('');
    elements.pbiFilterList.innerHTML = data.dashboard_recommendations.filters.map(filt => `
        <li><strong>Slicer on '${filt.column}'</strong>: ${filt.reason}</li>
    `).join('');
    elements.pbiLayoutAdvice.textContent = data.dashboard_recommendations.layout_description;
    
    // Jump to the Cleaning panel automatically to show results
    elements.navCleaning.click();
}

// Select default query and paste to sandbox
window.selectSqlQuery = function(query) {
    elements.sqlNlInput.value = query;
    elements.navSql.click();
};

// SQL terminal ask endpoint execution
elements.btnRunQuery.addEventListener('click', async () => {
    const question = elements.sqlNlInput.value.trim();
    if (!question) return;
    
    elements.btnRunQuery.disabled = true;
    elements.btnRunQuery.innerHTML = `<span class="spinner"></span> Running query...`;
    
    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            elements.queryOutputEmpty.classList.add('hidden');
            elements.queryOutputContainer.classList.remove('hidden');
            
            // Show generated SQL script
            elements.querySqlBox.classList.remove('hidden');
            elements.querySqlCode.textContent = data.query;
            
            // Display textual answer
            elements.queryAnswerText.innerHTML = data.answer.replace(/\n/g, '<br>');
            
            // Draw grid output
            if (data.result_rows && data.result_rows.length > 0) {
                elements.queryResultsTable.classList.remove('hidden');
                elements.queryResultsThead.innerHTML = `<tr>${data.result_columns.map(c => `<th>${c}</th>`).join('')}</tr>`;
                elements.queryResultsTbody.innerHTML = data.result_rows.map(row => `
                    <tr>${row.map(cell => `<td>${cell !== null ? cell : 'NULL'}</td>`).join('')}</tr>
                `).join('');
            } else {
                elements.queryResultsTable.classList.add('hidden');
                elements.queryResultsTbody.innerHTML = '';
            }
        } else {
            throw new Error(data.detail || 'SQL query sandbox failed.');
        }
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        elements.btnRunQuery.disabled = false;
        elements.btnRunQuery.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
            Query Dataset
        `;
    }
});

// Download Report Button Trigger
elements.btnDownloadReport.addEventListener('click', () => {
    if (!state.activeReportPath) return;
    window.open(`/download-report?path=${encodeURIComponent(state.activeReportPath)}`, '_blank');
});

// Load History from SQLite
async function loadHistory() {
    try {
        const response = await fetch('/history');
        const data = await response.json();
        
        if (response.ok) {
            if (data.length > 0) {
                elements.historyEmpty.classList.add('hidden');
                elements.historyTable.classList.remove('hidden');
                elements.historyTbody.innerHTML = data.map(run => `
                    <tr>
                        <td><strong>#${run.id}</strong></td>
                        <td>${run.filename}</td>
                        <td>${run.upload_time}</td>
                        <td>${run.rows}</td>
                        <td>${run.columns}</td>
                        <td>${run.missing_values}</td>
                        <td>${run.duplicates}</td>
                        <td>
                            <button class="history-action-btn" onclick="downloadHistoryReport('${run.report_path.replace(/\\/g, "\\\\")}')">
                                Download MD Report
                            </button>
                        </td>
                    </tr>
                `).join('');
            } else {
                elements.historyEmpty.classList.remove('hidden');
                elements.historyTable.classList.add('hidden');
            }
        }
    } catch (err) {
        console.error('Failed to load history:', err);
    }
}

// Download report direct from history row
window.downloadHistoryReport = function(path) {
    window.open(`/download-report?path=${encodeURIComponent(path)}`, '_blank');
};

// Initial load check
window.addEventListener('DOMContentLoaded', () => {
    loadHistory();
});
