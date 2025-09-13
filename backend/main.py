"""Vulna Pentest AI - Main System with AI Session Management"""

import asyncio
import subprocess
import threading
import time
import os
import sys
import socket
from pathlib import Path

# Add current directory to Python path  
sys.path.insert(0, os.getcwd())

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from backend.utils.queue import VulnaQueue
from backend.llm.worker import OllamaLLMWorker
from backend.utils.file_watcher import FileWatcher
from backend.web.dashboard import start_dashboard
from backend.utils.port_manager import EnhancedPortManager
from backend.ai.session_manager import AISessionManager


class VulnaPentestAI:
    def __init__(self):
        self.proxy_process = None
        self.monitoring_task = None
        
        # Load configuration from environment
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'qwen2.5-coder:14b')
        self.ollama_host = os.getenv('OLLAMA_HOST', 'localhost')
        self.ollama_port = int(os.getenv('OLLAMA_PORT', '11434'))
        self.llm_workers_count = int(os.getenv('LLM_WORKERS', '3'))
        
        # Initialize intelligent port manager
        self.port_manager = EnhancedPortManager()
        self.proxy_port = None
        self.dashboard_port = None
        
        self.queue_max_size = int(os.getenv('QUEUE_MAX_SIZE', '1000'))
        
        # Initialize components
        self.queue = VulnaQueue(maxsize=self.queue_max_size)
        self.llm_worker = OllamaLLMWorker(
            ollama_host=self.ollama_host,
            ollama_port=self.ollama_port,
            model_name=self.ollama_model,
            max_workers=self.llm_workers_count
        )
        self.llm_workers = []
        self.file_watcher = None
        self.dashboard_task = None
        
    async def start(self):
        print("Starting Vulna Pentest AI with Intelligent Port Management...")
        print(f"Queue initialized with maxsize={self.queue_max_size}")
        print(f"LLM Worker configured for Ollama ({self.ollama_model})")
        print(f"Using {self.llm_workers_count} LLM workers")
        print("=" * 60)
        
        Path("data").mkdir(exist_ok=True)
        
        try:
            # 1. Intelligent port setup with AI diagnostics
            await self._setup_intelligent_ports()
            
            # 2. Start proxy with enhanced monitoring
            await self._start_enhanced_proxy()
            
            # 3. Start LLM workers
            await self._start_llm_workers()
            
            # 4. Start file watcher to feed the queue
            await self._start_file_watcher()
            
            # 5. Start Web Dashboard
            await self._start_web_dashboard()
            
            # 6. Start continuous proxy monitoring
            await self._start_proxy_monitoring()
            
            # 7. Show instructions and keep running
            await self._run_live_monitoring()
            
        except KeyboardInterrupt:
            print("\nStopping Vulna Pentest AI...")
        finally:
            await self._cleanup()
    
    async def _setup_intelligent_ports(self):
        """Set up ports with intelligent conflict resolution"""
        print("Setting up intelligent port management...")
        
        # Get preferred ports from environment
        preferred_proxy = int(os.getenv('PROXY_PORT', '8080'))
        preferred_dashboard = int(os.getenv('DASHBOARD_PORT', '3000'))
        
        # Setup proxy port with AI analysis
        proxy_setup = await self.port_manager.setup_proxy_with_intelligence(preferred_proxy)
        self.proxy_port = proxy_setup["proxy_port"]
        
        if not self.proxy_port:
            raise RuntimeError("Failed to allocate proxy port")
        
        # Simple dashboard port (no AI needed as you mentioned)
        self.dashboard_port = self.port_manager.port_manager.find_free_port(preferred_dashboard)
        
        # Log results
        print(f"Proxy Port: {self.proxy_port}")
        if proxy_setup["port_selection"].get("port_changed"):
            conflict = proxy_setup["port_selection"].get("conflict_reason", {})
            print(f"   Changed from {preferred_proxy} (occupied by: {conflict.get('name', 'unknown')})")
        
        print(f"Dashboard Port: {self.dashboard_port}")
        if self.dashboard_port != preferred_dashboard:
            print(f"   Changed from {preferred_dashboard} (port conflict)")
        
        # Show AI recommendations if any
        recommendations = proxy_setup.get("recommendations", [])
        if recommendations:
            print("\nAI Recommendations:")
            for rec in recommendations[:3]:  # Show first 3
                print(f"   {rec}")
        
        print()
    
    async def _start_enhanced_proxy(self):
        """Start proxy with enhanced error handling and AI diagnostics"""
        print("Starting mitmproxy with enhanced monitoring...")
        
        def start_mitm():
            try:
                cmd = [
                    "mitmdump", 
                    "-s", "backend/proxy/addon_simple.py", 
                    "--listen-port", str(self.proxy_port),
                    "--set", "confdir=~/.mitmproxy",
                    "--set", "connection_strategy=lazy",
                    "--quiet"
                ]
                
                print(f"[*] Command: {' '.join(cmd)}")
                
                self.proxy_process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                
                print(f"[+] mitmproxy started on port {self.proxy_port}")
                    
            except Exception as e:
                print(f"[!] Failed to start mitmproxy: {e}")
        
        threading.Thread(target=start_mitm, daemon=True).start()
        
        # Enhanced proxy readiness check with AI diagnostics
        print("Performing AI-powered proxy diagnostics...")
        await asyncio.sleep(3)  # Give proxy time to start
        
        # Use AI diagnostics to check proxy health
        test_results = await self.port_manager.ai_diagnostics.comprehensive_proxy_test(self.proxy_port)
        
        print(f"\nAI Proxy Diagnosis: {test_results.get('overall_status', 'unknown').upper()}")
        if test_results.get("ai_diagnosis"):
            print(f"   💭 {test_results['ai_diagnosis']}")
        
        # Show key recommendations
        recommendations = test_results.get("recommendations", [])
        if recommendations:
            print("\n📋 Proxy Recommendations:")
            for rec in recommendations[:3]:
                print(f"   {rec}")
        
        # Auto-fix if proxy is failing
        if test_results.get("overall_status") == "failing":
            print("\n🔧 Attempting auto-fix...")
            fix_results = await self.port_manager.ai_diagnostics.auto_fix_proxy_issues(test_results)
            if fix_results.get("auto_fix_success"):
                print("   Auto-fix successful!")
            else:
                print("   Auto-fix failed - manual intervention required")
        
        print()
    
    async def _start_llm_workers(self):
        """Start LLM workers for processing captured traffic."""
        try:
            print("AI Starting LLM workers...")
            self.llm_workers = await self.llm_worker.start_workers(
                self.queue.queue, 
                "data/findings.jsonl"
            )
            print("LLM workers ready for AI analysis!")
        except Exception as e:
            print(f"LLM workers failed to start: {e}")
            print("   (Install Ollama: https://ollama.ai)")
            print("   (Run: ollama run llama3.2)")
    
    async def _start_file_watcher(self):
        """Start file watcher to monitor requests and feed the queue."""
        print("File Starting file watcher...")
        self.file_watcher = FileWatcher("data/requests.jsonl", self.queue)
        await self.file_watcher.start()
        print("File watcher monitoring proxy requests")
    
    async def _start_web_dashboard(self):
        """Start the web dashboard for monitoring and control."""
        print("Web Starting dashboard server...")
        
        # Start dashboard in background task
        self.dashboard_task = asyncio.create_task(
            start_dashboard(host="localhost", port=self.dashboard_port)
        )
        
        # Give it a moment to start
        await asyncio.sleep(2)
        print(f"Web Dashboard available at: http://localhost:{self.dashboard_port}")
    
    async def _run_live_monitoring(self):
        print("\n" + "=" * 50)
        print("VULNA IS LIVE!")
        print("=" * 50)
        print("Stats will be shown every 5 seconds")
        print("All requests saved to: data/requests.jsonl")
        print("AI findings saved to: data/findings.jsonl")
        print("")
        print("WEB DASHBOARD: http://localhost:{}".format(self.dashboard_port))
        print("PROXY SETTINGS: localhost:{}".format(self.proxy_port))
        print("")
        print("BROWSER SETUP:")
        print("  1. Open your browser")
        print("  2. Set HTTP/HTTPS proxy to: 127.0.0.1:{}".format(self.proxy_port))
        print("  3. Browse any website to capture traffic")
        print("")
        print("Press Ctrl+C to stop")
        print("=" * 50)
        
        start_time = time.time()
        
        while True:
            await asyncio.sleep(5)
            
            # Show stats
            runtime = time.time() - start_time
            print(f"\nRuntime: {runtime:.0f}s")
            
            # Check requests file
            requests_file = Path("data/requests.jsonl")
            findings_file = Path("data/findings.jsonl")
            
            if requests_file.exists():
                with open(requests_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    print(f"Total requests captured: {len(lines)}")
                    
                    if lines:
                        # Show last request
                        try:
                            import json
                            last_request = json.loads(lines[-1])
                            print(f"Last: {last_request.get('method', '')} {last_request.get('url', '')}")
                        except:
                            pass
            else:
                print("No requests captured yet")
            
            # Queue stats
            queue_stats = self.queue.get_stats()
            print(f"Queue: {queue_stats['current_size']} items pending")
            
            # LLM worker stats
            llm_stats = self.llm_worker.get_stats()
            print(f"AI Analysis: {llm_stats['processed_count']} completed, {llm_stats['error_count']} errors")
            
            # Findings count
            if findings_file.exists():
                with open(findings_file, 'r', encoding='utf-8') as f:
                    findings_count = len(f.readlines())
                    print(f"Vulnerabilities found: {findings_count}")
            
            print(f"Dashboard: http://localhost:{self.dashboard_port} | Proxy: localhost:{self.proxy_port}")
            
    async def _cleanup(self):
        print("Cleaning up...")
        
        # Cancel dashboard
        if self.dashboard_task:
            self.dashboard_task.cancel()
        
        # Cancel LLM workers
        for worker in self.llm_workers:
            worker.cancel()
        
        # Stop file watcher
        if self.file_watcher:
            await self.file_watcher.stop()
        
        # Stop proxy
        if self.proxy_process:
            self.proxy_process.terminate()
        
        print("Cleanup completed")
        print("Check data/requests.jsonl for captured traffic")
        print("   Check data/requests.jsonl for captured traffic")
        print("   Check data/findings.jsonl for vulnerabilities")
        print("   AI filtering and analysis statistics saved")

    async def _start_proxy_monitoring(self):
        """Start continuous proxy monitoring with AI"""
        print("Starting continuous proxy monitoring...")
        
        self.monitoring_task = asyncio.create_task(
            self.port_manager.continuous_proxy_monitoring(self.proxy_port, interval=60)
        )
        
        print(f"   AI monitoring active on port {self.proxy_port} (check every 60s)")


async def main():
    """Main application entry point with intelligent systems."""
    app = VulnaPentestAI()
    await app.start()


if __name__ == "__main__":
    asyncio.run(main())
