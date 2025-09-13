// Vulna Dashboard - AI Functions Module

// AI Chat Functions
function openAIChat(vulnId) {
    const chatSection = document.getElementById('aiChatSection');
    chatSection.style.display = chatSection.style.display === 'none' ? 'block' : 'none';
    
    if (chatSection.style.display === 'block') {
        document.getElementById('chatInput').focus();
    }
}

function sendAIMessage(vulnId) {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    const chatHistory = document.getElementById('chatHistory');
    
    // Add user message safely
    const userDiv = document.createElement('div');
    userDiv.style.marginBottom = '10px';
    userDiv.style.textAlign = 'right';
    userDiv.innerHTML = `<strong style="color: #00ff00;">You:</strong> `;
    userDiv.appendChild(document.createTextNode(message));
    chatHistory.appendChild(userDiv);
    
    input.value = '';
    
    // Add loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'aiLoading';
    loadingDiv.style.marginBottom = '10px';
    loadingDiv.innerHTML = '<strong style="color: #0088ff;">AI:</strong> <em>Thinking...</em>';
    chatHistory.appendChild(loadingDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    // Send to AI
    fetch(`/api/vulnerability/${vulnId}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        loadingDiv.remove();
        
        const responseDiv = document.createElement('div');
        responseDiv.style.marginBottom = '15px';
        responseDiv.innerHTML = '<strong style="color: #0088ff;">AI:</strong>';
        
        const contentDiv = document.createElement('div');
        contentDiv.style.background = '#2d2d2d';
        contentDiv.style.padding = '10px';
        contentDiv.style.borderRadius = '5px';
        contentDiv.style.marginTop = '5px';
        contentDiv.style.whiteSpace = 'pre-wrap';
        contentDiv.style.borderLeft = '3px solid #0088ff';
        contentDiv.textContent = data.success ? data.ai_response : `Error: ${data.message}`;
        
        responseDiv.appendChild(contentDiv);
        chatHistory.appendChild(responseDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    })
    .catch(error => {
        loadingDiv.remove();
        const errorDiv = document.createElement('div');
        errorDiv.style.marginBottom = '10px';
        errorDiv.innerHTML = '<strong style="color: #ff0000;">Error:</strong> ';
        errorDiv.appendChild(document.createTextNode(error.message));
        chatHistory.appendChild(errorDiv);
    });
}

function generatePoC(vulnId) {
    const pocSection = document.getElementById('pocSection');
    const pocContent = document.getElementById('pocContent');
    
    pocSection.style.display = 'block';
    pocContent.textContent = 'Generating Proof of Concept... 🔄';
    
    fetch(`/api/vulnerability/${vulnId}/generate-poc`, { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        pocContent.textContent = data.success ? data.proof_of_concept : `❌ PoC Generation Failed: ${data.message}`;
        showNotification(data.success ? '✅ PoC generated!' : '❌ PoC generation failed', data.success ? 'success' : 'error');
    })
    .catch(error => {
        pocContent.textContent = `❌ Error: ${error.message}`;
        showNotification('❌ PoC generation error', 'error');
    });
}

function analyzeExploitation(vulnId) {
    // Create safe analysis section
    let exploitSection = document.getElementById('exploitAnalysisSection');
    if (!exploitSection) {
        const modalContent = document.getElementById('modalContent');
        exploitSection = document.createElement('div');
        exploitSection.id = 'exploitAnalysisSection';
        exploitSection.style.marginTop = '20px';
        exploitSection.innerHTML = `
            <h3>🔍 Exploitation Analysis</h3>
            <div id="exploitContent" style="background: #1a1a1a; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; border-left: 3px solid #ffff00; max-height: 400px; overflow-y: auto;">
                Analyzing exploitation vectors... 🔄
            </div>
        `;
        modalContent.appendChild(exploitSection);
    } else {
        exploitSection.style.display = 'block';
    }
    
    const exploitContent = document.getElementById('exploitContent');
    exploitContent.textContent = 'Analyzing attack vectors and exploitation methods... 🔄';
    
    fetch(`/api/vulnerability/${vulnId}/analyze-exploitation`, { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.exploitation_analysis) {
            exploitContent.textContent = data.exploitation_analysis;
            exploitContent.style.borderLeftColor = '#ffff00';
        } else {
            exploitContent.textContent = `❌ Analysis failed: ${data.message || 'Unknown error'}`;
            exploitContent.style.borderLeftColor = '#ff0000';
        }
    })
    .catch(error => {
        exploitContent.textContent = `❌ Network Error: ${error.message}`;
        exploitContent.style.borderLeftColor = '#ff0000';
    });
}

function autoTestVulnerability(vulnId) {
    // Create safe auto test section
    let autoTestSection = document.getElementById('autoTestSection');
    if (!autoTestSection) {
        const modalContent = document.getElementById('modalContent');
        autoTestSection = document.createElement('div');
        autoTestSection.id = 'autoTestSection';
        autoTestSection.style.marginTop = '20px';
        autoTestSection.innerHTML = `
            <h3>⚡ Automated Vulnerability Testing</h3>
            <div id="autoTestContent" style="background: #1a1a1a; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; border-left: 3px solid #00ff00; max-height: 400px; overflow-y: auto;">
                Running comprehensive automated analysis... 🔄
            </div>
        `;
        modalContent.appendChild(autoTestSection);
    } else {
        autoTestSection.style.display = 'block';
    }
    
    const autoTestContent = document.getElementById('autoTestContent');
    autoTestContent.textContent = 'Performing automated vulnerability testing... 🔄';
    
    fetch(`/api/vulnerability/${vulnId}/auto-test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success && data.automated_analysis) {
            autoTestContent.textContent = data.automated_analysis;
            autoTestContent.style.borderLeftColor = '#00ff00';
        } else {
            autoTestContent.textContent = `❌ Auto-test failed: ${data.message || 'Unknown error'}`;
            autoTestContent.style.borderLeftColor = '#ff0000';
        }
    })
    .catch(error => {
        autoTestContent.textContent = `❌ Network Error: ${error.message}`;
        autoTestContent.style.borderLeftColor = '#ff0000';
    });
}
