// Vulna Dashboard - Browser Controls & Data Management

// Browser Controls
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
                showNotification('✅ Proxy test successful', 'success');
            } else {
                showNotification(`❌ ${data.message}`, 'error');
            }
        })
        .catch(error => {
            showNotification('❌ Proxy test failed: ' + error.message, 'error');
        });
}

// Data Management
function exportRequests() {
    const data = JSON.stringify(allRequests, null, 2);
    downloadJSON(data, 'vulna_requests.json');
}

function exportFindings() {
    const data = JSON.stringify(allFindings, null, 2);
    downloadJSON(data, 'vulna_findings.json');
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
    if (confirm('Are you sure you want to clear all data?')) {
        fetch('/api/clear', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                } else {
                    showNotification(data.message, 'error');
                }
            });
    }
}

function refreshData() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            stats = data;
            updateStats();
        });
        
    fetch('/api/requests')
        .then(response => response.json())
        .then(data => {
            allRequests = data;
            updateRequests();
        });
        
    fetch('/api/findings')
        .then(response => response.json())
        .then(data => {
            allFindings = data;
            updateFindings();
        });
}

// Test Request for Vulnerabilities
function testRequestForVulns(request) {
    showNotification('🔍 Testing request for vulnerabilities...', 'success');
    
    fetch('/api/test-request-vulnerabilities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('✅ Vulnerability test completed!', 'success');
        } else {
            showNotification('❌ Test failed: ' + data.message, 'error');
        }
    })
    .catch(error => {
        showNotification('❌ Test error: ' + error.message, 'error');
    });
}

// Export functions
window.VulnaControls = {
    startBrowser,
    testProxy,
    exportRequests,
    exportFindings,
    clearData,
    refreshData,
    testRequestForVulns
};
