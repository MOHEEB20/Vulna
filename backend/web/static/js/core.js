// Vulna Dashboard - Core Functions with Complete WebSocket Integration

// Global Variables
let ws = null;
let reconnectInterval = null;
let allRequests = [];
let allFindings = [];
let stats = {};

// WebSocket Connection with Full Message Handling
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = function() {
        console.log('WebSocket connected');
        updateConnectionStatus(true);
        if (reconnectInterval) {
            clearInterval(reconnectInterval);
            reconnectInterval = null;
        }
    };
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    ws.onclose = function() {
        console.log('WebSocket disconnected');
        updateConnectionStatus(false);
        
        // Auto-reconnect
        if (!reconnectInterval) {
            reconnectInterval = setInterval(connectWebSocket, 3000);
        }
    };
    
    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
        updateConnectionStatus(false);
    };
}

function handleWebSocketMessage(data) {
    switch(data.type) {
        case 'initial_load':
            allRequests = data.requests || [];
            allFindings = data.findings || [];
            stats = data.stats || {};
            updateDisplay();
            break;
            
        case 'new_requests':
            allRequests.push(...(data.requests || []));
            stats = data.stats || stats;
            updateDisplay();
            break;
            
        case 'new_findings':
            allFindings.push(...(data.findings || []));
            stats = data.stats || stats;
            updateDisplay();
            break;
            
        case 'browser_started':
            showNotification(data.message || 'Browser started successfully', 'success');
            break;
            
        case 'data_cleared':
            allRequests = [];
            allFindings = [];
            stats = {};
            updateDisplay();
            showNotification(data.message || 'Data cleared', 'success');
            break;
    }
}

function updateConnectionStatus(connected) {
    const indicator = document.getElementById('connectionIndicator');
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    
    if (connected) {
        indicator.classList.add('connected');
        statusIndicator.classList.remove('disconnected');
        statusIndicator.classList.add('connected');
        statusText.textContent = 'Connected';
    } else {
        indicator.classList.remove('connected');
        statusIndicator.classList.remove('connected');
        statusIndicator.classList.add('disconnected');
        statusText.textContent = 'Disconnected';
    }
}

function updateDisplay() {
    updateStats();
    updateRequests();
    updateFindings();
}

// Initialize Dashboard
function initializeDashboard() {
    connectWebSocket();
    loadInitialData();
    setupEventListeners();
    startAutoRefresh();
}

// Load Initial Data
function loadInitialData() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            stats = data;
            updateStats();
        })
        .catch(error => console.log('Failed to load stats:', error));
        
    fetch('/api/requests')
        .then(response => response.json())
        .then(data => {
            allRequests = data.slice(-100);
            updateRequests();
        })
        .catch(error => console.log('Failed to load requests:', error));
        
    fetch('/api/findings')
        .then(response => response.json())
        .then(data => {
            allFindings = data.slice(-50);
            updateFindings();
        })
        .catch(error => console.log('Failed to load findings:', error));
}

function setupEventListeners() {
    // Setup keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Escape to close modals
        if (e.key === 'Escape') {
            closeModal();
        }
        
        // Ctrl+R to refresh data
        if (e.ctrlKey && e.key === 'r') {
            e.preventDefault();
            refreshData();
        }
    });
}

function startAutoRefresh() {
    // Auto refresh stats every 30 seconds
    setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
        }
    }, 30000);
    
    // Periodic data refresh
    setInterval(() => {
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                stats = data;
                updateStats();
            })
            .catch(error => console.log('Auto refresh failed:', error));
    }, 30000);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', initializeDashboard);
