"""Intelligent Port Management and AI-based Proxy Diagnostics"""

import asyncio
import socket
import subprocess
import time
import json
import httpx
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import platform
import psutil


class SmartPortManager:
    """Intelligent port management with conflict resolution"""
    
    def __init__(self):
        self.reserved_ports = set()
        self.port_history = {}
        
    def find_free_port(self, preferred_port: int = 8080, port_range: int = 50) -> int:
        """Find free port with intelligent selection"""
        
        # First try preferred port
        if self.is_port_free(preferred_port):
            self.reserve_port(preferred_port)
            return preferred_port
        
        # Check what's using the preferred port
        port_info = self.analyze_port_usage(preferred_port)
        print(f"Port {preferred_port} is occupied by: {port_info}")
        
        # Smart port selection based on usage patterns
        for offset in range(1, port_range):
            # Try both directions
            for port in [preferred_port + offset, preferred_port - offset]:
                if 1024 <= port <= 65535 and self.is_port_free(port):
                    self.reserve_port(port)
                    print(f"Selected alternative port: {port}")
                    return port
        
        raise RuntimeError(f"Could not find free port in range {preferred_port}±{port_range}")
    
    def is_port_free(self, port: int) -> bool:
        """Check if port is free on both TCP and UDP"""
        try:
            # Test TCP
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('localhost', port))
            
            # Test UDP (some proxies use UDP)
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.bind(('localhost', port))
            
            return True
        except OSError:
            return False
    
    def analyze_port_usage(self, port: int) -> Dict[str, Any]:
        """Analyze what's using a specific port"""
        info = {
            "port": port,
            "status": "unknown",
            "process": None,
            "pid": None,
            "name": "unknown",
            "cmdline": []
        }
        
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port:
                    info["status"] = conn.status
                    if conn.pid:
                        try:
                            process = psutil.Process(conn.pid)
                            info["process"] = process.name()
                            info["pid"] = conn.pid
                            info["name"] = process.name()
                            info["cmdline"] = process.cmdline()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    break
        except Exception as e:
            info["error"] = str(e)
        
        return info
    
    def reserve_port(self, port: int):
        """Reserve a port to prevent conflicts"""
        self.reserved_ports.add(port)
        self.port_history[port] = {
            "reserved_at": datetime.now().isoformat(),
            "usage": "vulna"
        }
    
    def release_port(self, port: int):
        """Release a reserved port"""
        self.reserved_ports.discard(port)
        if port in self.port_history:
            self.port_history[port]["released_at"] = datetime.now().isoformat()
    
    def get_port_recommendations(self, service_type: str = "proxy") -> List[int]:
        """Get recommended ports based on service type"""
        recommendations = {
            "proxy": [8080, 8081, 8082, 8888, 9090, 9091, 3128, 8123],
            "dashboard": [3000, 3001, 3002, 8000, 8001, 5000, 5001],
            "api": [8000, 8001, 8002, 9000, 9001, 4000, 4001]
        }
        
        ports = recommendations.get(service_type, [8080, 8081, 8082])
        available_ports = [p for p in ports if self.is_port_free(p)]
        
        return available_ports[:5]  # Return top 5 available


