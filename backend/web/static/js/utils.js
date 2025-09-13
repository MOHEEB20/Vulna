// Vulna Dashboard - Enhanced Utility Functions

function showNotification(message, type = 'info') {
    // Try to use existing notification element first
    let notification = document.getElementById('notification');
    
    if (!notification) {
        // Create notification element if it doesn't exist
        notification = document.createElement('div');
        notification.id = 'notification';
        notification.className = 'notification';
        document.body.appendChild(notification);
    }
    
    // Set notification content and style
    notification.textContent = message;
    notification.className = `notification ${type}`;
    
    // Add show class for animation
    notification.classList.add('show');
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
    }, 5000);
    
    // Click to dismiss
    notification.onclick = () => {
        notification.classList.remove('show');
    };
}

function formatTimestamp(timestamp) {
    try {
        return new Date(timestamp).toLocaleString();
    } catch (error) {
        return 'Invalid Date';
    }
}

function formatTimeAgo(timestamp) {
    try {
        const now = new Date();
        const time = new Date(timestamp);
        const diffMs = now - time;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        return `${diffDays}d ago`;
    } catch (error) {
        return 'Unknown';
    }
}

function sanitizeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('📋 Copied to clipboard', 'success');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showNotification('📋 Copied to clipboard', 'success');
    } catch (err) {
        showNotification('❌ Failed to copy to clipboard', 'error');
    }
    
    document.body.removeChild(textArea);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

function isValidURL(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

function getDomainFromURL(url) {
    try {
        return new URL(url).hostname;
    } catch (_) {
        return 'unknown';
    }
}

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function highlightText(text, searchTerm) {
    if (!searchTerm) return text;
    
    const escapedTerm = escapeRegExp(searchTerm);
    const regex = new RegExp(`(${escapedTerm})`, 'gi');
    
    return text.replace(regex, '<mark>$1</mark>');
}

function getRandomId() {
    return Math.random().toString(36).substr(2, 9);
}

function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

// Enhanced keyboard shortcuts
function setupKeyboardShortcuts() {
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
        
        // Ctrl+E to export findings
        if (e.ctrlKey && e.key === 'e') {
            e.preventDefault();
            exportFindings();
        }
        
        // Ctrl+Shift+E to export requests
        if (e.ctrlKey && e.shiftKey && e.key === 'E') {
            e.preventDefault();
            exportRequests();
        }
        
        // F5 alternative for refresh
        if (e.key === 'F5') {
            e.preventDefault();
            refreshData();
        }
    });
}

// Setup when page loads
document.addEventListener('DOMContentLoaded', function() {
    setupKeyboardShortcuts();
});

// Error handling utilities
function handleFetchError(response) {
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response;
}

function logError(error, context = '') {
    console.error(`[Vulna Error${context ? ' - ' + context : ''}]:`, error);
    showNotification(`❌ Error${context ? ' (' + context + ')' : ''}: ${error.message}`, 'error');
}

// Performance monitoring
function measurePerformance(name, func) {
    const start = performance.now();
    const result = func();
    const end = performance.now();
    console.log(`[Performance] ${name}: ${(end - start).toFixed(2)}ms`);
    return result;
}

// Connection status utilities
function checkOnlineStatus() {
    return navigator.onLine;
}

window.addEventListener('online', () => {
    showNotification('🌐 Connection restored', 'success');
    if (ws && ws.readyState !== WebSocket.OPEN) {
        connectWebSocket();
    }
});

window.addEventListener('offline', () => {
    showNotification('📡 Connection lost', 'error');
});
