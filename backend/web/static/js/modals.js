// Vulna Dashboard - Enhanced Modal Functions with AI Integration

function showRequestDetails(request) {
    const modal = document.getElementById('detailModal');
    const content = document.getElementById('modalContent');
    
    content.innerHTML = `
        <h2>📥 Request Details</h2>
        <div style="display: grid; grid-template-columns: 1fr auto; gap: 20px; margin-bottom: 20px;">
            <div>
                <p><strong>Method:</strong> ${request.method}</p>
                <p><strong>URL:</strong> ${request.url}</p>
                <p><strong>Timestamp:</strong> ${new Date(request.timestamp).toLocaleString()}</p>
            </div>
            <div>
                <button class="btn btn-inspector" onclick="sendToInspector(${JSON.stringify(request).replace(/"/g, '&quot;')})">
                    🔍 Send to Inspector
                </button>
                <button class="btn" onclick="testRequestForVulns(${JSON.stringify(request).replace(/"/g, '&quot;')})">
                    🚀 Test for Vulnerabilities
                </button>
            </div>
        </div>
        
        <h3>Headers</h3>
        <pre style="background: #2d2d2d; padding: 10px; border-radius: 5px; overflow-x: auto;">${JSON.stringify(request.headers, null, 2)}</pre>
        
        ${request.content || request.body ? `
            <h3>Content</h3>
            <pre style="background: #2d2d2d; padding: 10px; border-radius: 5px; overflow-x: auto; max-height: 200px;">${request.content || request.body}</pre>
        ` : ''}
    `;
    
    modal.style.display = 'block';
}

function showFindingDetails(finding) {
    const modal = document.getElementById('detailModal');
    const content = document.getElementById('modalContent');
    
    // Enhanced vulnerability details display with all AI features
    content.innerHTML = `
        <h2>🔒 Vulnerability Analysis</h2>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
            <div>
                <h3>📋 Basic Information</h3>
                <p><strong>Title:</strong> ${finding.title || 'Security Finding'}</p>
                <p><strong>Risk Level:</strong> <span class="risk-badge risk-${finding.risk_level}">${finding.risk_level}</span></p>
                <p><strong>Risk Score:</strong> ${finding.risk_score || 'N/A'}/10</p>
                <p><strong>Confidence:</strong> ${Math.round((finding.confidence || 0) * 100)}%</p>
                <p><strong>Timestamp:</strong> ${new Date(finding.timestamp || Date.now()).toLocaleString()}</p>
            </div>
            
            <div>
                <h3>🎯 Technical Details</h3>
                <p><strong>URL:</strong> ${finding.affected_url || finding.url || 'Unknown'}</p>
                <p><strong>Method:</strong> ${finding.request_method || 'Unknown'}</p>
                <p><strong>OWASP:</strong> ${(finding.owasp_categories || []).join(', ') || 'Not classified'}</p>
                <p><strong>CWE:</strong> ${(finding.cwe_ids || []).join(', ') || 'Not classified'}</p>
                <p><strong>Parameters:</strong> ${(finding.affected_parameters || []).join(', ') || 'None specified'}</p>
            </div>
        </div>
        
        <div style="margin-bottom: 20px;">
            <h3>📝 Description</h3>
            <div style="background: #2d2d2d; padding: 15px; border-radius: 5px; border-left: 3px solid #00ff00;">
                ${finding.description || 'No description available'}
            </div>
        </div>
        
        <div style="margin-bottom: 20px;">
            <h3>🛠️ Remediation</h3>
            <div style="background: #2d2d2d; padding: 15px; border-radius: 5px; border-left: 3px solid #0088ff;">
                ${finding.suggestion || 'No remediation guidance available'}
            </div>
        </div>
        
        <div style="margin-bottom: 20px;">
            <h3>🤖 AI Actions</h3>
            <div class="ai-actions-grid">
                <button class="btn" onclick="generatePoC('${finding.id}')">🔬 Generate PoC</button>
                <button class="btn" onclick="openAIChat('${finding.id}')">💬 Chat with AI</button>
                <button class="btn" onclick="autoTestVulnerability('${finding.id}')">⚡ Auto Test</button>
                <button class="btn" onclick="analyzeExploitation('${finding.id}')">🔍 Analyze Exploitation</button>
            </div>
        </div>
        
        <div id="aiChatSection" style="display: none; margin-top: 20px;">
            <h3>💬 AI Conversation</h3>
            <div id="chatHistory" class="chat-history">
                <!-- Chat history will appear here -->
            </div>
            <div class="chat-input-container">
                <input type="text" id="chatInput" class="chat-input" placeholder="Ask AI about this vulnerability..." 
                       onkeypress="if(event.key==='Enter') sendAIMessage('${finding.id}')">
                <button class="btn" onclick="sendAIMessage('${finding.id}')">Send</button>
            </div>
        </div>
        
        <div id="pocSection" style="display: none; margin-top: 20px;">
            <h3>🔬 Generated Proof of Concept</h3>
            <div id="pocContent" class="poc-content">
                <!-- PoC will appear here -->
            </div>
        </div>
    `;
    
    modal.style.display = 'block';
}

function closeModal() {
    document.getElementById('detailModal').style.display = 'none';
}

// Placeholder functions for inspector integration (to be implemented)
function sendToInspector(request) {
    showNotification('🔍 Sending to Request Inspector...', 'success');
    // TODO: Implement inspector integration
    console.log('Inspector integration:', request);
}

function testRequestForVulns(request) {
    showNotification('🚀 Running vulnerability tests...', 'success');
    // TODO: Implement vulnerability testing
    console.log('Vulnerability testing:', request);
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('detailModal');
    if (event.target === modal) {
        closeModal();
    }
}
