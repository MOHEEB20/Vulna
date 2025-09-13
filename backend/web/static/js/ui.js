// Vulna Dashboard - UI Update Functions

function updateStats() {
    const statsGrid = document.getElementById('statsGrid');
    const requestCount = document.getElementById('requestCount');
    const findingCount = document.getElementById('findingCount');
    
    if (requestCount) requestCount.textContent = allRequests.length;
    if (findingCount) findingCount.textContent = allFindings.length;
    
    if (statsGrid) {
        statsGrid.innerHTML = `
            <div class="stat-card">
                <div class="stat-number">${stats.total_requests || 0}</div>
                <div class="stat-label">Total Requests</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${stats.total_findings || 0}</div>
                <div class="stat-label">Vulnerabilities</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${Object.keys(stats.methods || {}).length}</div>
                <div class="stat-label">HTTP Methods</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${Object.keys(stats.domains || {}).length}</div>
                <div class="stat-label">Domains</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${(stats.risks && stats.risks.HIGH) || 0}</div>
                <div class="stat-label">High Risk</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${new Date(stats.last_updated || Date.now()).toLocaleTimeString()}</div>
                <div class="stat-label">Last Updated</div>
            </div>
        `;
    }
}

function updateRequests() {
    const requestsArea = document.getElementById('requestsArea') || document.getElementById('requestsList');
    
    if (!requestsArea) return;
    
    // Show latest 100 requests
    const recentRequests = allRequests.slice(-100).reverse();
    
    requestsArea.innerHTML = recentRequests.map(req => `
        <div class="request-item ${req.method}" onclick="showRequestDetails(${JSON.stringify(req).replace(/"/g, '&quot;')})">
            <span class="request-method method-${req.method}">${req.method}</span>
            <span class="url">${truncateUrl(req.url, 60)}</span>
            <div class="timestamp">${new Date(req.timestamp).toLocaleString()}</div>
        </div>
    `).join('');
}

function updateFindings() {
    const findingsArea = document.getElementById('findingsArea') || document.getElementById('findingsList');
    
    if (!findingsArea) return;
    
    // Show latest 50 findings
    const recentFindings = allFindings.slice(-50).reverse();
    
    findingsArea.innerHTML = recentFindings.map(finding => `
        <div class="finding-item ${finding.risk_level}" onclick="showFindingDetails(${JSON.stringify(finding).replace(/"/g, '&quot;')})">
            <span class="risk-badge risk-${finding.risk_level}">${finding.risk_level}</span>
            <div class="finding-title">${finding.title || 'Security Finding'}</div>
            <div class="finding-description">${truncateText(finding.description || '', 100)}</div>
            <div class="timestamp">${new Date(finding.timestamp || Date.now()).toLocaleString()}</div>
        </div>
    `).join('');
}

function createRequestItem(request) {
    const div = document.createElement('div');
    div.className = `request-item ${request.method}`;
    div.onclick = () => showRequestDetails(request);
    
    div.innerHTML = `
        <div>
            <span class="request-method method-${request.method}">${request.method}</span>
            <span>${truncateUrl(request.url, 60)}</span>
        </div>
        <div style="font-size: 0.8em; color: #999; margin-top: 5px;">
            ${new Date(request.timestamp).toLocaleTimeString()}
        </div>
    `;
    
    return div;
}

function createFindingItem(finding) {
    const div = document.createElement('div');
    div.className = `finding-item ${finding.risk_level}`;
    div.onclick = () => showFindingDetails(finding);
    
    div.innerHTML = `
        <div>
            <span class="risk-badge risk-${finding.risk_level}">${finding.risk_level}</span>
            <span>${finding.title || 'Security Finding'}</span>
        </div>
        <div style="font-size: 0.8em; color: #999; margin-top: 5px;">
            ${truncateUrl(finding.affected_url || finding.url, 50)} • 
            Confidence: ${Math.round((finding.confidence || 0) * 100)}%
        </div>
    `;
    
    return div;
}

function truncateText(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3) + '...';
}

function truncateUrl(url, maxLength) {
    if (!url) return 'Unknown URL';
    if (url.length <= maxLength) return url;
    return url.substring(0, maxLength - 3) + '...';
}
