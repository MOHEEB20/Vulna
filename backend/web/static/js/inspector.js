// Vulna Dashboard - Request Inspector & Tamper Tool

// Request Inspector Functions
function sendToInspector(request) {
    const inspectorModal = document.createElement('div');
    inspectorModal.className = 'modal';
    inspectorModal.style.display = 'block';
    inspectorModal.style.zIndex = '1002';
    
    const modalContent = document.createElement('div');
    modalContent.className = 'modal-content';
    modalContent.style.maxWidth = '1200px';
    modalContent.style.height = '80vh';
    
    const closeBtn = document.createElement('span');
    closeBtn.className = 'close';
    closeBtn.textContent = '×';
    closeBtn.onclick = () => inspectorModal.remove();
    
    const title = document.createElement('h2');
    title.textContent = '🔍 Request Inspector & Tamper Tool';
    
    const content = document.createElement('div');
    content.style.display = 'grid';
    content.style.gridTemplateColumns = '1fr 1fr';
    content.style.gap = '20px';
    content.style.height = 'calc(100% - 60px)';
    
    // Original Request (left side)
    const originalDiv = createOriginalRequestDisplay(request);
    
    // Tamper Interface (right side)
    const tamperDiv = createTamperInterface(request);
    
    content.appendChild(originalDiv);
    content.appendChild(tamperDiv);
    
    modalContent.appendChild(closeBtn);
    modalContent.appendChild(title);
    modalContent.appendChild(content);
    inspectorModal.appendChild(modalContent);
    document.body.appendChild(inspectorModal);
}

function createOriginalRequestDisplay(request) {
    const originalDiv = document.createElement('div');
    const originalTitle = document.createElement('h3');
    originalTitle.textContent = '📥 Original Request (Read-Only)';
    
    const originalContent = document.createElement('pre');
    originalContent.style.background = '#1a1a1a';
    originalContent.style.padding = '15px';
    originalContent.style.borderRadius = '5px';
    originalContent.style.overflow = 'auto';
    originalContent.style.height = '100%';
    originalContent.style.fontFamily = 'monospace';
    originalContent.style.fontSize = '12px';
    originalContent.style.border = '1px solid #333';
    
    const requestText = `Method: ${request.method}
URL: ${request.url}
Timestamp: ${new Date(request.timestamp).toLocaleString()}

Headers:
${JSON.stringify(request.headers, null, 2)}

Body:
${request.body || 'No body'}`;
    
    originalContent.textContent = requestText;
    
    originalDiv.appendChild(originalTitle);
    originalDiv.appendChild(originalContent);
    
    return originalDiv;
}

