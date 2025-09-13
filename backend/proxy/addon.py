"""mitmproxy addon for intercepting HTTP/HTTPS traffic."""

import hashlib, json, sys, os
from datetime import datetime
from mitmproxy import http

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.models.findings import HttpRequest, HttpMethod


class VulnaProxyAddon:
    def __init__(self):
        self.max_body_size = 1024
        self.processed_hashes = set()
        self.findings_file = "data/requests.jsonl"
        os.makedirs("data", exist_ok=True)
        print("Vulna Proxy Addon loaded")
        
    def request(self, flow: http.HTTPFlow) -> None:
        try:
            request = self._create_request_model(flow.request)
            request_hash = self._generate_hash(request)
            
            if request_hash in self.processed_hashes:
                return
                
            self.processed_hashes.add(request_hash)
            print(f"Traffic: {request.method} {request.url}")
            self._save_request(request)
                
        except Exception as e:
            print(f"Error: {e}")
    
    def _create_request_model(self, request: http.HTTPRequest) -> HttpRequest:
        headers = dict(request.headers)
        
        body = None
        if request.content:
            body_text = request.get_text()
            if body_text and len(body_text) > self.max_body_size:
                body = body_text[:self.max_body_size] + "... [truncated]"
            else:
                body = body_text
        
        return HttpRequest(
            method=HttpMethod(request.method),
            url=request.pretty_url,
            headers=headers,
            body=body,
            timestamp=datetime.now()
        )
        
    def _generate_hash(self, request: HttpRequest) -> str:
        """Generate hash for duplicate detection."""
        hash_content = f"{request.method}|{request.url}|{request.body or ''}"
        return hashlib.sha256(hash_content.encode()).hexdigest()[:16]
        
    def _save_request(self, request: HttpRequest):
        """Save request to file."""
        try:
            with open(self.findings_file, "a", encoding="utf-8") as f:
                request_data = {
                    "timestamp": request.timestamp.isoformat(),
                    "method": request.method.value,
                    "url": request.url,
                    "headers": request.headers,
                    "body": request.body
                }
                f.write(json.dumps(request_data) + "\n")
        except Exception as e:
            print(f"Error saving: {e}")


# Global addon instance
addons = [VulnaProxyAddon()]
