"""Enhanced LLM Worker with AI-powered filtering and automated vulnerability testing."""

import asyncio, json, time, uuid
from datetime import datetime
from typing import Optional, Dict, Any
import httpx
from backend.models.findings import QueueItem, VulnerabilityFinding, RiskLevel
from backend.llm.prompts import create_analysis_prompt, get_system_prompt
from backend.utils.url_filter import should_analyze_url, categorize_url
from backend.utils.request_analyzer import RequestAnalyzer
from backend.utils.ai_smart_filter import AISmartFilter
from backend.utils.vulnerability_tester import VulnerabilityTester


class OllamaLLMWorker:
    """Enhanced worker with AI-powered filtering and automated vulnerability testing."""
    
    def __init__(self, ollama_host: str = "localhost", ollama_port: int = 11434, 
                 model_name: str = "qwen2.5-coder:14b", max_workers: int = 3):
        self.ollama_url = f"http://{ollama_host}:{ollama_port}/api/generate"
        self.model_name = model_name
        self.max_workers = max_workers
        self.processed_count = 0
        self.error_count = 0
        self.filtered_count = 0
        self.processing_times = []
        
        # Initialize AI-powered systems
        self.request_analyzer = RequestAnalyzer()
        self.ai_smart_filter = AISmartFilter(ollama_host, ollama_port)
        self.vulnerability_tester = VulnerabilityTester(ollama_host, ollama_port)
        
        # Enhanced analysis type counters
        self.analysis_stats = {
            "ai_deep_analysis": 0,
            "ai_standard_analysis": 0,
            "pattern_matching": 0,
            "ai_filtered": 0,
            "vulnerability_tests": 0,
            "verified_vulnerabilities": 0,
            "false_positives": 0,
            "skip": 0
        }
        
    async def start_workers(self, queue: asyncio.Queue, output_file: str = "data/findings.jsonl"):
        """Start multiple worker tasks for processing queue items."""
        workers = []
        
        for i in range(self.max_workers):
            worker = asyncio.create_task(
                self._worker_loop(queue, output_file, worker_id=i)
            )
            workers.append(worker)
            
        print(f"Started {self.max_workers} LLM workers with AI-powered filtering and auto-testing")
        return workers
        
    async def _worker_loop(self, queue: asyncio.Queue, output_file: str, worker_id: int):
        """Enhanced worker loop with AI filtering and vulnerability testing."""
        while True:
            try:
                queue_item = await asyncio.wait_for(queue.get(), timeout=1.0)
                
                # Get request details
                request = queue_item.request
                method_str = request.method.value if hasattr(request.method, 'value') else str(request.method)
                
                # AI-powered smart filtering (FIRST STAGE)
                ai_filter_result = await self.ai_smart_filter.should_analyze_url(
                    request.url, method_str, dict(request.headers)
                )
                
                print(f"Worker {worker_id}: AI Filter -> {ai_filter_result['decision']} | {ai_filter_result['reasoning']}")
                
                if ai_filter_result["decision"] == "FILTER":
                    self.filtered_count += 1
                    self.analysis_stats["ai_filtered"] += 1
                    print(f"Worker {worker_id}: AI-FILTERED {method_str} {request.url} | {ai_filter_result['category']}")
                    queue.task_done()
                    continue
                
                # Function calling analysis (SECOND STAGE)
                analysis = self.request_analyzer.analyze_request_context(
                    method=method_str,
                    url=request.url,
                    headers=dict(request.headers),
                    body=request.body
                )
                
                # Enhanced logging
                summary = self.request_analyzer.get_analysis_summary(analysis)
                print(f"Worker {worker_id}: {summary} | AI-Value: {ai_filter_result['pentesting_value']}")
                
                # Update stats
                self.analysis_stats[analysis["analysis_type"]] += 1
                
                if not analysis["should_analyze"]:
                    self.filtered_count += 1
                    queue.task_done()
                    continue
                
                print(f"Worker {worker_id}: ANALYZING {method_str} {request.url} - {analysis['analysis_type']}")
                
                start_time = time.time()
                
                # Analyze based on determined type
                if analysis["analysis_type"] == "ai_deep_analysis":
                    finding = await self._ai_deep_analysis(queue_item, analysis)
                elif analysis["analysis_type"] == "ai_standard_analysis":
                    finding = await self._ai_standard_analysis(queue_item, analysis)
                elif analysis["analysis_type"] == "pattern_matching":
                    finding = await self._pattern_matching_analysis(queue_item, analysis)
                else:
                    queue.task_done()
                    continue
                
                # AUTOMATIC VULNERABILITY TESTING (NEW!)
                if finding.risk_level.value in ["HIGH", "CRITICAL", "MEDIUM"]:
                    print(f"Worker {worker_id}: AUTO-TESTING vulnerability: {finding.title}")
                    test_result = await self.vulnerability_tester.test_vulnerability(finding.model_dump())
                    
                    # Update stats
                    self.analysis_stats["vulnerability_tests"] += 1
                    if test_result.get("verified", False):
                        self.analysis_stats["verified_vulnerabilities"] += 1
                        finding.confidence = min(finding.confidence + 0.3, 1.0)  # Boost confidence
                        print(f"Worker {worker_id}: VERIFIED! {finding.title}")
                    else:
                        self.analysis_stats["false_positives"] += 1
                        finding.confidence = max(finding.confidence - 0.2, 0.1)  # Reduce confidence
                        print(f"Worker {worker_id}: FALSE POSITIVE: {finding.title}")
                    
                    # Add test results to finding
                    finding_dict = finding.model_dump()
                    finding_dict["auto_test_result"] = test_result
                    finding = VulnerabilityFinding(**finding_dict)
                
                # Enhance finding with analysis context
                enhanced_finding = self._enhance_finding(finding, queue_item, analysis, ai_filter_result)
                
                # Save to file
                await self._save_finding(enhanced_finding, output_file)
                
                processing_time = time.time() - start_time
                self.processing_times.append(processing_time)
                self.processed_count += 1
                
                print(f"Worker {worker_id}: Processed {queue_item.id[:8]} in {processing_time:.2f}s")
                queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.error_count += 1
                print(f"Worker {worker_id} error: {e}")
                try:
                    queue.task_done()
                except:
                    pass

    def _enhance_finding(self, finding: VulnerabilityFinding, queue_item: QueueItem, analysis: Dict, ai_filter_result: Dict) -> VulnerabilityFinding:
        """Enhance finding with complete context including AI filtering results."""
        
        request = queue_item.request
        response = queue_item.response
        
        # Get existing finding data
        finding_data = finding.model_dump()
        
        # Add request context
        finding_data.update({
            "id": str(uuid.uuid4()),
            "affected_url": request.url,
            "request_method": request.method.value if hasattr(request.method, 'value') else str(request.method),
            "request_headers": dict(request.headers),
            "request_body": request.body,
            "url_category": categorize_url(request.url, finding_data.get("request_method", "GET")),
            "related_request_ids": [queue_item.id],
            
            # Add enhanced analysis context
            "analysis_type": analysis["analysis_type"],
            "priority_score": analysis["priority_score"],
            "security_indicators": analysis["security_indicators"],
            "function_calls": analysis["function_calls"],
            
            # Add AI filtering context
            "ai_filter_decision": ai_filter_result["decision"],
            "ai_filter_confidence": ai_filter_result["confidence"],
            "ai_filter_reasoning": ai_filter_result["reasoning"],
            "ai_filter_category": ai_filter_result["category"],
            "pentesting_value": ai_filter_result["pentesting_value"]
        })
        
        # Add response context if available
        if response:
            finding_data.update({
                "response_status": response.status_code,
                "response_headers": dict(response.headers),
                "response_body": response.body[:1000] if response.body else None
            })
        
        return VulnerabilityFinding(**finding_data)

    async def _ai_deep_analysis(self, queue_item: QueueItem, analysis: Dict) -> VulnerabilityFinding:
        """Full AI analysis for high-priority requests"""
        return await self._analyze_request(queue_item, enhanced_prompt=True)
    
    async def _ai_standard_analysis(self, queue_item: QueueItem, analysis: Dict) -> VulnerabilityFinding:
        """Standard AI analysis for medium-priority requests"""
        return await self._analyze_request(queue_item, enhanced_prompt=False)
    
    async def _pattern_matching_analysis(self, queue_item: QueueItem, analysis: Dict) -> VulnerabilityFinding:
        """Pattern-based analysis for low-priority requests (faster)"""
        request = queue_item.request
        
        # Simple pattern-based vulnerability detection
        vulnerabilities = []
        
        # SQL Injection patterns
        sql_patterns = ['union', 'select', 'drop', 'insert', 'delete', "'", '"', '--', '/*']
        content = f"{request.url} {request.body or ''}".lower()
        
        for pattern in sql_patterns:
            if pattern in content:
                vulnerabilities.append("Potential SQL Injection")
                break
        
        # XSS patterns
        xss_patterns = ['<script', 'javascript:', 'onerror=', 'onload=', 'alert(']
        for pattern in xss_patterns:
            if pattern in content:
                vulnerabilities.append("Potential XSS")
                break
        
        # Default low-risk finding
        title = vulnerabilities[0] if vulnerabilities else "Request analyzed (pattern matching)"
        description = f"Pattern-based analysis detected: {', '.join(vulnerabilities)}" if vulnerabilities else "No obvious patterns detected"
        
        return VulnerabilityFinding(
            id=queue_item.id,
            risk_score=2 if vulnerabilities else 1,
            risk_level=RiskLevel.MEDIUM if vulnerabilities else RiskLevel.INFO,
            owasp_categories=[],
            cwe_ids=[],
            title=title,
            description=description,
            suggestion="Review manually for actual vulnerabilities",
            confidence=0.3 if vulnerabilities else 0.1,
            affected_parameters=[],
            impact="",
            proof_of_concept="",
            exploitation_steps=[]
        )

    async def _analyze_request(self, queue_item: QueueItem, enhanced_prompt: bool = False) -> VulnerabilityFinding:
        """Analyze a request using Ollama LLM with optional enhanced prompting."""
        request = queue_item.request
        
        # Create prompt with method string conversion
        method_str = request.method.value if hasattr(request.method, 'value') else str(request.method)
        
        user_prompt = create_analysis_prompt(
            method=method_str,
            url=request.url,
            headers=request.headers,
            body=request.body
        )
        
        # Enhanced prompting for high-priority requests
        if enhanced_prompt:
            user_prompt += "\n\nIMPORTANT: This is a high-priority request. Perform deep analysis for:\n"
            user_prompt += "- Advanced injection techniques\n- Authentication bypass\n- Authorization issues\n"
            user_prompt += "- Business logic flaws\n- Rate limiting issues\n- Session management problems"
        
        # Call Ollama API
        async with httpx.AsyncClient(timeout=45.0 if enhanced_prompt else 30.0) as client:
            ollama_payload = {
                "model": self.model_name,
                "prompt": user_prompt,
                "system": get_system_prompt(),
                "stream": False,
                "format": "json"
            }
            
            response = await client.post(self.ollama_url, json=ollama_payload)
            response.raise_for_status()
            
            result = response.json()
            llm_response = result.get("response", "")
            
            # Parse JSON response
            try:
                analysis = json.loads(llm_response)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                analysis = {
                    "risk_score": 1,
                    "risk_level": "INFO",
                    "title": "Analysis Error",
                    "description": "Failed to parse LLM response",
                    "suggestion": "Check LLM output format",
                    "confidence": 0.1
                }
            
            # Create VulnerabilityFinding with safe defaults
            finding = VulnerabilityFinding(
                id=queue_item.id,
                risk_score=analysis.get("risk_score", 0),
                risk_level=RiskLevel(analysis.get("risk_level", "INFO")),
                owasp_categories=analysis.get("owasp_categories", []),
                cwe_ids=analysis.get("cwe_ids", []),
                title=analysis.get("title", "Unknown vulnerability"),
                description=analysis.get("description", "No description"),
                suggestion=analysis.get("suggestion", "No suggestion"),
                confidence=analysis.get("confidence", 0.5),
                
                # Enhanced fields with defaults
                affected_parameters=analysis.get("affected_parameters", []),
                impact=analysis.get("impact", ""),
                proof_of_concept=analysis.get("proof_of_concept", ""),
                exploitation_steps=analysis.get("exploitation_steps", [])
            )
            
            return finding
    
    async def _save_finding(self, finding: VulnerabilityFinding, output_file: str):
        """Save finding to JSONL file."""
        import aiofiles
        
        async with aiofiles.open(output_file, "a", encoding="utf-8") as f:
            await f.write(finding.model_dump_json() + "\n")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get enhanced worker statistics including AI filtering and testing."""
        avg_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        
        # Get AI filter stats
        ai_filter_stats = self.ai_smart_filter.get_filter_stats()
        vuln_test_stats = self.vulnerability_tester.get_test_results()
        
        return {
            "processed_count": self.processed_count,
            "error_count": self.error_count,
            "filtered_count": self.filtered_count,
            "average_processing_time": avg_time,
            "total_processing_time": sum(self.processing_times),
            "analysis_stats": self.analysis_stats,
            "ai_filter_stats": ai_filter_stats,
            "vulnerability_test_stats": vuln_test_stats,
            
            # Enhanced metrics
            "false_positive_rate": self.analysis_stats["false_positives"] / max(self.analysis_stats["vulnerability_tests"], 1),
            "verification_rate": self.analysis_stats["verified_vulnerabilities"] / max(self.analysis_stats["vulnerability_tests"], 1),
            "ai_filter_efficiency": ai_filter_stats.get("filtered_domains", 0) / max(ai_filter_stats.get("total_decisions", 1), 1)
        }