function createTamperInterface(request) {
    const tamperDiv = document.createElement('div');
    tamperDiv.style.display = 'flex';
    tamperDiv.style.flexDirection = 'column';
    tamperDiv.style.height = '100%';
    
    const tamperTitle = document.createElement('h3');
    tamperTitle.textContent = '🛠️ Tamper Request (Editable)';
    tamperDiv.appendChild(tamperTitle);
    
    // Method selector
    const methodContainer = document.createElement('div');
    methodContainer.style.marginBottom = '10px';
    const methodLabel = document.createElement('label');
    methodLabel.textContent = 'Method: ';
    methodLabel.style.fontWeight = 'bold';
    
    const methodSelect = document.createElement('select');
    methodSelect.id = 'tamperMethod';
    methodSelect.style.background = '#333';
    methodSelect.style.color = 'white';
    methodSelect.style.border = '1px solid #555';
    methodSelect.style.marginLeft = '10px';
    
    ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'].forEach(method => {
        const option = document.createElement('option');
        option.value = method;
        option.textContent = method;
        option.selected = method === request.method;
        methodSelect.appendChild(option);
    });
    
    methodContainer.appendChild(methodLabel);
    methodContainer.appendChild(methodSelect);
    tamperDiv.appendChild(methodContainer);
    
    // URL input
    const urlContainer = document.createElement('div');
    urlContainer.style.marginBottom = '10px';
    const urlLabel = document.createElement('label');
    urlLabel.textContent = 'URL:';
    urlLabel.style.fontWeight = 'bold';
    urlLabel.style.display = 'block';
    
    const urlInput = document.createElement('input');
    urlInput.type = 'text';
    urlInput.id = 'tamperUrl';
    urlInput.value = request.url;
    urlInput.style.width = '100%';
    urlInput.style.background = '#333';
    urlInput.style.color = 'white';
    urlInput.style.border = '1px solid #555';
    urlInput.style.padding = '5px';
    urlInput.style.fontFamily = 'monospace';
    urlInput.style.marginTop = '5px';
    
    urlContainer.appendChild(urlLabel);
    urlContainer.appendChild(urlInput);
    tamperDiv.appendChild(urlContainer);
    
    // Headers textarea
    const headersContainer = document.createElement('div');
    headersContainer.style.marginBottom = '10px';
    headersContainer.style.flex = '1';
    headersContainer.style.display = 'flex';
    headersContainer.style.flexDirection = 'column';
    
    const headersLabel = document.createElement('label');
    headersLabel.textContent = 'Headers:';
    headersLabel.style.fontWeight = 'bold';
    
    const headersTextarea = document.createElement('textarea');
    headersTextarea.id = 'tamperHeaders';
    headersTextarea.value = JSON.stringify(request.headers || {}, null, 2);
    headersTextarea.style.flex = '1';
    headersTextarea.style.background = '#333';
    headersTextarea.style.color = 'white';
    headersTextarea.style.border = '1px solid #555';
    headersTextarea.style.fontFamily = 'monospace';
    headersTextarea.style.fontSize = '11px';
    headersTextarea.style.marginTop = '5px';
    headersTextarea.style.resize = 'vertical';
    
    headersContainer.appendChild(headersLabel);
    headersContainer.appendChild(headersTextarea);
    tamperDiv.appendChild(headersContainer);
    
    // Body textarea
    const bodyContainer = document.createElement('div');
    bodyContainer.style.marginBottom = '10px';
    bodyContainer.style.flex = '1';
    bodyContainer.style.display = 'flex';
    bodyContainer.style.flexDirection = 'column';
    
    const bodyLabel = document.createElement('label');
    bodyLabel.textContent = 'Body:';
    bodyLabel.style.fontWeight = 'bold';
    
    const bodyTextarea = document.createElement('textarea');
    bodyTextarea.id = 'tamperBody';
    bodyTextarea.value = request.body || '';
    bodyTextarea.style.flex = '1';
    bodyTextarea.style.background = '#333';
    bodyTextarea.style.color = 'white';
    bodyTextarea.style.border = '1px solid #555';
    bodyTextarea.style.fontFamily = 'monospace';
    bodyTextarea.style.fontSize = '11px';
    bodyTextarea.style.marginTop = '5px';
    bodyTextarea.style.resize = 'vertical';
    
    bodyContainer.appendChild(bodyLabel);
    bodyContainer.appendChild(bodyTextarea);
    tamperDiv.appendChild(bodyContainer);
    
    // Action buttons
    const buttonsContainer = createTamperButtons();
    tamperDiv.appendChild(buttonsContainer);
    
    return tamperDiv;
}

function createTamperButtons() {
    const buttonsContainer = document.createElement('div');
    buttonsContainer.style.display = 'grid';
    buttonsContainer.style.gridTemplateColumns = '1fr 1fr';
    buttonsContainer.style.gap = '10px';
    buttonsContainer.style.marginTop = '10px';
    
    const buttons = [
        { text: '💉 Add XSS', onclick: () => addPayload('xss'), class: 'btn' },
        { text: '💉 Add SQL', onclick: () => addPayload('sql'), class: 'btn' },
        { text: '📋 Generate cURL', onclick: generateCurlCommand, class: 'btn' },
        { text: '🔥 Generate Burp', onclick: generateBurpRequest, class: 'btn' },
        { text: '🚀 Test Request', onclick: testTamperedRequest, class: 'btn btn-inspector' },
        { text: '💾 Save Template', onclick: saveRequestTemplate, class: 'btn' }
    ];
    
    buttons.forEach(buttonConfig => {
        const button = document.createElement('button');
        button.textContent = buttonConfig.text;
        button.className = buttonConfig.class;
        button.onclick = buttonConfig.onclick;
        buttonsContainer.appendChild(button);
    });
    
    return buttonsContainer;
}

