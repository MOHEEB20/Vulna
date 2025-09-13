"""Vulna Pentest AI - Working Version with proper proxy timing"""

import asyncio, subprocess, threading, time, os
from pathlib import Path
from playwright.async_api import async_playwright
from backend.utils.queue import VulnaQueue
from backend.llm.worker import OllamaLLMWorker
from backend.utils.file_watcher import FileWatcher


class VulnaPentestAI:
    def __init__(self):
        self.proxy_process = None
        self.browser = None
        self.queue = VulnaQueue(maxsize=1000)
        self.llm_worker = OllamaLLMWorker()
        self.llm_workers = []
        self.file_watcher = None
        
    async def start(self):
        print("Starting Vulna Pentest AI...")
        print("Queue initialized with maxsize=1000")
        print("LLM Worker configured for Ollama (llama3.2)")
        print("=" * 50)
        
        Path("data").mkdir(exist_ok=True)
        
        try:
            # 1. Start proxy and wait for it to be ready
            await self._start_proxy_and_wait()
            
            # 2. Start LLM workers
            await self._start_llm_workers()
            
            # 3. Start file watcher to feed the queue
            await self._start_file_watcher()
            
            # 4. Start browser with proxy
            await self._start_browser()
            
            # 5. Show instructions and keep running
            await self._run_live_monitoring()
            
        except KeyboardInterrupt:
            print("\nStopping Vulna Pentest AI...")
        finally:
            await self._cleanup()
    
    async def _start_proxy_and_wait(self):
        print("Starting mitmproxy interceptor...")
        
        def start_mitm():
            cmd = ["mitmdump", "-s", "backend/proxy/addon.py", "--listen-port", "8080"]
            self.proxy_process = subprocess.Popen(cmd, 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        
        threading.Thread(target=start_mitm, daemon=True).start()
        
        # Wait for proxy to be ready by testing HTTP connection
        print("Waiting for proxy to be ready...")
        
        for i in range(15):  # Try for 15 seconds
            try:
                import requests
                # Test proxy by making a request through it
                proxies = {"http": "http://localhost:8080", "https": "http://localhost:8080"}
                response = requests.get('http://httpbin.org/ip', 
                                     proxies=proxies, timeout=3)
                if response.status_code == 200:
                    print("✅ mitmproxy is ready and working!")
                    return
                    
            except Exception as e:
                print(f"   Proxy check {i+1}/15 - {type(e).__name__}")
            
            await asyncio.sleep(1)
        
        print("⚠️  Proxy readiness uncertain, but continuing...")
    
    async def _start_llm_workers(self):
        """Start LLM workers for processing captured traffic."""
        try:
            print("🤖 Starting LLM workers...")
            self.llm_workers = await self.llm_worker.start_workers(
                self.queue.queue, 
                "data/findings.jsonl"
            )
            print("✅ LLM workers ready for AI analysis!")
        except Exception as e:
            print(f"⚠️  LLM workers failed to start: {e}")
            print("   (Install Ollama: https://ollama.ai)")
            print("   (Run: ollama run llama3.2)")
    
    async def _start_file_watcher(self):
        """Start file watcher to monitor requests and feed the queue."""
        print("📁 Starting file watcher...")
        self.file_watcher = FileWatcher("data/requests.jsonl", self.queue)
        await self.file_watcher.start()
        print("✅ File watcher monitoring proxy requests")
    
    async def _start_browser(self):
        print("Starting browser with proxy...")
        
        playwright = await async_playwright().start()
        
        self.browser = await playwright.chromium.launch(
            headless=False,
            proxy={"server": "http://localhost:8080"},
            args=["--ignore-certificate-errors", "--disable-web-security"]
        )
        
        context = await self.browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        
        try:
            await page.goto("http://httpbin.org/", timeout=10000)
            print("Browser started and ready!")
            print("Start browsing - all traffic is being analyzed!")
        except Exception as e:
            print(f"Browser started but couldn't load test page: {e}")
            print("You can still browse manually - traffic will be captured!")
    
    async def _run_live_monitoring(self):
        print("\n" + "=" * 50)
        print("VULNA IS LIVE - Start browsing!")
        print("=" * 50)
        print("📊 Stats will be shown every 5 seconds")
        print("📁 All requests saved to: data/requests.jsonl")
        print("🔍 AI findings saved to: data/findings.jsonl")
        print("❌ Press Ctrl+C to stop")
        print("=" * 50)
        
        start_time = time.time()
        
        while True:
            await asyncio.sleep(5)
            
            # Show stats
            runtime = time.time() - start_time
            print(f"\n⏱️  Runtime: {runtime:.0f}s")
            
            # Check requests file
            requests_file = Path("data/requests.jsonl")
            findings_file = Path("data/findings.jsonl")
            
            if requests_file.exists():
                with open(requests_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    print(f"📋 Total requests captured: {len(lines)}")
                    
                    if lines:
                        # Show last request
                        try:
                            import json
                            last_request = json.loads(lines[-1])
                            print(f"📝 Last: {last_request.get('method', '')} {last_request.get('url', '')}")
                        except:
                            pass
            else:
                print("📋 No requests captured yet")
            
            # Queue stats
            queue_stats = self.queue.get_stats()
            print(f"📊 Queue: {queue_stats['current_size']} items pending")
            
            # LLM worker stats
            llm_stats = self.llm_worker.get_stats()
            print(f"🤖 AI Analysis: {llm_stats['processed_count']} completed, {llm_stats['error_count']} errors")
            
            # Findings count
            if findings_file.exists():
                with open(findings_file, 'r', encoding='utf-8') as f:
                    findings_count = len(f.readlines())
                    print(f"🔍 Vulnerabilities found: {findings_count}")
            
            print("🌐 Browse any website - AI analysis is running!")
            
    async def _cleanup(self):
        print("Cleaning up...")
        
        # Cancel LLM workers
        for worker in self.llm_workers:
            worker.cancel()
        
        # Stop file watcher
        if self.file_watcher:
            await self.file_watcher.stop()
        
        if self.browser:
            await self.browser.close()
        
        if self.proxy_process:
            self.proxy_process.terminate()
        
        print("Cleanup completed")
        print("📁 Check data/requests.jsonl for captured traffic")
        print("🔍 Check data/findings.jsonl for vulnerabilities")


async def main():
    """Main application entry point."""
    app = VulnaPentestAI()
    await app.start()


if __name__ == "__main__":
    asyncio.run(main())
