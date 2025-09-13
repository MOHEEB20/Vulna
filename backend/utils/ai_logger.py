"""
AI Activity Logger for Vulna - Real-time logging of AI testing activities
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional

class AIActivityLogger:
    def __init__(self):
        self.active_sessions: Dict[str, List] = {}
        self.log_history: List[Dict] = []
        
    async def add_websocket_session(self, vuln_id: str, websocket):
        if vuln_id not in self.active_sessions:
            self.active_sessions[vuln_id] = []
        self.active_sessions[vuln_id].append(websocket)
        
    def remove_websocket_session(self, vuln_id: str, websocket):
        if vuln_id in self.active_sessions and websocket in self.active_sessions[vuln_id]:
            self.active_sessions[vuln_id].remove(websocket)
            if not self.active_sessions[vuln_id]:
                del self.active_sessions[vuln_id]
    
    async def log_activity(self, vuln_id: str, activity_type: str, message: str, 
                         details: Optional[Dict] = None, level: str = "INFO"):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "vuln_id": vuln_id,
            "activity_type": activity_type,
            "message": message,
            "details": details or {},
            "level": level
        }
        
        self.log_history.append(log_entry)
        if len(self.log_history) > 1000:
            self.log_history = self.log_history[-1000:]
        
        # Broadcast to WebSocket sessions
        if vuln_id in self.active_sessions:
            websocket_message = {
                "type": "log",
                "message": f"{self._get_activity_icon(activity_type)} {message}",
                "timestamp": log_entry["timestamp"],
                "activity_type": activity_type,
                "level": level
            }
            
            disconnected_sessions = []
            for websocket in self.active_sessions[vuln_id]:
                try:
                    await websocket.send_text(json.dumps(websocket_message))
                except Exception:
                    disconnected_sessions.append(websocket)
            
            for ws in disconnected_sessions:
                self.remove_websocket_session(vuln_id, ws)
    
    def _get_activity_icon(self, activity_type: str) -> str:
        icons = {
            "session_start": "🟢", "ai_analysis": "🤖", "poc_generation": "🔬",
            "payload_injection": "💉", "request_sent": "🚀", "response_received": "📥",
            "vulnerability_confirmed": "✅", "false_positive": "❌", "error": "🚨",
            "auto_test": "⚡", "burp_export": "🔄", "curl_export": "📋"
        }
        return icons.get(activity_type, "📊")
    
    async def log_ai_analysis_start(self, vuln_id: str, analysis_type: str):
        await self.log_activity(vuln_id=vuln_id, activity_type="ai_analysis", 
                              message=f"AI Model starting {analysis_type} analysis...",
                              details={"analysis_type": analysis_type})
    
    async def log_poc_generation(self, vuln_id: str, success: bool, details: Dict):
        if success:
            await self.log_activity(vuln_id=vuln_id, activity_type="poc_generation",
                                  message="PoC generated successfully", details=details)
        else:
            await self.log_activity(vuln_id=vuln_id, activity_type="error",
                                  message="PoC generation failed", details=details, level="ERROR")
    
    async def log_request_inspection(self, vuln_id: str, method: str, url: str, modified: bool):
        action = "modified" if modified else "original"
        await self.log_activity(vuln_id=vuln_id, activity_type="request_sent",
                              message=f"Request Inspector: {action} {method} request to {url}",
                              details={"method": method, "url": url, "modified": modified})

ai_logger = AIActivityLogger()
