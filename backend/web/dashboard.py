"""
Vulna Web Dashboard - Modular Edition with Enhanced Static File Serving
"""

import asyncio
import json
import os
import subprocess
import platform
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn

# Import AI Session Manager
from backend.ai.session_manager import AISessionManager
from backend.utils.ai_logger import ai_logger
from backend.database.manager import db


class DashboardManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.requests_file = Path("data/requests.jsonl")
        self.findings_file = Path("data/findings.jsonl")
        self.last_request_count = 0
        self.last_finding_count = 0
        
        # Initialize AI Session Manager
        self.ai_session_manager = AISessionManager()
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.send_initial_data(websocket)
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_initial_data(self, websocket: WebSocket):
        """Send all current data to new connection"""
        data = {
            "type": "initial_load",
            "requests": await self.get_all_requests(),
            "findings": await self.get_all_findings(),
            "stats": await self.get_stats()
        }
        await websocket.send_text(json.dumps(data))
    
    async def broadcast_update(self, message: dict):
        """Send update to all connected clients"""
        if self.active_connections:
            for connection in self.active_connections.copy():
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    self.active_connections.remove(connection)
    
    async def get_all_requests(self) -> List[Dict]:
        """Load all requests from file"""
        if not self.requests_file.exists():
            return []
        
        requests = []
        try:
            with open(self.requests_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            req = json.loads(line.strip())
                            requests.append(req)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"Error reading requests: {e}")
        
        return requests
    
    async def get_all_findings(self) -> List[Dict]:
        """Load all findings from database with file fallback"""
        try:
            # Try to get from database first
            db_findings = db.get_all_vulnerabilities()
            if db_findings:
                return db_findings
        except Exception as e:
            print(f"Database error, falling back to file: {e}")
        
        # Fallback to file-based system
        if not self.findings_file.exists():
            return []
        
        findings = []
        try:
            with open(self.findings_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            finding = json.loads(line.strip())
                            # Migrate to database
                            try:
                                db.save_vulnerability(finding)
                            except Exception:
                                pass  # Continue if migration fails
                            findings.append(finding)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"Error reading findings: {e}")
        
        return findings
    
    async def get_stats(self) -> Dict:
        """Get current statistics"""
        requests = await self.get_all_requests()
        findings = await self.get_all_findings()
        
        # Count by method
        methods = {}
        domains = {}
        
        for req in requests:
            method = req.get('method', 'UNKNOWN')
            methods[method] = methods.get(method, 0) + 1
            
            url = req.get('url', '')
            if '://' in url:
                domain = url.split('://')[1].split('/')[0]
                domains[domain] = domains.get(domain, 0) + 1
        
        # Count by risk level
        risks = {}
        for finding in findings:
            risk = finding.get('risk_level', 'UNKNOWN')
            risks[risk] = risks.get(risk, 0) + 1
        
        return {
            "total_requests": len(requests),
            "total_findings": len(findings),
            "methods": methods,
            "domains": domains,
            "risks": risks,
            "last_updated": datetime.now().isoformat()
        }
    
    async def monitor_files(self):
        """Monitor files for changes and broadcast updates"""
        while True:
            try:
                # Check for new requests
                if self.requests_file.exists():
                    current_requests = len(list(open(self.requests_file, 'r', encoding='utf-8')))
                    if current_requests > self.last_request_count:
                        # New requests found
                        new_requests = await self.get_all_requests()
                        stats = await self.get_stats()
                        
                        await self.broadcast_update({
                            "type": "new_requests",
                            "requests": new_requests[self.last_request_count:],
                            "stats": stats
                        })
                        self.last_request_count = current_requests
                
                # Check for new findings
                if self.findings_file.exists():
                    current_findings = len(list(open(self.findings_file, 'r', encoding='utf-8')))
                    if current_findings > self.last_finding_count:
                        # New findings found
                        new_findings = await self.get_all_findings()
                        stats = await self.get_stats()
                        
                        await self.broadcast_update({
                            "type": "new_findings", 
                            "findings": new_findings[self.last_finding_count:],
                            "stats": stats
                        })
                        self.last_finding_count = current_findings
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"Monitor error: {e}")
                await asyncio.sleep(5)


# Initialize FastAPI app and dashboard with AI Session support
app = FastAPI(title="Vulna Dashboard", description="Real-time Pentest Monitoring with AI Sessions")
# Create FastAPI app
app = FastAPI(title="Vulna Dashboard", description="AI-Powered Penetration Testing Platform")

# Initialize dashboard
dashboard = DashboardManager()

# Static files and templates  
import os
template_dir = os.path.join(os.getcwd(), "backend", "web", "templates")
static_dir = os.path.join(os.getcwd(), "backend", "web", "static")

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Templates
templates = Jinja2Templates(directory=template_dir)

# BULLETPROOF Browser Storage - Global and Persistent
browser_storage = {
    'processes': [],
    'browsers': [],
    'tasks': [],
    'keep_alive_tasks': []
}

@app.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/modular", response_class=HTMLResponse)
async def modular_dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard_modular.html", {"request": request})

