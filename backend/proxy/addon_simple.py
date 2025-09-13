"""Enhanced mitmproxy addon with intelligent traffic filtering for pentesting."""

import hashlib
import json
import os
import sys
from datetime import datetime
from mitmproxy import http

# Add parent directory to path so we can import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.utils.url_filter import should_analyze_url, get_analysis_priority


class VulnaProxyAddon:
    def __init__(self):
        self.max_body_size = 1024
        self.processed_hashes = set()
        self.findings_file = "data/requests.jsonl"
        self.filtered_count = 0
        self.processed_count = 0
        os.makedirs("data", exist_ok=True)
        print("Vulna Proxy Addon loaded with intelligent filtering")
        
    def request(self, flow: http.HTTPFlow) -> None:
        try:
            # Quick pre-filter check
            if not should_analyze_url(flow.request.pretty_url, flow.request.method):
                self.filtered_count += 1
                if self.filtered_count % 10 == 0:  # Log every 10th filtered request
                    print(f"Filtered {self.filtered_count} requests (CDN/static content)")
                return
            
            request_data = self._create_request_dict(flow.request)
            request_hash = self._generate_hash(request_data)
            
            if request_hash in self.processed_hashes:
                return
                
            self.processed_hashes.add(request_hash)
            
            # Get priority for logging
            priority = get_analysis_priority(request_data['url'], request_data['method'])
            priority_label = "" if priority >= 8 else "" if priority >= 5 else ""
            
            print(f"{priority_label} Traffic (P{priority}): {request_data['method']} {request_data['url']}")
            self._save_request(request_data)
            self.processed_count += 1
                
        except Exception as e:
            print(f"Proxy Error: {e}")
    
    def _create_request_dict(self, request):
        """Create enhanced request dictionary with priority information."""
        headers = dict(request.headers)
        
        body = None
        if request.content:
            body_text = request.get_text()
            if body_text and len(body_text) > self.max_body_size:
                body = body_text[:self.max_body_size] + "... [truncated]"
            else:
                body = body_text
        
        # Add priority and analysis hints
        priority = get_analysis_priority(request.pretty_url, request.method)
        
        return {
            "method": request.method,
            "url": request.pretty_url,
            "headers": headers,
            "body": body,
            "timestamp": datetime.now().isoformat(),
            "priority": priority,
            "analysis_hint": "high_priority" if priority >= 8 else "standard" if priority >= 5 else "low_priority"
        }
        
    def _generate_hash(self, request_data):
        """Generate hash for duplicate detection."""
        hash_content = f"{request_data['method']}|{request_data['url']}|{request_data.get('body', '') or ''}"
        return hashlib.sha256(hash_content.encode()).hexdigest()[:16]
        
    def _save_request(self, request_data):
        """Save filtered request to file."""
        try:
            with open(self.findings_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(request_data) + "\n")
        except Exception as e:
            print(f"Error saving request: {e}")
    
    def get_stats(self):
        """Get proxy statistics"""
        return {
            "processed_count": self.processed_count,
            "filtered_count": self.filtered_count,
            "total_requests": self.processed_count + self.filtered_count
        }


# Global addon instance
addons = [VulnaProxyAddon()]
