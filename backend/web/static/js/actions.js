// Vulna Dashboard - Action Functions with Complete Browser and Data Management

function startBrowser() {
    showNotification('🚀 Starting browser...', 'success');
    
    fetch('/api/browser/start', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(`✅ ${data.message}`, 'success');
            } else {
                showNotification(`❌ ${data.message}`, 'error');
            }
        })
        .catch(error => {
            showNotification('❌ Failed to start browser: ' + error.message, 'error');
        });
}

function testProxy() {
    showNotification('🔍 Testing proxy connection...', 'success');
    
    fetch('/api/browser/test', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const message = `🔍 PROXY TEST RESULTS:
                
Direct Proxy: ${data.proxy_direct_test ? '✅ WORKING' : '❌ FAILED'}
Recent Captures: ${data.recent_requests_captured} requests
Test Time: ${data.test_time ? data.test_time.toFixed(2) : 'N/A'}s

${data.proxy_response ? 'Proxy IP: ' + JSON.stringify(data.proxy_response) : ''}

INSTRUCTIONS:
${data.instructions ? data.instructions.join('\n') : 'No additional instructions'}`;
                showNotification(message, data.proxy_direct_test ? 'success' : 'error');
            } else {
                showNotification(`❌ ${data.message}`, 'error');
            }
        })
        .catch(error => {
            showNotification('❌ Proxy test failed: ' + error.message, 'error');
        });
}

function exportRequests() {
    const data = JSON.stringify(allRequests, null, 2);
    downloadJSON(data, 'vulna_requests.json');
    showNotification('📤 Requests exported successfully', 'success');
}

function exportFindings() {
    const data = JSON.stringify(allFindings, null, 2);
    downloadJSON(data, 'vulna_findings.json');
    showNotification('📤 Findings exported successfully', 'success');
}

function downloadJSON(data, filename) {
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function clearData() {
    if (confirm('Are you sure you want to clear all data? This will delete the data files.')) {
        fetch('/api/clear', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message || 'Data cleared successfully', 'success');
                    // Clear local data immediately
                    allRequests = [];
                    allFindings = [];
                    stats = {};
                    updateDisplay();
                } else {
                    showNotification(data.message || 'Failed to clear data', 'error');
                }
            })
            .catch(error => {
                showNotification('❌ Clear data failed: ' + error.message, 'error');
            });
    }
}

function refreshData() {
    showNotification('🔄 Refreshing data...', 'success');
    
    // Refresh stats
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            stats = data;
            updateStats();
        })
        .catch(error => console.log('Failed to refresh stats:', error));
        
    // Refresh requests
    fetch('/api/requests')
        .then(response => response.json())
        .then(data => {
            allRequests = data;
            updateRequests();
        })
        .catch(error => console.log('Failed to refresh requests:', error));
        
    // Refresh findings
    fetch('/api/findings')
        .then(response => response.json())
        .then(data => {
            allFindings = data;
            updateFindings();
        })
        .catch(error => console.log('Failed to refresh findings:', error));
    
    setTimeout(() => {
        showNotification('✅ Data refreshed', 'success');
    }, 1000);
}

// Additional helper functions for future features
function filterRequestsByMethod(method) {
    const filteredRequests = allRequests.filter(req => req.method === method);
    console.log(`Filtered ${filteredRequests.length} ${method} requests`);
    return filteredRequests;
}

function filterFindingsByRisk(riskLevel) {
    const filteredFindings = allFindings.filter(finding => finding.risk_level === riskLevel);
    console.log(`Filtered ${filteredFindings.length} ${riskLevel} risk findings`);
    return filteredFindings;
}

function getStatsSnapshot() {
    return {
        timestamp: new Date().toISOString(),
        requests: allRequests.length,
        findings: allFindings.length,
        high_risk: allFindings.filter(f => f.risk_level === 'HIGH').length,
        methods: [...new Set(allRequests.map(r => r.method))],
        domains: [...new Set(allRequests.map(r => {
            try {
                return new URL(r.url).hostname;
            } catch {
                return 'unknown';
            }
        }))]
    };
}