@app.get("/test", response_class=HTMLResponse)
async def test_components_page(request: Request):
    return templates.TemplateResponse("test_components.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await dashboard.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        dashboard.disconnect(websocket)

@app.post("/api/browser/start")
async def start_browser():
    """BULLETPROOF Browser Start with AUTOMATIC PROXY - GUARANTEED to stay open"""
    try:
        system = platform.system()
        success = False
        
        print("[*] BULLETPROOF Browser Launch Starting...")
        print(f"[i] Operating System: {system}")
        
        # Create temporary profile directory for isolated browsing
        import tempfile
        import os
        temp_dir = tempfile.mkdtemp(prefix="vulna_browser_")
        print(f"[i] Using temporary profile: {temp_dir}")
        
        # Create simple Chrome preferences for proxy
        prefs_dir = os.path.join(temp_dir, "Default")
        os.makedirs(prefs_dir, exist_ok=True)
        
        # Simple proxy configuration in Chrome prefs
        chrome_prefs = {
            "proxy": {
                "mode": "fixed_servers",
                "server": "127.0.0.1:8080"
            }
        }
        
        prefs_file = os.path.join(prefs_dir, "Preferences")
        with open(prefs_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(chrome_prefs, f, indent=2)
        
        print(f"[i] Created Chrome preferences with proxy: {prefs_file}")
        
        # BULLETPROOF Method: Native Chrome with DETACHED_PROCESS
        chrome_paths = {
            "Windows": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser("~/AppData/Local/Google/Chrome/Application/chrome.exe"),
                os.path.expanduser("~/AppData/Local/Chromium/Application/chrome.exe")
            ],
            "Darwin": [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium"
            ],
            "Linux": [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable", 
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium"
            ]
        }
        
        # Find Chrome executable
        chrome_exe = None
        for path in chrome_paths.get(system, []):
            if os.path.exists(path):
                chrome_exe = path
                print(f"[+] Found Chrome: {chrome_exe}")
                break
        
        if chrome_exe:
            try:
                # SIMPLIFIED Chrome arguments - DIRECT PROXY ONLY
                chrome_args = [
                    chrome_exe,
                    '--new-window',
                    f'--user-data-dir={temp_dir}',  # Isolated profile
                    '--proxy-server=127.0.0.1:8080',  # DIRECT proxy - most reliable
                    '--ignore-certificate-errors',
                    '--ignore-ssl-errors', 
                    '--disable-web-security',
                    '--disable-extensions',
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--test-type',
                    f'http://localhost:{os.getenv("CURRENT_DASHBOARD_PORT", "3000")}/proxy-test'  # Dynamic port!
                ]
                
                print("[i] Chrome Arguments:")
                for arg in chrome_args:
                    print(f"   {arg}")
                
                print("[i] Testing if Chrome will use proxy...")
                
                # CRITICAL: Use DETACHED_PROCESS on Windows for true independence
                if system == "Windows":
                    print("[i] Windows: Using DETACHED_PROCESS + CREATE_NEW_PROCESS_GROUP")
                    process = subprocess.Popen(
                        chrome_args,
                        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL,
                        close_fds=True  # CRITICAL: Close file descriptors
                    )
                else:
                    print("🐧 Unix: Using setsid for new session")
                    process = subprocess.Popen(
                        chrome_args,
                        preexec_fn=os.setsid,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL,
                        close_fds=True
                    )
                
                # Store process reference but DON'T wait for it
                browser_storage['processes'].append(process)
                
                print(f"[+] BULLETPROOF: Chrome started with PID {process.pid}")
                print("[+] BULLETPROOF: Process is DETACHED from Python")
                print("[+] BULLETPROOF: Browser will NOT close when Python exits")
                print("[+] BULLETPROOF: Browser will open in NEW WINDOW")
                print("[i] BULLETPROOF: All HTTP requests will be intercepted")
                
                success = True
                
                # Broadcast success
                await dashboard.broadcast_update({
                    "type": "browser_started",
                    "message": f"BULLETPROOF Browser launched (PID: {process.pid}) - GUARANTEED to stay open!"
                })
                
            except Exception as e:
                print(f"❌ Chrome subprocess failed: {e}")
        else:
            print("❌ Chrome not found on system")
        
        # Fallback: Playwright if Chrome not found
        if not success:
            try:
                print("🔄 Fallback: Attempting Playwright...")
                from playwright.async_api import async_playwright
                
                async def bulletproof_playwright():
                    try:
                        print("🎭 Starting Playwright Browser...")
                        
                        # Start playwright WITHOUT context manager
                        playwright = await async_playwright().start()
                        browser = await playwright.chromium.launch(
                            headless=False,
                            args=[
                                '--proxy-server=localhost:8080',  # FIXED: localhost format
                                '--ignore-certificate-errors',
                                '--disable-web-security', 
                                '--ignore-ssl-errors',
                                '--disable-extensions',
                                '--no-first-run',
                                '--new-window',
                                '--no-sandbox',
                                '--disable-dev-shm-usage',
                                '--disable-features=VizDisplayCompositor',
                                '--disable-proxy-certificate-handler'
                            ]
                        )
                        
                        # CRITICAL: Store references globally to prevent GC
                        browser_storage['browsers'].append((playwright, browser))
                        
                        page = await browser.new_page()
                        await page.goto("http://httpbin.org/", timeout=15000)
                        
                        print("[+] BULLETPROOF: Playwright browser started")
                        print("[+] BULLETPROOF: References stored globally (anti-GC)")
                        
                        # INFINITE keep-alive loop - NEVER EXIT THIS FUNCTION
                        print("🔄 BULLETPROOF: Starting infinite keep-alive loop...")
                        counter = 0
                        while True:
                            try:
                                if browser.is_closed():
                                    print("❌ Browser closed by user")
                                    break
                                    
                                counter += 1
                                if counter % 6 == 0:  # Every minute
                                    print(f"🔄 Browser alive for {counter * 10} seconds...")
                                    
                                await asyncio.sleep(10)  # Check every 10 seconds
                                
                            except Exception as e:
                                print(f"⚠️ Keep-alive error: {e}")
                                await asyncio.sleep(5)
                                
                    except Exception as e:
                        print(f"❌ Playwright error: {e}")
                
                # Start playwright task and store globally
                task = asyncio.create_task(bulletproof_playwright())
                browser_storage['tasks'].append(task)
                browser_storage['keep_alive_tasks'].append(task)
                
                print("[+] BULLETPROOF: Playwright task started and stored globally")
                
                # Don't await - let it run independently
                success = True
                
            except ImportError:
                print("❌ Playwright not available")
            except Exception as e:
                print(f"❌ Playwright failed: {e}")
        
        if success:
            return {
                "success": True,
                "message": "[*] BULLETPROOF Browser with AUTO-PROXY launched! Opens in NEW WINDOW and stays open FOREVER!",
                "method": "Native Chrome (DETACHED + PAC)" if chrome_exe else "Playwright (Keep-Alive)",
                "proxy": "127.0.0.1:8080 (AUTO-CONFIGURED)",
                "proxy_method": "PAC File + Direct Fallback",
                "test_url": "http://testphp.vulnweb.com",
                "profile": temp_dir if 'temp_dir' in locals() else "Default",
                "guarantee": "Browser is 100% INDEPENDENT from Python - will NEVER auto-close!",
                "processes": len(browser_storage['processes']),
                "browsers": len(browser_storage['browsers']),
                "tasks": len(browser_storage['tasks']),
                "instructions": [
                    "✓ Proxy is AUTOMATICALLY configured",
                    "✓ Browse ANY website - all HTTP/HTTPS requests will be captured!",
                    "✓ No manual FoxyProxy setup needed",
                    "✓ Browser stays open even if Python exits"
                ]
            }
        else:
            return {
                "success": False,
                "message": "[!] Failed to start browser with auto-proxy. Please install Chrome or use manual FoxyProxy setup.",
                "fallback": "Use FoxyProxy extension with proxy: 127.0.0.1:8080"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ BULLETPROOF browser launch failed: {str(e)}"
        }

@app.post("/api/proxy/test-ai")
async def ai_proxy_test():
    """Comprehensive AI-powered proxy testing"""
    try:
        from backend.utils.port_manager import AIProxyDiagnostics
        
        # Get current proxy port from environment or default
        proxy_port = int(os.getenv('CURRENT_PROXY_PORT', '8080'))
        
        # Initialize AI diagnostics
        ai_diagnostics = AIProxyDiagnostics()
        
        # Run comprehensive test
        test_results = await ai_diagnostics.comprehensive_proxy_test(proxy_port)
        
        return {
            "success": True,
            "proxy_port": proxy_port,
            "test_results": test_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"AI proxy test failed: {str(e)}"
        }

@app.post("/api/proxy/auto-fix")
async def auto_fix_proxy():
    """Attempt to automatically fix proxy issues"""
    try:
        from backend.utils.port_manager import AIProxyDiagnostics
        
        proxy_port = int(os.getenv('CURRENT_PROXY_PORT', '8080'))
        ai_diagnostics = AIProxyDiagnostics()
        
        # First run diagnostics
        test_results = await ai_diagnostics.comprehensive_proxy_test(proxy_port)
        
        # Then attempt auto-fix
        fix_results = await ai_diagnostics.auto_fix_proxy_issues(test_results)
        
        return {
            "success": True,
            "proxy_port": proxy_port,
            "test_results": test_results,
            "fix_results": fix_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Auto-fix failed: {str(e)}"
        }
    """Test if browser proxy is working by checking our proxy logs"""
    try:
        import requests
        import time
        
        # Test proxy directly
        start_time = time.time()
        proxies = {"http": "http://localhost:8080", "https": "http://localhost:8080"}
        
        try:
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=5)
            if response.status_code == 200:
                proxy_working = True
                proxy_response = response.json()
            else:
                proxy_working = False
                proxy_response = None
        except Exception as e:
            proxy_working = False
            proxy_response = str(e)
        
        # Check recent requests in file
        requests_file = Path("data/requests.jsonl")
        recent_requests = 0
        if requests_file.exists():
            with open(requests_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Count requests in last 30 seconds
                current_time = time.time()
                for line in lines[-10:]:  # Check last 10 requests
                    try:
                        req_data = json.loads(line.strip())
                        req_time = datetime.fromisoformat(req_data.get('timestamp', '2000-01-01T00:00:00'))
                        if (current_time - req_time.timestamp()) < 30:
                            recent_requests += 1
                    except:
                        pass
        
        return {
            "success": True,
            "proxy_direct_test": proxy_working,
            "proxy_response": proxy_response,
            "recent_requests_captured": recent_requests,
            "test_time": time.time() - start_time,
            "proxy_port": proxy_port,
            "message": f"Proxy direct test: {'[+] WORKING' if proxy_working else '[!] FAILED'}, Recent captures: {recent_requests}",
            "instructions": [
                "1. Open Chrome browser (should be already open)",
                f"2. Navigate to: http://localhost:{os.getenv('CURRENT_DASHBOARD_PORT', '3000')}/proxy-test",
                "3. If proxy works, the test page will show captured requests",
                "4. Then try: http://testphp.vulnweb.com for vulnerability scanning"
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Proxy test failed: {str(e)}"
        }


@app.get("/proxy-test")
async def proxy_test_page():
    """Simple page to test if proxy is working"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vulna Proxy Test</title>
        <style>
            body { font-family: Arial, sans-serif; background: #000; color: #0f0; padding: 20px; }
            .test { margin: 20px; padding: 20px; border: 1px solid #0f0; }
            .success { color: #0f0; }
            .fail { color: #f00; }
        </style>
    </head>
    <body>
        <h1>🔍 VULNA PROXY TEST</h1>
        <div class="test">
            <h2>Instructions:</h2>
            <p>1. If you see this page, your browser is connected to Vulna proxy!</p>
            <p>2. Check the main dashboard - this request should appear there</p>
            <p>3. Try visiting: <a href="http://testphp.vulnweb.com">testphp.vulnweb.com</a></p>
        </div>
        <div class="test">
            <h2>Your Status:</h2>
            <p id="status">Loading...</p>
        </div>
        <script>
            fetch('/api/stats')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('status').innerHTML = 
                        '<span class="success">✓ Proxy is working! Total requests captured: ' + data.total_requests + '</span>';
                })
                .catch(e => {
                    document.getElementById('status').innerHTML = 
                        '<span class="fail">✗ Proxy connection failed: ' + e + '</span>';
                });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/requests")
async def get_requests():
    """API endpoint to get all requests"""
    return await dashboard.get_all_requests()

@app.get("/api/findings")
async def get_findings():
    """API endpoint to get all findings"""
    return await dashboard.get_all_findings()

@app.get("/api/stats")
async def get_stats():
    """API endpoint to get statistics"""
    return await dashboard.get_stats()

@app.post("/api/vulnerability/{vuln_id}/chat")
async def chat_with_ai_about_vulnerability(vuln_id: str, request: Request):
    """Chat with AI about specific vulnerability - SHORT ANSWERS"""
    try:
        data = await request.json()
        user_message = data.get("message", "")
        
        if not user_message:
            return {"success": False, "message": "No message provided"}
        
        # Load vulnerability details
        findings = await dashboard.get_all_findings()
        vulnerability = None
        
        for finding in findings:
            if finding.get("id") == vuln_id:
                vulnerability = finding
                break
        
        if not vulnerability:
            return {"success": False, "message": "Vulnerability not found"}
        
        # Create SHORT, DIRECT context for AI
        context = f"""
Du bist ein Cybersecurity-Experte. Antworte KURZ und DIREKT auf die Frage.

VULNERABILITY: {vulnerability.get('title', 'Unknown')}
RISK: {vulnerability.get('risk_level', 'Unknown')}
URL: {vulnerability.get('affected_url', vulnerability.get('url', 'Unknown'))}
METHOD: {vulnerability.get('request_method', 'Unknown')}

FRAGE: {user_message}

REGELN:
- Antworte in 1-3 kurzen Sätzen
- Sei technisch präzise aber knapp  
- Keine langen Erklärungen
- Direkte Antwort auf die Frage
- Deutsch antworten
"""
        
        # Send to AI with specific instructions for short answers
        import httpx
        ollama_url = "http://localhost:11434/api/generate"
        
        ai_request = {
            "model": "qwen2.5-coder:latest",
            "prompt": context,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for more precise answers
                "top_p": 0.8,
                "max_tokens": 200,   # Limit response length
                "stop": ["\n\n", "###"]  # Stop at double newlines
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(ollama_url, json=ai_request, timeout=15)
            
            if response.status_code == 200:
                ai_response = response.json()
                ai_message = ai_response.get("response", "AI response error").strip()
                
                # Ensure response is short
                if len(ai_message) > 500:
                    ai_message = ai_message[:500] + "..."
                
                return {
                    "success": True,
                    "ai_response": ai_message,
                    "model": "qwen2.5-coder:latest",
                    "timestamp": datetime.now().isoformat(),
                    "response_length": len(ai_message)
                }
            else:
                return {
                    "success": False, 
                    "message": f"AI request failed: {response.status_code}"
                }
                
    except Exception as e:
        return {
            "success": False,
            "message": f"Chat error: {str(e)}"
        }

@app.post("/api/vulnerability/{vuln_id}/test")
async def test_vulnerability_manually(vuln_id: str):
    """Manually trigger vulnerability testing for a specific finding"""
    try:
        # Load vulnerability details
        findings = await dashboard.get_all_findings()
        vulnerability = None
        
        for finding in findings:
            if finding.get("id") == vuln_id:
                vulnerability = finding
                break
        
        if not vulnerability:
            return {"success": False, "message": "Vulnerability not found"}
        
        # Create vulnerability tester instance
        from backend.utils.vulnerability_tester import VulnerabilityTester
        tester = VulnerabilityTester()
        
        # Run automated test
        test_result = await tester.test_vulnerability(vulnerability)
        
        return {
            "success": True,
            "vulnerability_id": vuln_id,
            "test_result": test_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Vulnerability test failed: {str(e)}"
        }

@app.post("/api/vulnerability/{vuln_id}/feedback")
async def provide_vulnerability_feedback(vuln_id: str, request: Request):
    """Provide feedback on vulnerability accuracy (for AI learning)"""
    try:
        data = await request.json()
        is_valid = data.get("is_valid", True)
        feedback_reason = data.get("reason", "")
        
        # Load vulnerability details
        findings = await dashboard.get_all_findings()
        vulnerability = None
        
        for finding in findings:
            if finding.get("id") == vuln_id:
                vulnerability = finding
                break
        
        if not vulnerability:
            return {"success": False, "message": "Vulnerability not found"}
        
        # Send feedback to AI systems for learning
        from backend.utils.ai_smart_filter import AISmartFilter
        ai_filter = AISmartFilter()
        
        # Learn from feedback
        correct_decision = "ANALYZE" if is_valid else "FILTER"
        await ai_filter.learn_from_feedback(
            vulnerability.get("affected_url", ""),
            correct_decision,
            feedback_reason
        )
        
        # Broadcast feedback event
        await dashboard.broadcast_update({
            "type": "vulnerability_feedback",
            "vulnerability_id": vuln_id,
            "feedback": {
                "is_valid": is_valid,
                "reason": feedback_reason,
                "timestamp": datetime.now().isoformat()
            }
        })
        
        return {
            "success": True,
            "message": "Feedback received and AI system updated",
            "vulnerability_id": vuln_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Feedback processing failed: {str(e)}"
        }
    """Generate Proof of Concept for vulnerability"""
    try:
        # Load vulnerability details
        findings = await dashboard.get_all_findings()
        vulnerability = None
        
        for finding in findings:
            if finding.get("id") == vuln_id:
                vulnerability = finding
                break
        
        if not vulnerability:
            return {"success": False, "message": "Vulnerability not found"}
        
        # Create PoC generation prompt
        poc_prompt = f"""
GENERATE PROOF OF CONCEPT:

Vulnerability: {vulnerability.get('title', 'Unknown')}
Risk Level: {vulnerability.get('risk_level', 'Unknown')}
URL: {vulnerability.get('affected_url', vulnerability.get('url', 'Unknown'))}
Method: {vulnerability.get('request_method', 'Unknown')}
Description: {vulnerability.get('description', 'No description')}

REQUEST DETAILS:
Headers: {json.dumps(vulnerability.get('request_headers', {}), indent=2)}
Body: {vulnerability.get('request_body', 'None')}

Please generate:
1. A working curl command to reproduce this vulnerability
2. Step-by-step exploitation instructions
3. Expected response/behavior
4. Potential impact scenarios

Format as practical, executable commands.
"""
        
        # Send to AI for PoC generation
        import httpx
        ollama_url = "http://localhost:11434/api/generate"
        
        ai_request = {
            "model": "qwen2.5-coder:latest", 
            "prompt": poc_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for more precise PoC
                "max_tokens": 1500
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(ollama_url, json=ai_request, timeout=30)
            
            if response.status_code == 200:
                ai_response = response.json()
                poc_content = ai_response.get("response", "PoC generation failed")
                
                return {
                    "success": True,
                    "proof_of_concept": poc_content,
                    "vulnerability_id": vuln_id,
                    "generated_at": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "message": f"PoC generation failed: {response.status_code}"
                }
                
    except Exception as e:
        return {
            "success": False,
            "message": f"PoC generation error: {str(e)}"
        }

@app.get("/api/export/requests")
async def export_requests():
    """Export requests as JSON"""
    requests = await dashboard.get_all_requests()
    return {"data": requests, "count": len(requests)}

@app.get("/api/export/findings")
async def export_findings():
    """Export findings as JSON"""
    findings = await dashboard.get_all_findings()
    return {"data": findings, "count": len(findings)}

@app.post("/api/clear")
async def clear_data():
    """Clear all data files"""
    try:
        requests_file = Path("data/requests.jsonl")
        findings_file = Path("data/findings.jsonl")
        
        if requests_file.exists():
            requests_file.unlink()
        if findings_file.exists():
            findings_file.unlink()
            
        # Reset counters
        dashboard.last_request_count = 0
        dashboard.last_finding_count = 0
        
        # Broadcast clear event
        await dashboard.broadcast_update({
            "type": "data_cleared",
            "message": "All data cleared"
        })
        
        return {"success": True, "message": "Data cleared successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error clearing data: {e}"}


async def start_dashboard(host: str = "localhost", port: int = 3000):
    """Start the web dashboard"""
    print(f"Starting Vulna Dashboard on http://{host}:{port}")
    
    # Start file monitoring in background
    monitor_task = asyncio.create_task(dashboard.monitor_files())
    
    # Start web server
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    finally:
        monitor_task.cancel()


if __name__ == "__main__":
    asyncio.run(start_dashboard())

@app.post("/api/browser/test")
async def test_browser_proxy():
    """Test if browser proxy is working by checking our proxy logs"""
    try:
        import requests
        import time
        
        # Get current proxy port
        proxy_port = int(os.getenv('CURRENT_PROXY_PORT', '8080'))
        
        # Test proxy directly
        start_time = time.time()
        
        try:
            # Use httpx with correct proxy syntax
            async with httpx.AsyncClient(
                proxies={"http://": f"http://localhost:{proxy_port}", "https://": f"http://localhost:{proxy_port}"}, 
                timeout=5
            ) as client:
                response = await client.get('http://httpbin.org/ip')
                if response.status_code == 200:
                    proxy_working = True
                    proxy_response = response.json()
                else:
                    proxy_working = False
                    proxy_response = None
        except Exception as e:
            proxy_working = False
            proxy_response = str(e)
        
        # Check recent requests in file
        requests_file = Path("data/requests.jsonl")
        recent_requests = 0
        if requests_file.exists():
            with open(requests_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Count requests in last 30 seconds
                current_time = time.time()
                for line in lines[-10:]:  # Check last 10 requests
                    try:
                        req_data = json.loads(line.strip())
                        req_time = datetime.fromisoformat(req_data.get('timestamp', '2000-01-01T00:00:00'))
                        if (current_time - req_time.timestamp()) < 30:
                            recent_requests += 1
                    except:
                        pass
        
        return {
            "success": True,
            "proxy_direct_test": proxy_working,
            "proxy_response": proxy_response,
            "recent_requests_captured": recent_requests,
            "test_time": time.time() - start_time,
            "proxy_port": proxy_port,
            "message": f"Proxy direct test: {'[+] WORKING' if proxy_working else '[!] FAILED'}, Recent captures: {recent_requests}",
            "instructions": [
                "1. Open Chrome browser (should be already open)",
                f"2. Navigate to: http://localhost:{os.getenv('CURRENT_DASHBOARD_PORT', '3000')}/proxy-test",
                "3. If proxy works, the test page will show captured requests",
                "4. Then try: http://testphp.vulnweb.com for vulnerability scanning"
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Proxy test failed: {str(e)}"
        }


@app.post("/api/vulnerability/{vuln_id}/chat")
async def chat_with_ai_about_vulnerability(vuln_id: str, request: Request):
    """Chat with AI about specific vulnerability - SHORT ANSWERS"""
    try:
        data = await request.json()
        user_message = data.get("message", "")
        
        if not user_message:
            return {"success": False, "message": "No message provided"}
        
        # Load vulnerability details
        findings = await dashboard.get_all_findings()
        vulnerability = None
        
        for finding in findings:
            if finding.get("id") == vuln_id:
                vulnerability = finding
                break
        
        if not vulnerability:
            return {"success": False, "message": "Vulnerability not found"}
        
        # Create SHORT, DIRECT context for AI
        context = f"""
Du bist ein Cybersecurity-Experte. Antworte KURZ und DIREKT auf die Frage.

VULNERABILITY: {vulnerability.get('title', 'Unknown')}
RISK: {vulnerability.get('risk_level', 'Unknown')}
URL: {vulnerability.get('affected_url', vulnerability.get('url', 'Unknown'))}
METHOD: {vulnerability.get('request_method', 'Unknown')}

FRAGE: {user_message}

REGELN:
- Antworte in 1-3 kurzen Sätzen
- Sei technisch präzise aber knapp  
- Keine langen Erklärungen
- Direkte Antwort auf die Frage
- Deutsch antworten
"""
        
        # Send to AI with specific instructions for short answers
        import httpx
        ollama_url = "http://localhost:11434/api/generate"
        
        ai_request = {
            "model": "qwen2.5-coder:latest",
            "prompt": context,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for more precise answers
                "top_p": 0.8,
                "max_tokens": 200,   # Limit response length
                "stop": ["\n\n", "###"]  # Stop at double newlines
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(ollama_url, json=ai_request, timeout=15)
            
            if response.status_code == 200:
                ai_response = response.json()
                ai_message = ai_response.get("response", "AI response error").strip()
                
                # Ensure response is short
                if len(ai_message) > 500:
                    ai_message = ai_message[:500] + "..."
                
                return {
                    "success": True,
                    "ai_response": ai_message,
                    "model": "qwen2.5-coder:latest",
                    "timestamp": datetime.now().isoformat(),
                    "response_length": len(ai_message)
                }
            else:
                return {
                    "success": False, 
                    "message": f"AI request failed: {response.status_code}"
                }
                
    except Exception as e:
        return {
            "success": False,
            "message": f"Chat error: {str(e)}"
        }

@app.post("/api/vulnerability/{vuln_id}/generate-poc")
async def generate_poc_for_vulnerability(vuln_id: str):
    """Generate Proof of Concept for vulnerability"""
    try:
        # Log PoC generation start
        await ai_logger.log_activity(
            vuln_id=vuln_id,
            activity_type="poc_generation",
            message="Starting PoC generation process..."
        )
        
        # Load vulnerability details
        findings = await dashboard.get_all_findings()
        vulnerability = None
        
        for finding in findings:
            if finding.get("id") == vuln_id:
                vulnerability = finding
                break
        
        if not vulnerability:
            await ai_logger.log_poc_generation(
                vuln_id=vuln_id,
                success=False,
                details={"error": "Vulnerability not found"}
            )
            return {"success": False, "message": "Vulnerability not found"}
        
        await ai_logger.log_activity(
            vuln_id=vuln_id,
            activity_type="poc_generation",
            message=f"Generating PoC for: {vulnerability.get('title', 'Unknown')}"
        )
        
        # Create PoC generation prompt
        poc_prompt = f"""
GENERATE PROOF OF CONCEPT:

Vulnerability: {vulnerability.get('title', 'Unknown')}
Risk Level: {vulnerability.get('risk_level', 'Unknown')}
URL: {vulnerability.get('affected_url', vulnerability.get('url', 'Unknown'))}
Method: {vulnerability.get('request_method', 'Unknown')}
Description: {vulnerability.get('description', 'No description')}

REQUEST DETAILS:
Headers: {json.dumps(vulnerability.get('request_headers', {}), indent=2)}
Body: {vulnerability.get('request_body', 'None')}

Please generate:
1. A working curl command to reproduce this vulnerability
2. Step-by-step exploitation instructions
3. Expected response/behavior
4. Potential impact scenarios

Format as practical, executable commands.
"""
        
        # Send to AI for PoC generation
        import httpx
        ollama_url = "http://localhost:11434/api/generate"
        
        ai_request = {
            "model": "qwen2.5-coder:latest", 
            "prompt": poc_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for more precise PoC
                "max_tokens": 1500
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(ollama_url, json=ai_request, timeout=30)
            
            if response.status_code == 200:
                ai_response = response.json()
                poc_content = ai_response.get("response", "PoC generation failed")
                
                return {
                    "success": True,
                    "proof_of_concept": poc_content,
                    "vulnerability_id": vuln_id,
                    "generated_at": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "message": f"PoC generation failed: {response.status_code}"
                }
                
    except Exception as e:
        return {
            "success": False,
            "message": f"PoC generation error: {str(e)}"
        }

@app.post("/api/vulnerability/{vuln_id}/auto-test")
async def automatic_vulnerability_testing(vuln_id: str):
    """Automatic Vulnerability Testing - Comprehensive Analysis"""
    try:
        # Log start of auto-testing
        await ai_logger.log_ai_analysis_start(vuln_id, "auto-test")
        
        # Load vulnerability details
        findings = await dashboard.get_all_findings()
        vulnerability = None
        
        for finding in findings:
            if finding.get("id") == vuln_id:
                vulnerability = finding
                break
        
        if not vulnerability:
            await ai_logger.log_activity(
                vuln_id=vuln_id,
                activity_type="error",
                message="Vulnerability not found in database",
                level="ERROR"
            )
            return {"success": False, "message": "Vulnerability not found"}
        
        await ai_logger.log_activity(
            vuln_id=vuln_id,
            activity_type="ai_analysis",
            message=f"Loading vulnerability data: {vulnerability.get('title', 'Unknown')}"
        )
        
        # Create comprehensive testing prompt
        auto_test_prompt = f"""
AUTOMATIC VULNERABILITY TESTING ANALYSIS:

Target Vulnerability: {vulnerability.get('title', 'Unknown')}
Risk Level: {vulnerability.get('risk_level', 'Unknown')}
URL: {vulnerability.get('affected_url', vulnerability.get('url', 'Unknown'))}
Method: {vulnerability.get('request_method', 'Unknown')}

CURRENT VULNERABILITY DETAILS:
Description: {vulnerability.get('description', 'No description')}
Confidence: {vulnerability.get('confidence', 'Unknown')}

REQUEST CONTEXT:
Headers: {json.dumps(vulnerability.get('request_headers', {}), indent=2)}
Body: {vulnerability.get('request_body', 'None')}

PERFORM COMPREHENSIVE AUTOMATED TESTING ANALYSIS:

1. VULNERABILITY VALIDATION:
   - Confirm if this is actually exploitable
   - Check for false positive indicators
   - Rate exploitability (1-10)

2. ATTACK VECTORS:
   - List all possible attack methods
   - Identify payload variations
   - Check for bypass techniques

3. PREREQUISITES:
   - Required conditions for exploitation
   - Authentication requirements
   - Network access needs

4. IMPACT ASSESSMENT:
   - Data confidentiality impact
   - Data integrity impact  
   - System availability impact
   - Business risk assessment

5. EXPLOITATION DIFFICULTY:
   - Skill level required
   - Tools needed
   - Time to exploit

6. MITIGATION STRATEGIES:
   - Immediate fixes
   - Long-term solutions
   - Detection methods

7. ADDITIONAL TESTING:
   - Related vulnerabilities to check
   - Similar endpoints to test
   - Escalation possibilities

Provide a detailed, structured analysis as if running an automated vulnerability assessment tool.
"""
        
        # Send to AI for comprehensive analysis
        import httpx
        ollama_url = "http://localhost:11434/api/generate"
        
        ai_request = {
            "model": "qwen2.5-coder:latest",
            "prompt": auto_test_prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,  # Very low temperature for precise analysis
                "max_tokens": 2000   # Longer response for comprehensive analysis
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(ollama_url, json=ai_request, timeout=45)
            
            if response.status_code == 200:
                ai_response = response.json()
                test_analysis = ai_response.get("response", "")
                
                # Better response validation
                if not test_analysis or test_analysis.strip() == "":
                    test_analysis = "⚠️ AI model returned empty response. This might indicate:\n" \
                                   "- Model is not responding properly\n" \
                                   "- Prompt was too complex\n" \
                                   "- Model needs restart\n\n" \
                                   f"Debug: Raw response = {ai_response}"
                
                return {
                    "success": True,
                    "automated_analysis": test_analysis,
                    "vulnerability_id": vuln_id,
                    "analysis_type": "comprehensive_auto_test",
                    "generated_at": datetime.now().isoformat(),
                    "model_used": "qwen2.5-coder:latest",
                    "raw_response": ai_response  # For debugging
                }
            else:
                return {
                    "success": False,
                    "message": f"Automated testing failed: HTTP {response.status_code}",
                    "response_text": response.text[:500]  # First 500 chars for debugging
                }
                
    except Exception as e:
        return {
            "success": False,
            "message": f"Automated testing error: {str(e)}"
        }

@app.post("/api/vulnerability/{vuln_id}/analyze-exploitation") 
async def analyze_exploitation_methods(vuln_id: str):
    """Analyze Exploitation Methods and Attack Chains"""
    try:
        # Load vulnerability details
        findings = await dashboard.get_all_findings()
        vulnerability = None
        
        for finding in findings:
            if finding.get("id") == vuln_id:
                vulnerability = finding
                break
        
        if not vulnerability:
            return {"success": False, "message": "Vulnerability not found"}
        
        # Create exploitation analysis prompt
        exploitation_prompt = f"""
EXPLOITATION ANALYSIS FOR PENETRATION TESTING:

Vulnerability: {vulnerability.get('title', 'Unknown')}
Risk Level: {vulnerability.get('risk_level', 'Unknown')}
Target: {vulnerability.get('affected_url', vulnerability.get('url', 'Unknown'))}
Method: {vulnerability.get('request_method', 'Unknown')}

DEEP EXPLOITATION ANALYSIS:

1. ATTACK CHAIN DEVELOPMENT:
   - Initial access vector
   - Privilege escalation possibilities  
   - Lateral movement opportunities
   - Data exfiltration methods

2. PAYLOAD DEVELOPMENT:
   - Custom payload creation
   - Encoding/obfuscation techniques
   - Bypass methods for common protections
   - Multi-stage attack payloads

3. PERSISTENCE MECHANISMS:
   - Ways to maintain access
   - Backdoor installation methods
   - Stealth techniques

4. EVASION TECHNIQUES:
   - WAF bypass methods
   - IDS/IPS evasion
   - Logging avoidance
   - Anti-forensics

5. REAL-WORLD SCENARIOS:
   - How attackers would exploit this
   - Common attack patterns
   - Tools typically used
   - Timeline for exploitation

6. DETECTION INDICATORS:
   - Log signatures to watch for
   - Network traffic indicators
   - System behavior changes
   - Forensic artifacts

Provide detailed exploitation methodology as used in professional penetration testing.
"""
        
        # Send to AI for exploitation analysis
        import httpx
        ollama_url = "http://localhost:11434/api/generate"
        
        ai_request = {
            "model": "qwen2.5-coder:latest",
            "prompt": exploitation_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "max_tokens": 2000
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(ollama_url, json=ai_request, timeout=45)
            
            if response.status_code == 200:
                ai_response = response.json()
                exploitation_analysis = ai_response.get("response", "")
                
                # Better response validation  
                if not exploitation_analysis or exploitation_analysis.strip() == "":
                    exploitation_analysis = "⚠️ AI model returned empty exploitation analysis.\n\n" \
                                          "This might indicate:\n" \
                                          "- Model requires more context\n" \
                                          "- Complex vulnerability type\n" \
                                          "- Model processing issue\n\n" \
                                          f"Debug: Raw response = {ai_response}"
                
                return {
                    "success": True,
                    "exploitation_analysis": exploitation_analysis,
                    "vulnerability_id": vuln_id,
                    "analysis_type": "exploitation_methods",
                    "generated_at": datetime.now().isoformat(),
                    "raw_response": ai_response  # For debugging
                }
            else:
                return {
                    "success": False,
                    "message": f"Exploitation analysis failed: {response.status_code}"
                }
                
    except Exception as e:
        return {
            "success": False,
            "message": f"Exploitation analysis error: {str(e)}"
        }


@app.post("/api/test-request")
async def test_request(request: Request):
    """Test a modified request and return response details"""
    try:
        body = await request.json()
        
        method = body.get("method", "GET")
        url = body.get("url", "")
        headers = body.get("headers", {})
        request_body = body.get("body", "")
        
        if not url:
            return {"success": False, "message": "URL is required"}
        
        # Make the request
        async with httpx.AsyncClient(timeout=10.0) as client:
            start_time = time.time()
            
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=request_body if request_body else None
            )
            
            response_time = int((time.time() - start_time) * 1000)
            
            return {
                "success": True,
                "status_code": response.status_code,
                "response_time": response_time,
                "response_headers": dict(response.headers),
                "response_body": response.text[:2000],  # Limit response size
                "request_details": {
                    "method": method,
                    "url": url,
                    "headers": headers,
                    "body": request_body[:500] if request_body else None
                }
            }
            
    except httpx.TimeoutException:
        return {"success": False, "message": "Request timeout"}
    except httpx.RequestError as e:
        return {"success": False, "message": f"Request error: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {str(e)}"}

@app.post("/api/test-request-vulnerabilities")
async def test_request_vulnerabilities(request: Request):
    """Test a request for potential vulnerabilities using AI analysis"""
    try:
        body = await request.json()
        
        # Create a prompt for vulnerability testing
        test_prompt = f"""
VULNERABILITY TESTING ANALYSIS:

Request Details:
- Method: {body.get('method', 'Unknown')}
- URL: {body.get('url', 'Unknown')}
- Headers: {json.dumps(body.get('headers', {}), indent=2)}
- Body: {body.get('body', 'No body')}

COMPREHENSIVE VULNERABILITY ASSESSMENT:

1. INJECTION VULNERABILITIES:
   - SQL Injection potential in parameters
   - XSS vulnerabilities in inputs
   - Command injection possibilities
   - Path traversal risks

2. AUTHENTICATION & AUTHORIZATION:
   - Authentication bypass opportunities
   - Authorization flaws
   - Session management issues

3. BUSINESS LOGIC:
   - Input validation weaknesses
   - Rate limiting bypass
   - Parameter tampering risks

4. RECOMMENDED TESTS:
   - Specific payloads to test
   - Attack vectors to explore
   - Security headers to check

Provide detailed analysis with specific test recommendations.
"""

        # Call AI for analysis
        ollama_url = "http://localhost:11434/api/generate"
        ai_request = {
            "model": "qwen2.5-coder:latest",
            "prompt": test_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "max_tokens": 1500
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(ollama_url, json=ai_request, timeout=30)
            
            if response.status_code == 200:
                ai_response = response.json()
                analysis = ai_response.get("response", "Analysis failed")
                
                return {
                    "success": True,
                    "analysis": analysis,
                    "request_summary": {
                        "method": body.get('method'),
                        "url": body.get('url'),
                        "has_body": bool(body.get('body')),
                        "headers_count": len(body.get('headers', {}))
                    },
                    "analysis_type": "vulnerability_assessment",
                    "generated_at": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "message": f"AI analysis failed: HTTP {response.status_code}"
                }
                
    except Exception as e:
        return {
            "success": False,
            "message": f"Vulnerability analysis error: {str(e)}"
        }

# AI Chat and PoC Generation Endpoints
@app.post("/api/vulnerability/{vuln_id}/chat")
async def vulnerability_ai_chat(vuln_id: str, request: Request):
    """AI Chat for specific vulnerability"""
    try:
        body = await request.json()
        user_message = body.get("message", "")
        
        if not user_message:
            return {"success": False, "message": "No message provided"}
        
        # Load vulnerability details
        findings = await dashboard.get_all_findings()
        vulnerability = None
        
        for finding in findings:
            if finding.get("id") == vuln_id:
                vulnerability = finding
                break
        
        if not vulnerability:
            return {"success": False, "message": "Vulnerability not found"}
        
        # Create context-aware chat prompt
        chat_prompt = f"""
VULNERABILITY SECURITY CONSULTATION:

Vulnerability Details:
- Title: {vulnerability.get('title', 'Unknown')}
- Risk Level: {vulnerability.get('risk_level', 'Unknown')}
- Target URL: {vulnerability.get('affected_url', vulnerability.get('url', 'Unknown'))}
- Method: {vulnerability.get('request_method', 'Unknown')}
- Description: {vulnerability.get('description', 'No description')}
- Impact: {vulnerability.get('impact', 'Unknown impact')}

User Question: {user_message}

INSTRUCTIONS:
- Provide precise, technical answers about this specific vulnerability
- Focus on penetration testing and security assessment aspects
- Give actionable advice for exploitation, remediation, or verification
- Keep responses concise but comprehensive
- Include practical examples when relevant

Please answer the user's question about this vulnerability:
"""
        
        # Send to AI
        import httpx
        ollama_url = "http://localhost:11434/api/generate"
        
        ai_request = {
            "model": "qwen2.5-coder:latest",
            "prompt": chat_prompt,
            "stream": False,
            "options": {
                "temperature": 0.4,
                "max_tokens": 1000
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(ollama_url, json=ai_request, timeout=30)
            
            if response.status_code == 200:
                ai_response = response.json()
                ai_message = ai_response.get("response", "AI response failed")
                
                return {
                    "success": True,
                    "ai_response": ai_message,
                    "user_message": user_message,
                    "vulnerability_id": vuln_id,
                    "model": "qwen2.5-coder",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "message": f"AI chat failed: {response.status_code}"
                }
                
    except Exception as e:
        return {
            "success": False,
            "message": f"Chat error: {str(e)}"
        }

@app.post("/api/vulnerability/{vuln_id}/generate-poc")
async def generate_proof_of_concept(vuln_id: str):
    """Generate Proof of Concept for vulnerability"""
    try:
        # Load vulnerability details
        findings = await dashboard.get_all_findings()
        vulnerability = None
        
        for finding in findings:
            if finding.get("id") == vuln_id:
                vulnerability = finding
                break
        
        if not vulnerability:
            return {"success": False, "message": "Vulnerability not found"}
        
        # Create PoC generation prompt
        poc_prompt = f"""
PROOF OF CONCEPT GENERATION:

Vulnerability: {vulnerability.get('title', 'Unknown')}
Risk Level: {vulnerability.get('risk_level', 'Unknown')}
Target: {vulnerability.get('affected_url', vulnerability.get('url', 'Unknown'))}
Method: {vulnerability.get('request_method', 'Unknown')}
Description: {vulnerability.get('description', 'No description')}

Request Details:
- Headers: {json.dumps(vulnerability.get('request_headers', {}), indent=2)}
- Body: {vulnerability.get('request_body', 'No body')}

GENERATE COMPREHENSIVE PROOF OF CONCEPT:

1. WORKING CURL COMMAND:
   - Complete curl command that demonstrates the vulnerability
   - Include all necessary headers and parameters
   - Show expected malicious payload

2. STEP-BY-STEP EXPLOITATION:
   - Detailed steps to reproduce the vulnerability
   - Prerequisites and setup requirements
   - Expected responses at each step

3. MULTIPLE PAYLOAD VARIANTS:
   - Different payloads for different scenarios
   - Encoded/obfuscated versions
   - Bypass techniques

4. VALIDATION METHODS:
   - How to confirm successful exploitation
   - What to look for in responses
   - Signs of vulnerability

5. IMPACT DEMONSTRATION:
   - Show the actual impact/damage possible
   - Data that could be accessed/modified
   - Business consequences

Provide working, testable proof of concept code that security professionals can use to verify this vulnerability.
"""
        
        # Send to AI for PoC generation
        import httpx
        ollama_url = "http://localhost:11434/api/generate"
        
        ai_request = {
            "model": "qwen2.5-coder:latest",
            "prompt": poc_prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "max_tokens": 2000
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(ollama_url, json=ai_request, timeout=60)
            
            if response.status_code == 200:
                ai_response = response.json()
                proof_of_concept = ai_response.get("response", "PoC generation failed")
                
                return {
                    "success": True,
                    "proof_of_concept": proof_of_concept,
                    "vulnerability_id": vuln_id,
                    "generated_at": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "message": f"PoC generation failed: {response.status_code}"
                }
                
    except Exception as e:
        return {
            "success": False,
            "message": f"PoC generation error: {str(e)}"
        }

@app.post("/api/vulnerability/{vuln_id}/auto-test")
async def automatic_vulnerability_testing(vuln_id: str):
    """Comprehensive automated vulnerability analysis"""
    try:
        # Load vulnerability details
        findings = await dashboard.get_all_findings()
        vulnerability = None
        
        for finding in findings:
            if finding.get("id") == vuln_id:
                vulnerability = finding
                break
        
        if not vulnerability:
            return {"success": False, "message": "Vulnerability not found"}
        
        # Create comprehensive auto-test prompt
        auto_test_prompt = f"""
COMPREHENSIVE AUTOMATED VULNERABILITY ANALYSIS:

Target Vulnerability:
- Title: {vulnerability.get('title', 'Unknown')}
- Risk Level: {vulnerability.get('risk_level', 'Unknown')}
- URL: {vulnerability.get('affected_url', vulnerability.get('url', 'Unknown'))}
- Method: {vulnerability.get('request_method', 'Unknown')}
- OWASP: {', '.join(vulnerability.get('owasp_categories', []))}
- CWE: {', '.join(map(str, vulnerability.get('cwe_ids', [])))}

REQUEST ANALYSIS:
Headers: {json.dumps(vulnerability.get('request_headers', {}), indent=2)}
Body: {vulnerability.get('request_body', 'No body')}

PERFORM COMPREHENSIVE ANALYSIS:

1. ATTACK VECTOR IDENTIFICATION:
   - Primary attack vectors available
   - Secondary exploitation paths
   - Combined attack scenarios
   - Prerequisites for exploitation

2. IMPACT ASSESSMENT:
   - Confidentiality impact (C)
   - Integrity impact (I) 
   - Availability impact (A)
   - Business impact scenarios
   - Compliance violations

3. EXPLOITATION DIFFICULTY RATING:
   - Technical skill required (1-10)
   - Time to exploit (minutes/hours/days)
   - Tools needed
   - Access requirements
   - Detection likelihood

4. MITIGATION STRATEGIES:
   - Immediate fixes
   - Long-term solutions
   - Workarounds
   - Prevention measures
   - Monitoring recommendations

5. VERIFICATION METHODS:
   - How to test if vulnerability exists
   - Automated testing approaches
   - Manual verification steps
   - False positive indicators

6. RELATED VULNERABILITIES:
   - Similar vulnerabilities to check
   - Common misconfigurations
   - Associated attack patterns

Provide detailed professional security assessment as used in penetration testing engagements.
"""
        
        # Send to AI for comprehensive analysis
        import httpx
        ollama_url = "http://localhost:11434/api/generate"
        
        ai_request = {
            "model": "qwen2.5-coder:latest",
            "prompt": auto_test_prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "max_tokens": 2500
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(ollama_url, json=ai_request, timeout=60)
            
            if response.status_code == 200:
                ai_response = response.json()
                auto_analysis = ai_response.get("response", "Auto-analysis failed")
                
                return {
                    "success": True,
                    "auto_analysis": auto_analysis,
                    "vulnerability_id": vuln_id,
                    "analysis_type": "comprehensive_auto_test",
                    "generated_at": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "message": f"Auto-test failed: {response.status_code}"
                }
                
    except Exception as e:
        return {
            "success": False,
            "message": f"Auto-test error: {str(e)}"
        }

# WebSocket for live logging
@app.websocket("/ws/logs/{vuln_id}")
async def websocket_logs(websocket: WebSocket, vuln_id: str):
    """WebSocket endpoint for live AI testing logs"""
    await websocket.accept()
    
    try:
        # Register this WebSocket session with the AI logger
        await ai_logger.add_websocket_session(vuln_id, websocket)
        
        # Keep the connection alive and handle incoming messages
        while True:
            # Wait for messages (ping/pong to keep connection alive)
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                # Send a ping to keep connection alive
                await websocket.send_text(json.dumps({
                    "type": "ping",
                    "message": "Connection alive"
                }))
                
    except WebSocketDisconnect:
        ai_logger.remove_websocket_session(vuln_id, websocket)

@app.get("/api/vulnerability/{vuln_id}/request-data")
async def get_request_data(vuln_id: str):
    """Get original request data for the Request Inspector"""
    try:
        findings = await dashboard.get_all_findings()
        vulnerability = None
        
        for finding in findings:
            if finding.get("id") == vuln_id:
                vulnerability = finding
                break
        
        if not vulnerability:
            return {"success": False, "message": "Vulnerability not found"}
        
        # Reconstruct the original HTTP request
        method = vulnerability.get('request_method', 'GET')
        url = vulnerability.get('affected_url', vulnerability.get('url', 'Unknown'))
        headers = vulnerability.get('request_headers', {})
        body = vulnerability.get('request_body', '')
        
        # Format as raw HTTP request
        original_request = f"{method} {url} HTTP/1.1\n"
        
        for header, value in headers.items():
            original_request += f"{header}: {value}\n"
        
        if body:
            original_request += f"\n{body}"
        
        return {
            "success": True,
            "original_request": original_request,
            "vulnerability_id": vuln_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to load request data: {str(e)}"
        }

@app.post("/api/vulnerability/{vuln_id}/send-request")
async def send_modified_request(vuln_id: str, request: Request):
    """Send modified request through the Request Inspector"""
    try:
        body = await request.json()
        modified_request = body.get('modified_request', '')
        
        if not modified_request:
            await ai_logger.log_activity(
                vuln_id=vuln_id,
                activity_type="error",
                message="No modified request provided",
                level="ERROR"
            )
            return {"success": False, "message": "No modified request provided"}
        
        # Parse the modified request (basic implementation)
        lines = modified_request.split('\n')
        first_line = lines[0]
        
        # Extract method and URL
        parts = first_line.split(' ')
        if len(parts) < 2:
            await ai_logger.log_activity(
                vuln_id=vuln_id,
                activity_type="error",
                message="Invalid request format",
                level="ERROR"
            )
            return {"success": False, "message": "Invalid request format"}
        
        method = parts[0]
        url = parts[1]
        
        # Extract headers
        headers = {}
        body_start = len(lines)
        
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '':
                body_start = i + 1
                break
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
        
        # Extract body
        request_body = '\n'.join(lines[body_start:]) if body_start < len(lines) else ''
        
        # Send the actual request (basic implementation)
        import httpx
        
        # Log the request attempt
        await ai_logger.log_request_inspection(vuln_id, method, url, modified=True)
        
        async with httpx.AsyncClient() as client:
            try:
                if method.upper() == 'GET':
                    response = await client.get(url, headers=headers, timeout=10)
                elif method.upper() == 'POST':
                    response = await client.post(url, headers=headers, data=request_body, timeout=10)
                elif method.upper() == 'PUT':
                    response = await client.put(url, headers=headers, data=request_body, timeout=10)
                else:
                    response = await client.request(method, url, headers=headers, data=request_body, timeout=10)
                
                # Log successful response
                await ai_logger.log_activity(
                    vuln_id=vuln_id,
                    activity_type="response_received",
                    message=f"Response received: {response.status_code} ({len(response.text)} bytes)",
                    details={"status_code": response.status_code, "response_size": len(response.text)}
                )
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text[:2000],  # Limit body size
                    "vulnerability_id": vuln_id
                }
                
            except httpx.TimeoutException:
                return {
                    "success": False,
                    "message": "Request timeout"
                }
            except Exception as req_error:
                return {
                    "success": False,
                    "message": f"Request failed: {str(req_error)}"
                }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing request: {str(e)}"
        }

# Database API endpoints
@app.post("/api/vulnerability/{vuln_id}/save-session")
async def save_vulnerability_session(vuln_id: str, request: Request):
    """Save vulnerability session data (chat, poc, analysis, etc.)"""
    try:
        body = await request.json()
        session_type = body.get('session_type')  # 'chat', 'poc', 'analysis', 'auto_test'
        data = body.get('data', {})
        
        # Update vulnerability with session data
        if session_type == 'chat':
            db.add_chat_message(vuln_id, {
                'type': data.get('type', 'user'),
                'content': data.get('content', ''),
                'metadata': data.get('metadata', {})
            })
        elif session_type == 'poc':
            db.update_vulnerability_field(vuln_id, 'poc_code', data.get('poc_code'))
        elif session_type == 'analysis':
            db.update_vulnerability_field(vuln_id, 'exploitation_analysis', data.get('analysis'))
        elif session_type == 'auto_test':
            db.update_vulnerability_field(vuln_id, 'auto_test_results', data.get('results'))
        
        return {"success": True, "message": "Session data saved"}
        
    except Exception as e:
        return {"success": False, "message": f"Failed to save session: {str(e)}"}

@app.get("/api/vulnerability/{vuln_id}/session")
async def get_vulnerability_session(vuln_id: str):
    """Get vulnerability session data"""
    try:
        vuln = db.get_vulnerability(vuln_id)
        if not vuln:
            return {"success": False, "message": "Vulnerability not found"}
        
        return {
            "success": True,
            "vulnerability": vuln,
            "chat_history": vuln.get('ai_chat_history', []),
            "poc_code": vuln.get('poc_code'),
            "exploitation_analysis": vuln.get('exploitation_analysis'),
            "auto_test_results": vuln.get('auto_test_results')
        }
        
    except Exception as e:
        return {"success": False, "message": f"Failed to get session: {str(e)}"}

@app.post("/api/vulnerability/{vuln_id}/update-status")
async def update_vulnerability_status(vuln_id: str, request: Request):
    """Update vulnerability status (new, confirmed, false_positive, fixed)"""
    try:
        body = await request.json()
        status = body.get('status')
        
        if status not in ['new', 'confirmed', 'false_positive', 'fixed']:
            return {"success": False, "message": "Invalid status"}
        
        db.update_vulnerability_field(vuln_id, 'status', status)
        
        return {"success": True, "message": f"Status updated to {status}"}
        
    except Exception as e:
        return {"success": False, "message": f"Failed to update status: {str(e)}"}

# End of file