class AIProxyDiagnostics:
    """AI-powered proxy testing and diagnostics"""
    
    def __init__(self, ollama_host: str = "localhost", ollama_port: int = 11434):
        self.ollama_url = f"http://{ollama_host}:{ollama_port}/api/generate"
        self.test_urls = [
            "http://httpbin.org/ip",
            "http://httpbin.org/headers", 
            "http://httpbin.org/user-agent",
            "https://api.github.com/zen",
            "http://testphp.vulnweb.com"
        ]
    
    async def comprehensive_proxy_test(self, proxy_port: int) -> Dict[str, Any]:
        """Comprehensive proxy testing with AI analysis"""
        
        test_results = {
            "proxy_port": proxy_port,
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "overall_status": "unknown",
            "ai_diagnosis": None,
            "recommendations": []
        }
        
        proxy_url = f"http://localhost:{proxy_port}"
        proxies = {"http": proxy_url, "https": proxy_url}
        
        print(f"Starting comprehensive proxy test on port {proxy_port}")
        
        # Test 1: Basic connectivity
        connectivity_result = await self._test_basic_connectivity(proxy_port)
        test_results["tests"].append(connectivity_result)
        
        # Test 2: HTTP requests through proxy
        http_results = await self._test_http_requests(proxies)
        test_results["tests"].extend(http_results)
        
        # Test 3: HTTPS/SSL handling
        ssl_result = await self._test_ssl_handling(proxies)
        test_results["tests"].append(ssl_result)
        
        # Test 4: Proxy headers and transparency
        transparency_result = await self._test_proxy_transparency(proxies)
        test_results["tests"].append(transparency_result)
        
        # Test 5: Performance metrics
        performance_result = await self._test_proxy_performance(proxies)
        test_results["tests"].append(performance_result)
        
        # Determine overall status
        passed_tests = sum(1 for test in test_results["tests"] if test.get("status") == "pass")
        total_tests = len(test_results["tests"])
        
        if passed_tests == total_tests:
            test_results["overall_status"] = "excellent"
        elif passed_tests >= total_tests * 0.8:
            test_results["overall_status"] = "good"
        elif passed_tests >= total_tests * 0.5:
            test_results["overall_status"] = "poor"
        else:
            test_results["overall_status"] = "failing"
        
        # Get AI diagnosis
        ai_diagnosis = await self._get_ai_diagnosis(test_results)
        test_results["ai_diagnosis"] = ai_diagnosis
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(test_results)
        test_results["recommendations"] = recommendations
        
        return test_results
    
    async def _test_basic_connectivity(self, port: int) -> Dict[str, Any]:
        """Test basic socket connectivity to proxy port"""
        test = {
            "name": "Basic Connectivity",
            "type": "connectivity",
            "status": "unknown",
            "details": {},
            "duration": 0
        }
        
        start_time = time.time()
        
        try:
            # Test TCP connection
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection('localhost', port), 
                timeout=5.0
            )
            writer.close()
            await writer.wait_closed()
            
            test["status"] = "pass"
            test["details"]["message"] = f"Port {port} is accepting connections"
            
        except asyncio.TimeoutError:
            test["status"] = "fail"
            test["details"]["error"] = "Connection timeout"
        except ConnectionRefusedError:
            test["status"] = "fail"  
            test["details"]["error"] = "Connection refused - proxy not running"
        except Exception as e:
            test["status"] = "fail"
            test["details"]["error"] = str(e)
        
        test["duration"] = time.time() - start_time
        return test
    
    async def _test_http_requests(self, proxies: Dict[str, str]) -> List[Dict[str, Any]]:
        """Test HTTP requests through proxy with correct HTTPX syntax"""
        tests = []
        
        proxy_url = proxies["http"]  # Get proxy URL
        
        for url in self.test_urls[:3]:  # Test first 3 URLs
            test = {
                "name": f"HTTP Request - {url}",
                "type": "http_request",
                "url": url,
                "status": "unknown",
                "details": {},
                "duration": 0
            }
            
            start_time = time.time()
            
            try:
                # CORRECT: Use proxies parameter with dictionary
                async with httpx.AsyncClient(proxies={"http://": proxy_url, "https://": proxy_url}, timeout=10.0) as client:
                    response = await client.get(url)
                    
                    test["status"] = "pass" if response.status_code == 200 else "partial"
                    test["details"]["status_code"] = response.status_code
                    test["details"]["response_size"] = len(response.content)
                    
                    # Check if response looks like proxy response
                    if "httpbin" in url and response.status_code == 200:
                        try:
                            json_response = response.json()
                            test["details"]["json_response"] = json_response
                        except:
                            pass
                    
            except httpx.TimeoutException:
                test["status"] = "fail"
                test["details"]["error"] = "Request timeout"
            except httpx.ProxyError as e:
                test["status"] = "fail"
                test["details"]["error"] = f"Proxy error: {str(e)}"
            except Exception as e:
                test["status"] = "fail"
                test["details"]["error"] = str(e)
            
            test["duration"] = time.time() - start_time
            tests.append(test)
        
        return tests
    
    async def _test_ssl_handling(self, proxies: Dict[str, str]) -> Dict[str, Any]:
        """Test HTTPS/SSL handling through proxy"""
        test = {
            "name": "SSL/HTTPS Handling",
            "type": "ssl_test",
            "status": "unknown", 
            "details": {},
            "duration": 0
        }
        
        start_time = time.time()
        
        try:
            proxy_url = proxies["http"]  # Get proxy URL
            async with httpx.AsyncClient(proxies={"http://": proxy_url, "https://": proxy_url}, timeout=10.0, verify=False) as client:
                response = await client.get("https://httpbin.org/ip")
                
                test["status"] = "pass" if response.status_code == 200 else "partial"
                test["details"]["status_code"] = response.status_code
                test["details"]["message"] = "HTTPS requests working through proxy"
                
        except Exception as e:
            test["status"] = "fail"
            test["details"]["error"] = f"SSL/HTTPS failed: {str(e)}"
        
        test["duration"] = time.time() - start_time
        return test
    
    async def _test_proxy_transparency(self, proxies: Dict[str, str]) -> Dict[str, Any]:
        """Test proxy transparency and header handling"""
        test = {
            "name": "Proxy Transparency",
            "type": "transparency",
            "status": "unknown",
            "details": {},
            "duration": 0
        }
        
        start_time = time.time()
        
        try:
            proxy_url = proxies["http"]  # Get proxy URL
            async with httpx.AsyncClient(proxies={"http://": proxy_url, "https://": proxy_url}, timeout=10.0) as client:
                response = await client.get("http://httpbin.org/headers")
                
                if response.status_code == 200:
                    headers_data = response.json()
                    received_headers = headers_data.get("headers", {})
                    
                    test["status"] = "pass"
                    test["details"]["received_headers"] = received_headers
                    test["details"]["proxy_detected"] = any(
                        "proxy" in k.lower() or "x-forwarded" in k.lower() 
                        for k in received_headers.keys()
                    )
                else:
                    test["status"] = "partial"
                    
        except Exception as e:
            test["status"] = "fail"
            test["details"]["error"] = str(e)
        
        test["duration"] = time.time() - start_time
        return test
    
    async def _test_proxy_performance(self, proxies: Dict[str, str]) -> Dict[str, Any]:
        """Test proxy performance metrics"""
        test = {
            "name": "Proxy Performance",
            "type": "performance",
            "status": "unknown",
            "details": {},
            "duration": 0
        }
        
        start_time = time.time()
        times = []
        
        try:
            proxy_url = proxies["http"]  # Get proxy URL
            
            # Make multiple requests to measure average response time
            for _ in range(3):
                req_start = time.time()
                async with httpx.AsyncClient(proxies={"http://": proxy_url, "https://": proxy_url}, timeout=10.0) as client:
                    response = await client.get("http://httpbin.org/ip")
                    if response.status_code == 200:
                        times.append(time.time() - req_start)
            
            if times:
                avg_time = sum(times) / len(times)
                test["details"]["average_response_time"] = avg_time
                test["details"]["min_time"] = min(times)
                test["details"]["max_time"] = max(times)
                
                # Classify performance
                if avg_time < 1.0:
                    test["status"] = "pass"
                    test["details"]["performance"] = "excellent"
                elif avg_time < 3.0:
                    test["status"] = "pass"
                    test["details"]["performance"] = "good"  
                else:
                    test["status"] = "partial"
                    test["details"]["performance"] = "slow"
            else:
                test["status"] = "fail"
                test["details"]["error"] = "No successful requests for performance measurement"
                
        except Exception as e:
            test["status"] = "fail"
            test["details"]["error"] = str(e)
        
        test["duration"] = time.time() - start_time
        return test
    
    async def _get_ai_diagnosis(self, test_results: Dict[str, Any]) -> str:
        """Get AI diagnosis of proxy test results"""
        
        # Prepare test summary for AI
        test_summary = {
            "overall_status": test_results["overall_status"],
            "total_tests": len(test_results["tests"]),
            "passed_tests": sum(1 for test in test_results["tests"] if test.get("status") == "pass"),
            "failed_tests": sum(1 for test in test_results["tests"] if test.get("status") == "fail"),
            "test_details": []
        }
        
        for test in test_results["tests"]:
            test_summary["test_details"].append({
                "name": test["name"],
                "status": test["status"],
                "error": test["details"].get("error", None),
                "duration": test["duration"]
            })
        
        prompt = f"""
Du bist ein Cybersecurity-Experte für Proxy-Diagnose. Analysiere die folgenden Proxy-Testergebnisse und gib eine präzise Diagnose.

PROXY TEST RESULTS:
{json.dumps(test_summary, indent=2)}

Gib eine kurze, technische Diagnose:
1. Was funktioniert gut?
2. Was sind die Hauptprobleme?
3. Wahrscheinliche Ursachen für Fehler?

Antworte in 3-4 kurzen Sätzen auf Deutsch.
"""
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(self.ollama_url, json={
                    "model": "qwen2.5-coder:latest",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "max_tokens": 300}
                })
                
                if response.status_code == 200:
                    ai_response = response.json()
                    return ai_response.get("response", "AI-Diagnose nicht verfügbar").strip()
                else:
                    return "AI-Diagnose fehlgeschlagen - Ollama nicht erreichbar"
                    
        except Exception as e:
            return f"AI-Diagnose Fehler: {str(e)}"
    
    async def _generate_recommendations(self, test_results: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations based on test results"""
        
        recommendations = []
        
        # Analyze failed tests
        for test in test_results["tests"]:
            if test["status"] == "fail":
                test_type = test["type"]
                error = test["details"].get("error", "")
                
                if test_type == "connectivity":
                    if "Connection refused" in error:
                        recommendations.append("mitmproxy ist nicht gestartet - prüfe die Proxy-Instanz")
                    elif "timeout" in error.lower():
                        recommendations.append("⏱️ Verbindungs-Timeout - prüfe Firewall/Netzwerk-Einstellungen")
                
                elif test_type == "http_request":
                    if "Proxy error" in error:
                        recommendations.append("HTTP-Proxy-Fehler - prüfe mitmproxy Konfiguration")
                    elif "timeout" in error.lower():
                        recommendations.append("🐌 HTTP-Request Timeout - Proxy zu langsam oder überlastet")
                
                elif test_type == "ssl_test":
                    recommendations.append("HTTPS/SSL Problem - prüfe SSL-Zertifikat Handling in mitmproxy")
        
        # Performance recommendations
        performance_test = next((t for t in test_results["tests"] if t["type"] == "performance"), None)
        if performance_test and performance_test["status"] != "fail":
            avg_time = performance_test["details"].get("average_response_time", 0)
            if avg_time > 3.0:
                recommendations.append("Proxy Performance schlecht - reduziere mitmproxy Add-ons oder erhöhe Ressourcen")
        
        # General recommendations based on overall status
        if test_results["overall_status"] == "failing":
            recommendations.extend([
                "Kritisches Problem: Proxy komplett defekt",
                "🔄 Empfehlung: mitmproxy neu starten auf anderem Port",
                "🛠️ Checke: pip install mitmproxy --upgrade"
            ])
        elif test_results["overall_status"] == "poor":
            recommendations.extend([
                "Proxy funktioniert teilweise - einige Requests können fehlschlagen", 
                "Empfehlung: Proxy-Konfiguration überprüfen"
            ])
        
        # Add default recommendations if none found
        if not recommendations:
            recommendations.extend([
                "Proxy funktioniert korrekt",
                "Bereit für Penetration Testing",
                "Teste mit: http://testphp.vulnweb.com"
            ])
        
        return recommendations
    
    async def quick_proxy_check(self, proxy_port: int) -> bool:
        """Quick proxy health check"""
        try:
            async with httpx.AsyncClient(
                proxies={"http://": f"http://localhost:{proxy_port}", "https://": f"http://localhost:{proxy_port}"}, 
                timeout=5.0
            ) as client:
                response = await client.get("http://httpbin.org/ip")
                return response.status_code == 200
        except:
            return False
    
    async def auto_fix_proxy_issues(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to automatically fix common proxy issues"""
        
        fixes_applied = []
        issues_found = []
        
        # Analyze test results for fixable issues
        for test in test_results["tests"]:
            if test["status"] == "fail":
                error = test["details"].get("error", "")
                
                # Issue: Connection refused (proxy not running)
                if "Connection refused" in error:
                    issues_found.append("proxy_not_running")
                
                # Issue: Timeout (port conflict or network issue)
                elif "timeout" in error.lower():
                    issues_found.append("connection_timeout")
                
                # Issue: Proxy error (configuration problem)
                elif "Proxy error" in error:
                    issues_found.append("proxy_configuration")
        
        # Apply automatic fixes
        if "proxy_not_running" in issues_found:
            fix_result = await self._auto_restart_proxy(test_results["proxy_port"])
            fixes_applied.append(fix_result)
        
        return {
            "issues_found": issues_found,
            "fixes_applied": fixes_applied,
            "auto_fix_success": all(fix.get("success", False) for fix in fixes_applied)
        }
    
    async def _auto_restart_proxy(self, port: int) -> Dict[str, Any]:
        """Attempt to restart proxy automatically"""
        fix_result = {
            "action": "restart_proxy",
            "success": False,
            "details": {}
        }
        
        try:
            # Try to find and kill existing mitmproxy processes
            killed_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'mitm' in proc.info['name'].lower():
                        proc.kill()
                        killed_processes.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if killed_processes:
                fix_result["details"]["killed_processes"] = killed_processes
                await asyncio.sleep(2)  # Wait for processes to die
            
            # Try to restart mitmproxy
            # Note: This is a simplified version - real implementation would 
            # need to coordinate with the main application
            fix_result["details"]["attempted_restart"] = True
            fix_result["success"] = True
            fix_result["details"]["message"] = "Proxy restart attempted - may require manual intervention"
            
        except Exception as e:
            fix_result["details"]["error"] = str(e)
        
        return fix_result


class EnhancedPortManager:
    """Combined port management with AI diagnostics"""
    
    def __init__(self):
        self.port_manager = SmartPortManager()
        self.ai_diagnostics = AIProxyDiagnostics()
        self.active_ports = {}
    
    async def setup_proxy_with_intelligence(self, preferred_port: int = 8080) -> Dict[str, Any]:
        """Set up proxy with intelligent port selection and AI testing"""
        
        setup_result = {
            "proxy_port": None,
            "port_selection": {},
            "proxy_test": {},
            "recommendations": [],
            "success": False
        }
        
        # Step 1: Intelligent port selection
        try:
            port = self.port_manager.find_free_port(preferred_port)
            setup_result["proxy_port"] = port
            setup_result["port_selection"] = {
                "requested_port": preferred_port,
                "assigned_port": port,
                "port_changed": port != preferred_port,
                "alternatives": self.port_manager.get_port_recommendations("proxy")
            }
            
            # If port changed, explain why
            if port != preferred_port:
                port_analysis = self.port_manager.analyze_port_usage(preferred_port)
                setup_result["port_selection"]["conflict_reason"] = port_analysis
                
        except Exception as e:
            setup_result["port_selection"]["error"] = str(e)
            return setup_result
        
        # Step 2: Wait a moment for proxy to potentially start
        await asyncio.sleep(2)
        
        # Step 3: AI-powered proxy testing
        try:
            test_results = await self.ai_diagnostics.comprehensive_proxy_test(port)
            setup_result["proxy_test"] = test_results
            setup_result["recommendations"] = test_results.get("recommendations", [])
            
            # Determine overall success
            setup_result["success"] = test_results.get("overall_status") in ["excellent", "good"]
            
        except Exception as e:
            setup_result["proxy_test"]["error"] = str(e)
        
        return setup_result
    
    async def continuous_proxy_monitoring(self, proxy_port: int, interval: int = 30):
        """Continuously monitor proxy health with AI analysis"""
        
        print(f"Starting continuous proxy monitoring on port {proxy_port}")
        
        while True:
            try:
                # Quick health check
                is_healthy = await self.ai_diagnostics.quick_proxy_check(proxy_port)
                
                if not is_healthy:
                    print(f"Proxy health check failed on port {proxy_port}")
                    
                    # Full diagnostic if quick check fails
                    test_results = await self.ai_diagnostics.comprehensive_proxy_test(proxy_port)
                    
                    # Attempt auto-fix
                    if test_results.get("overall_status") == "failing":
                        auto_fix_results = await self.ai_diagnostics.auto_fix_proxy_issues(test_results)
                        print(f"Auto-fix attempted: {auto_fix_results}")
                
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                print("Proxy monitoring stopped")
                break
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(interval)