// Payload Functions
function addPayload(type) {
    const urlField = document.getElementById('tamperUrl');
    const bodyField = document.getElementById('tamperBody');
    const headersField = document.getElementById('tamperHeaders');
    
    if (!urlField || !bodyField || !headersField) {
        showNotification('❌ Tamper fields not found', 'error');
        return;
    }
    
    let payload = '';
    let paramName = '';
    
    switch(type) {
        case 'xss':
            payload = '<script>alert("XSS-Test-Vulna")</script>';
            paramName = 'xss_test';
            break;
        case 'sql':
            payload = "' OR '1'='1' UNION SELECT null,user(),version() --";
            paramName = 'sql_test';
            break;
        case 'lfi':
            payload = '../../../etc/passwd';
            paramName = 'file_test';
            break;
        default:
            return;
    }
    
    // Add to URL
    const url = urlField.value;
    if (url.includes('?')) {
        urlField.value = url + `&${paramName}=${encodeURIComponent(payload)}`;
    } else {
        urlField.value = url + `?${paramName}=${encodeURIComponent(payload)}`;
    }
    
    // Add to body if exists
    const body = bodyField.value.trim();
    if (body) {
        try {
            const jsonBody = JSON.parse(body);
            jsonBody[paramName] = payload;
            bodyField.value = JSON.stringify(jsonBody, null, 2);
        } catch (e) {
            if (body.includes('=')) {
                bodyField.value = body + `&${paramName}=${encodeURIComponent(payload)}`;
            } else {
                bodyField.value = body + `\n${paramName}=${payload}`;
            }
        }
    }
    
    showNotification(`✅ ${type.toUpperCase()} payload added`, 'success');
}

function generateCurlCommand() {
    const method = document.getElementById('tamperMethod')?.value || 'GET';
    const url = document.getElementById('tamperUrl')?.value || '';
    const headers = document.getElementById('tamperHeaders')?.value || '{}';
    const body = document.getElementById('tamperBody')?.value || '';
    
    let curlCommand = `curl -X ${method}`;
    
    try {
        const headersObj = JSON.parse(headers);
        for (let [key, value] of Object.entries(headersObj)) {
            curlCommand += ` \\\n  -H "${key}: ${value}"`;
        }
    } catch (e) {
        console.error('Invalid headers JSON:', e);
    }
    
    if (body && body.trim() !== '') {
        curlCommand += ` \\\n  -d '${body}'`;
    }
    
    curlCommand += ` \\\n  "${url}"`;
    
    navigator.clipboard.writeText(curlCommand).then(() => {
        showNotification('📋 cURL command copied to clipboard!', 'success');
    });
}

function generateBurpRequest() {
    const method = document.getElementById('tamperMethod')?.value || 'GET';
    const url = document.getElementById('tamperUrl')?.value || '';
    const headers = document.getElementById('tamperHeaders')?.value || '{}';
    const body = document.getElementById('tamperBody')?.value || '';
    
    try {
        const urlObj = new URL(url);
        let burpRequest = `${method} ${urlObj.pathname}${urlObj.search} HTTP/1.1\n`;
        burpRequest += `Host: ${urlObj.host}\n`;
        
        const headersObj = JSON.parse(headers);
        for (let [key, value] of Object.entries(headersObj)) {
            if (key.toLowerCase() !== 'host') {
                burpRequest += `${key}: ${value}\n`;
            }
        }
        
        if (body && body.trim() !== '') {
            burpRequest += `Content-Length: ${body.length}\n`;
            burpRequest += `\n${body}`;
        } else {
            burpRequest += `\n`;
        }
        
        navigator.clipboard.writeText(burpRequest).then(() => {
            showNotification('🔥 Burp request copied to clipboard!', 'success');
        });
    } catch (e) {
        showNotification('❌ Error generating Burp request', 'error');
    }
}

