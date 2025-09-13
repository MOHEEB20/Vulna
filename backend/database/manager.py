"""
Database Manager for Vulna - SQLite Database for persistent storage
"""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

class VulnaDatabase:
    def __init__(self, db_path: str = "data/vulna.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()
        
    def init_database(self):
        """Initialize database with all required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vulnerabilities (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    risk_level TEXT,
                    risk_score REAL,
                    confidence REAL,
                    url TEXT,
                    affected_url TEXT,
                    request_method TEXT,
                    request_headers TEXT,
                    request_body TEXT,
                    response_headers TEXT,
                    response_body TEXT,
                    owasp_categories TEXT,
                    cwe_ids TEXT,
                    affected_parameters TEXT,
                    suggestion TEXT,
                    poc_code TEXT,
                    exploitation_analysis TEXT,
                    auto_test_results TEXT,
                    ai_chat_history TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'new'
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ai_sessions (
                    id TEXT PRIMARY KEY,
                    vulnerability_id TEXT,
                    session_type TEXT,
                    messages TEXT,
                    context TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vulnerability_id) REFERENCES vulnerabilities(id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS request_templates (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    method TEXT,
                    url TEXT,
                    headers TEXT,
                    body TEXT,
                    payload_type TEXT,
                    description TEXT,
                    vulnerability_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vulnerability_id) REFERENCES vulnerabilities(id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS testing_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vulnerability_id TEXT,
                    log_type TEXT,
                    message TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vulnerability_id) REFERENCES vulnerabilities(id)
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_vuln_status ON vulnerabilities(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_vuln_risk ON vulnerabilities(risk_level)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_logs_vuln ON testing_logs(vulnerability_id)")
            
    def save_vulnerability(self, vuln_data: Dict) -> str:
        """Save or update vulnerability"""
        vuln_id = vuln_data.get('id', str(uuid.uuid4()))
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO vulnerabilities 
                (id, title, description, risk_level, risk_score, confidence, url, affected_url, 
                 request_method, request_headers, request_body, response_headers, response_body,
                 owasp_categories, cwe_ids, affected_parameters, suggestion, poc_code,
                 exploitation_analysis, auto_test_results, ai_chat_history, updated_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                vuln_id,
                vuln_data.get('title'),
                vuln_data.get('description'),
                vuln_data.get('risk_level'),
                vuln_data.get('risk_score'),
                vuln_data.get('confidence'),
                vuln_data.get('url'),
                vuln_data.get('affected_url'),
                vuln_data.get('request_method'),
                json.dumps(vuln_data.get('request_headers', {})),
                vuln_data.get('request_body'),
                json.dumps(vuln_data.get('response_headers', {})),
                vuln_data.get('response_body'),
                json.dumps(vuln_data.get('owasp_categories', [])),
                json.dumps(vuln_data.get('cwe_ids', [])),
                json.dumps(vuln_data.get('affected_parameters', [])),
                vuln_data.get('suggestion'),
                vuln_data.get('poc_code'),
                vuln_data.get('exploitation_analysis'),
                vuln_data.get('auto_test_results'),
                json.dumps(vuln_data.get('ai_chat_history', [])),
                datetime.now().isoformat(),
                vuln_data.get('status', 'new')
            ))
        return vuln_id
    
    def get_vulnerability(self, vuln_id: str) -> Optional[Dict]:
        """Get vulnerability by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM vulnerabilities WHERE id = ?", (vuln_id,))
            row = cursor.fetchone()
            
            if row:
                vuln = dict(row)
                # Parse JSON fields
                vuln['request_headers'] = json.loads(vuln['request_headers'] or '{}')
                vuln['response_headers'] = json.loads(vuln['response_headers'] or '{}')
                vuln['owasp_categories'] = json.loads(vuln['owasp_categories'] or '[]')
                vuln['cwe_ids'] = json.loads(vuln['cwe_ids'] or '[]')
                vuln['affected_parameters'] = json.loads(vuln['affected_parameters'] or '[]')
                vuln['ai_chat_history'] = json.loads(vuln['ai_chat_history'] or '[]')
                return vuln
        return None
    
    def get_all_vulnerabilities(self, status: Optional[str] = None) -> List[Dict]:
        """Get all vulnerabilities, optionally filtered by status"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if status:
                cursor = conn.execute("SELECT * FROM vulnerabilities WHERE status = ? ORDER BY created_at DESC", (status,))
            else:
                cursor = conn.execute("SELECT * FROM vulnerabilities ORDER BY created_at DESC")
            
            vulnerabilities = []
            for row in cursor.fetchall():
                vuln = dict(row)
                # Parse JSON fields
                vuln['request_headers'] = json.loads(vuln['request_headers'] or '{}')
                vuln['response_headers'] = json.loads(vuln['response_headers'] or '{}')
                vuln['owasp_categories'] = json.loads(vuln['owasp_categories'] or '[]')
                vuln['cwe_ids'] = json.loads(vuln['cwe_ids'] or '[]')
                vuln['affected_parameters'] = json.loads(vuln['affected_parameters'] or '[]')
                vuln['ai_chat_history'] = json.loads(vuln['ai_chat_history'] or '[]')
                vulnerabilities.append(vuln)
            return vulnerabilities
    
    def update_vulnerability_field(self, vuln_id: str, field: str, value: Any):
        """Update specific field of vulnerability"""
        if field in ['request_headers', 'response_headers', 'owasp_categories', 'cwe_ids', 'affected_parameters', 'ai_chat_history']:
            value = json.dumps(value)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f"UPDATE vulnerabilities SET {field} = ?, updated_at = ? WHERE id = ?", 
                        (value, datetime.now().isoformat(), vuln_id))
    
    def add_chat_message(self, vuln_id: str, message: Dict):
        """Add message to AI chat history"""
        vuln = self.get_vulnerability(vuln_id)
        if vuln:
            chat_history = vuln.get('ai_chat_history', [])
            chat_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': message.get('type', 'user'),
                'content': message.get('content', ''),
                'metadata': message.get('metadata', {})
            })
            self.update_vulnerability_field(vuln_id, 'ai_chat_history', chat_history)

# Global database instance
db = VulnaDatabase()
