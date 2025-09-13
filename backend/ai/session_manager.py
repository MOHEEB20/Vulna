"""Integrated AI Session Manager for Vulnerability Analysis"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import httpx


class VulnerabilityAISession:
    """AI Session für eine spezifische Vulnerability mit kompletter Nachverfolgung"""
    
    def __init__(self, vulnerability_id: str, vulnerability_data: Dict):
        self.session_id = str(uuid.uuid4())
        self.vulnerability_id = vulnerability_id
        self.vulnerability_data = vulnerability_data
        self.created_at = datetime.now().isoformat()
        
        # Session conversation history
        self.conversation_history: List[Dict] = []
        
        # AI action results
        self.ai_actions = {
            "poc_generation": None,
            "auto_test": None, 
            "exploitation_analysis": None,
            "chat_interactions": []
        }
        
        # Session status
        self.status = "active"
        self.last_activity = datetime.now().isoformat()
        
        # Initialize session with vulnerability context
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize session with vulnerability context"""
        context_message = {
            "role": "system",
            "content": f"""Du bist ein AI Security Analyst für Vulnerability Analysis Session.

VULNERABILITY CONTEXT:
- ID: {self.vulnerability_id}
- Title: {self.vulnerability_data.get('title', 'Unknown')}
- Risk Level: {self.vulnerability_data.get('risk_level', 'Unknown')}
- URL: {self.vulnerability_data.get('affected_url', 'Unknown')}
- Method: {self.vulnerability_data.get('request_method', 'Unknown')}

Du hilfst bei:
1. Proof of Concept Generation
2. Automatic Testing
3. Exploitation Analysis
4. Security Questions zu dieser Vulnerability

Behalte immer den Kontext dieser spezifischen Vulnerability im Gedächtnis.""",
            "timestamp": datetime.now().isoformat(),
            "action_type": "session_init"
        }
        
        self.conversation_history.append(context_message)
    
    async def generate_poc(self) -> Dict[str, Any]:
        """Generate Proof of Concept with session tracking"""
        try:
            poc_prompt = self._create_poc_prompt()
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": "Generate Proof of Concept for this vulnerability",
                "action_type": "poc_generation",
                "timestamp": datetime.now().isoformat()
            })
            
            # Call AI
            ai_response = await self._call_ollama_ai(poc_prompt)
            
            # Store result
            self.ai_actions["poc_generation"] = {
                "timestamp": datetime.now().isoformat(),
                "request": poc_prompt,
                "response": ai_response,
                "status": "completed"
            }
            
            # Add AI response to conversation
            self.conversation_history.append({
                "role": "assistant", 
                "content": ai_response,
                "action_type": "poc_generation",
                "timestamp": datetime.now().isoformat()
            })
            
            self._update_activity()
            
            return {
                "success": True,
                "session_id": self.session_id,
                "poc_content": ai_response,
                "action_type": "poc_generation"
            }
            
        except Exception as e:
            error_result = {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "failed"
            }
            self.ai_actions["poc_generation"] = error_result
            
            return {
                "success": False,
                "session_id": self.session_id, 
                "error": str(e)
            }
    
    async def auto_test(self) -> Dict[str, Any]:
        """Automatic testing with detailed tracking"""
        try:
            test_prompt = self._create_auto_test_prompt()
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": "Perform automatic vulnerability testing and analysis",
                "action_type": "auto_test",
                "timestamp": datetime.now().isoformat()
            })
            
            # Call AI
            ai_response = await self._call_ollama_ai(test_prompt)
            
            # Store result
            self.ai_actions["auto_test"] = {
                "timestamp": datetime.now().isoformat(),
                "request": test_prompt,
                "response": ai_response,
                "status": "completed"
            }
            
            # Add AI response to conversation
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_response, 
                "action_type": "auto_test",
                "timestamp": datetime.now().isoformat()
            })
            
            self._update_activity()
            
            return {
                "success": True,
                "session_id": self.session_id,
                "test_results": ai_response,
                "action_type": "auto_test"
            }
            
        except Exception as e:
            error_result = {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "failed"
            }
            self.ai_actions["auto_test"] = error_result
            
            return {
                "success": False,
                "session_id": self.session_id,
                "error": str(e)
            }
    
    async def exploitation_analysis(self) -> Dict[str, Any]:
        """Detailed exploitation analysis"""
        try:
            exploit_prompt = self._create_exploitation_prompt()
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": "Analyze exploitation techniques and methods",
                "action_type": "exploitation_analysis", 
                "timestamp": datetime.now().isoformat()
            })
            
            # Call AI
            ai_response = await self._call_ollama_ai(exploit_prompt)
            
            # Store result
            self.ai_actions["exploitation_analysis"] = {
                "timestamp": datetime.now().isoformat(),
                "request": exploit_prompt,
                "response": ai_response,
                "status": "completed"
            }
            
            # Add AI response to conversation
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_response,
                "action_type": "exploitation_analysis",
                "timestamp": datetime.now().isoformat()
            })
            
            self._update_activity()
            
            return {
                "success": True,
                "session_id": self.session_id,
                "exploitation_info": ai_response,
                "action_type": "exploitation_analysis"
            }
            
        except Exception as e:
            error_result = {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "failed"
            }
            self.ai_actions["exploitation_analysis"] = error_result
            
            return {
                "success": False,
                "session_id": self.session_id,
                "error": str(e)
            }

    async def chat_with_ai(self, user_message: str) -> Dict[str, Any]:
        """Interactive chat about the vulnerability"""
        try:
            # Create contextual chat prompt
            chat_prompt = f"""
PREVIOUS CONVERSATION CONTEXT:
{self._get_conversation_summary()}

USER QUESTION: {user_message}

Als AI Security Analyst, antworte auf die Frage im Kontext dieser Vulnerability:
- Title: {self.vulnerability_data.get('title', 'Unknown')}
- Risk Level: {self.vulnerability_data.get('risk_level', 'Unknown')}
- URL: {self.vulnerability_data.get('affected_url', 'Unknown')}

Gib eine hilfreiche, technische Antwort.
"""
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_message,
                "action_type": "chat",
                "timestamp": datetime.now().isoformat()
            })
            
            # Call AI
            ai_response = await self._call_ollama_ai(chat_prompt)
            
            # Add AI response to conversation
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_response,
                "action_type": "chat",
                "timestamp": datetime.now().isoformat()
            })
            
            # Store in chat interactions
            self.ai_actions["chat_interactions"].append({
                "user_message": user_message,
                "ai_response": ai_response,
                "timestamp": datetime.now().isoformat()
            })
            
            self._update_activity()
            
            return {
                "success": True,
                "session_id": self.session_id,
                "ai_response": ai_response,
                "action_type": "chat"
            }
            
        except Exception as e:
            return {
                "success": False,
                "session_id": self.session_id,
                "error": str(e)
            }

    def _create_poc_prompt(self) -> str:
        """Create detailed PoC generation prompt"""
        return f"""
GENERATE COMPREHENSIVE PROOF OF CONCEPT:

VULNERABILITY DETAILS:
- Title: {self.vulnerability_data.get('title', 'Unknown')}
- Risk Level: {self.vulnerability_data.get('risk_level', 'Unknown')}
- URL: {self.vulnerability_data.get('affected_url', 'Unknown')}
- Method: {self.vulnerability_data.get('request_method', 'Unknown')}
- Description: {self.vulnerability_data.get('description', 'No description')}

REQUEST DETAILS:
Headers: {json.dumps(self.vulnerability_data.get('request_headers', {}), indent=2)}
Body: {self.vulnerability_data.get('request_body', 'None')}

GENERATE:
1. Working curl command to reproduce this vulnerability
2. Step-by-step exploitation instructions
3. Expected response/behavior
4. Potential impact scenarios
5. Alternative attack vectors

Format as practical, executable commands with detailed explanations.
"""
    
    def _create_auto_test_prompt(self) -> str:
        """Create automatic testing prompt"""
        return f"""
AUTOMATIC VULNERABILITY TESTING ANALYSIS:

VULNERABILITY: {self.vulnerability_data.get('title', 'Unknown')}
RISK LEVEL: {self.vulnerability_data.get('risk_level', 'Unknown')}
URL: {self.vulnerability_data.get('affected_url', 'Unknown')}
METHOD: {self.vulnerability_data.get('request_method', 'Unknown')}

VULNERABILITY DETAILS:
Description: {self.vulnerability_data.get('description', 'No description')}
Confidence: {self.vulnerability_data.get('confidence', 'Unknown')}

REQUEST CONTEXT:
Headers: {json.dumps(self.vulnerability_data.get('request_headers', {}), indent=2)}
Body: {self.vulnerability_data.get('request_body', 'None')}

PERFORM COMPREHENSIVE AUTOMATED TESTING:

1. VULNERABILITY VALIDATION:
   - Confirm if this is actually exploitable
   - Check for false positive indicators
   - Rate exploitability (1-10)

2. ATTACK VECTORS:
   - List all possible attack methods
   - Identify payload variations
   - Check for bypass techniques

3. TESTING RESULTS:
   - What tests were successful
   - What failed and why
   - Risk assessment

Provide detailed results with success/failure status for each test.
"""

    def _create_exploitation_prompt(self) -> str:
        """Create exploitation analysis prompt"""
        return f"""
DETAILED EXPLOITATION ANALYSIS:

TARGET VULNERABILITY: {self.vulnerability_data.get('title', 'Unknown')}
RISK LEVEL: {self.vulnerability_data.get('risk_level', 'Unknown')}
TARGET URL: {self.vulnerability_data.get('affected_url', 'Unknown')}

ANALYZE:
1. EXPLOITATION TECHNIQUES:
   - Manual exploitation methods
   - Automated tools that could exploit this
   - Advanced techniques

2. PREREQUISITES:
   - What conditions are needed
   - Required access levels
   - Environmental factors

3. IMPACT ASSESSMENT:
   - What data could be accessed
   - System compromise potential
   - Business impact

4. DEFENSE BYPASS:
   - WAF bypass techniques
   - Evasion methods
   - Obfuscation strategies

5. REMEDIATION:
   - Immediate fixes
   - Long-term solutions
   - Prevention strategies

Provide detailed technical analysis with specific examples.
"""
    
    async def _call_ollama_ai(self, prompt: str) -> str:
        """Call Ollama AI with the prompt"""
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "qwen2.5-coder:latest",
                        "prompt": prompt,
                        "stream": False,
                        "system": "Du bist ein AI Security Expert für Penetration Testing."
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "AI response error")
                
        except Exception as e:
            return f"AI API Error: {str(e)}"
    
    def _get_conversation_summary(self) -> str:
        """Get summary of conversation for context"""
        summary_parts = []
        for msg in self.conversation_history[-5:]:  # Last 5 messages
            role = msg.get("role", "unknown")
            action = msg.get("action_type", "")
            content_preview = msg.get("content", "")[:100] + "..."
            summary_parts.append(f"{role} ({action}): {content_preview}")
        return "\n".join(summary_parts)
    
    def _update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now().isoformat()
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get complete session information"""
        return {
            "session_id": self.session_id,
            "vulnerability_id": self.vulnerability_id,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "status": self.status,
            "conversation_count": len(self.conversation_history),
            "ai_actions": self.ai_actions,
            "conversation_history": self.conversation_history
        }


class AISessionManager:
    """Manager für alle AI Sessions"""
    
    def __init__(self):
        self.active_sessions: Dict[str, VulnerabilityAISession] = {}
    
    def get_or_create_session(self, vulnerability_id: str, vulnerability_data: Dict) -> VulnerabilityAISession:
        """Get existing session or create new one"""
        if vulnerability_id not in self.active_sessions:
            self.active_sessions[vulnerability_id] = VulnerabilityAISession(
                vulnerability_id, vulnerability_data
            )
        return self.active_sessions[vulnerability_id]
    
    def get_session(self, vulnerability_id: str) -> Optional[VulnerabilityAISession]:
        """Get existing session"""
        return self.active_sessions.get(vulnerability_id)
    
    def get_all_sessions(self) -> Dict[str, Dict]:
        """Get info for all sessions"""
        return {
            vuln_id: session.get_session_info() 
            for vuln_id, session in self.active_sessions.items()
        }
    
    def close_session(self, vulnerability_id: str):
        """Close a session"""
        if vulnerability_id in self.active_sessions:
            self.active_sessions[vulnerability_id].status = "closed"
            del self.active_sessions[vulnerability_id]