function testTamperedRequest() {
    const method = document.getElementById('tamperMethod')?.value || 'GET';
    const url = document.getElementById('tamperUrl')?.value || '';
    const headers = document.getElementById('tamperHeaders')?.value || '{}';
    const body = document.getElementById('tamperBody')?.value || '';
    
    showNotification('🚀 Testing tampered request...', 'success');
    
    try {
        const headersObj = JSON.parse(headers);
        
        fetch('/api/test-request', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                method: method,
                url: url,
                headers: headersObj,
                body: body
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(`✅ Request successful! Status: ${data.status_code}, Time: ${data.response_time}ms`, 'success');
            } else {
                showNotification(`❌ Request failed: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            showNotification(`❌ Network error: ${error.message}`, 'error');
        });
    } catch (e) {
        showNotification('❌ Invalid headers JSON', 'error');
    }
}

function saveRequestTemplate() {
    const method = document.getElementById('tamperMethod')?.value || 'GET';
    const url = document.getElementById('tamperUrl')?.value || '';
    const headers = document.getElementById('tamperHeaders')?.value || '{}';
    const body = document.getElementById('tamperBody')?.value || '';
    
    try {
        const template = {
            name: `Template_${new Date().toISOString().slice(0,19).replace(/[:.]/g, '-')}`,
            method: method,
            url: url,
            headers: JSON.parse(headers),
            body: body,
            created: new Date().toISOString()
        };
        
        // Save to localStorage
        const templates = JSON.parse(localStorage.getItem('vulna_templates') || '[]');
        templates.push(template);
        localStorage.setItem('vulna_templates', JSON.stringify(templates));
        
        showNotification('💾 Request template saved!', 'success');
    } catch (e) {
        showNotification('❌ Error saving template', 'error');
    }
}

// Vulnerability to Inspector Integration
function sendVulnToInspector(vulnId) {
    const vulnerability = allFindings.find(f => f.id === vulnId);
    if (!vulnerability) {
        showNotification('❌ Vulnerability not found', 'error');
        return;
    }
    
    const request = {
        method: vulnerability.request_method || 'GET',
        url: vulnerability.affected_url || vulnerability.url || '',
        headers: vulnerability.request_headers || {},
        body: vulnerability.request_body || '',
        timestamp: vulnerability.timestamp || new Date().toISOString()
    };
    
    sendToInspector(request);
    showNotification('🔍 Vulnerability request sent to inspector', 'success');
}

function createTestRequest(vulnId) {
    const vulnerability = allFindings.find(f => f.id === vulnId);
    if (!vulnerability) {
        showNotification('❌ Vulnerability not found', 'error');
        return;
    }
    
    const testRequest = {
        method: 'POST',
        url: vulnerability.affected_url || vulnerability.url || '',
        headers: {
            'Content-Type': 'application/json',
            'User-Agent': 'Vulna-Tester/1.0'
        },
        body: JSON.stringify({
            test_param: 'vulnerability_test',
            vuln_id: vulnerability.id,
            payload: 'test_payload_here'
        }, null, 2),
        timestamp: new Date().toISOString()
    };
    
    sendToInspector(testRequest);
    showNotification('📝 Test request created and sent to inspector', 'success');
}

// Export for global access
window.VulnaInspector = {
    sendToInspector,
    sendVulnToInspector,
    createTestRequest,
    addPayload,
    generateCurlCommand,
    generateBurpRequest,
    testTamperedRequest
};
