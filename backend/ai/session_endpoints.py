"""
Enhanced AI Session Endpoints for Vulna Dashboard
Replaces isolated AI workers with session-based AI analysis
"""

from fastapi import FastAPI, Request
from backend.ai.session_manager import AISessionManager
from datetime import datetime


def add_ai_session_endpoints(app: FastAPI, dashboard_manager):
    """Add AI session endpoints to the FastAPI app"""
    
    @app.post("/api/vulnerability/{vuln_id}/generate-poc-session")
    async def generate_poc_session(vuln_id: str):
        """Generate PoC using AI Session (NEW VERSION)"""
        try:
            findings = await dashboard_manager.get_all_findings()
            vulnerability = None
            
            for finding in findings:
                if finding.get("id") == vuln_id:
                    vulnerability = finding
                    break
            
            if not vulnerability:
                return {"success": False, "message": "Vulnerability not found"}
            
            # Get or create AI session
            ai_session = dashboard_manager.ai_session_manager.get_or_create_session(vuln_id, vulnerability)
            
            # Generate PoC
            result = await ai_session.generate_poc()
            
            if result["success"]:
                # Broadcast to dashboard
                await dashboard_manager.broadcast_update({
                    "type": "ai_poc_completed",
                    "vulnerability_id": vuln_id,
                    "session_id": result["session_id"],
                    "content": result["poc_content"],
                    "timestamp": datetime.now().isoformat()
                })
                
                # Return with session info
                return {
                    "success": True,
                    "proof_of_concept": result["poc_content"],
                    "session_id": result["session_id"],
                    "vulnerability_id": vuln_id,
                    "message": "PoC generated successfully with session tracking"
                }
            
            return result
            
        except Exception as e:
            return {"success": False, "message": f"PoC generation error: {str(e)}"}
    
    @app.post("/api/vulnerability/{vuln_id}/auto-test-session")
    async def auto_test_session(vuln_id: str):
        """Auto Test using AI Session (NEW VERSION)"""
        try:
            findings = await dashboard_manager.get_all_findings()
            vulnerability = None
            
            for finding in findings:
                if finding.get("id") == vuln_id:
                    vulnerability = finding
                    break
            
            if not vulnerability:
                return {"success": False, "message": "Vulnerability not found"}
            
            # Get or create AI session
            ai_session = dashboard_manager.ai_session_manager.get_or_create_session(vuln_id, vulnerability)
            
            # Perform auto test
            result = await ai_session.auto_test()
            
            if result["success"]:
                # Broadcast to dashboard
                await dashboard_manager.broadcast_update({
                    "type": "ai_autotest_completed",
                    "vulnerability_id": vuln_id,
                    "session_id": result["session_id"],
                    "content": result["test_results"],
                    "timestamp": datetime.now().isoformat()
                })
                
                return {
                    "success": True,
                    "test_results": result["test_results"],
                    "session_id": result["session_id"],
                    "vulnerability_id": vuln_id,
                    "message": "Auto-test completed with detailed results"
                }
            
            return result
            
        except Exception as e:
            return {"success": False, "message": f"Auto test error: {str(e)}"}
    
    @app.post("/api/vulnerability/{vuln_id}/exploitation-session")
    async def exploitation_analysis_session(vuln_id: str):
        """Exploitation Analysis using AI Session (NEW VERSION)"""
        try:
            findings = await dashboard_manager.get_all_findings()
            vulnerability = None
            
            for finding in findings:
                if finding.get("id") == vuln_id:
                    vulnerability = finding
                    break
            
            if not vulnerability:
                return {"success": False, "message": "Vulnerability not found"}
            
            # Get or create AI session
            ai_session = dashboard_manager.ai_session_manager.get_or_create_session(vuln_id, vulnerability)
            
            # Perform exploitation analysis
            result = await ai_session.exploitation_analysis()
            
            if result["success"]:
                # Broadcast to dashboard
                await dashboard_manager.broadcast_update({
                    "type": "ai_exploitation_completed",
                    "vulnerability_id": vuln_id,
                    "session_id": result["session_id"],
                    "content": result["exploitation_info"],
                    "timestamp": datetime.now().isoformat()
                })
                
                return {
                    "success": True,
                    "exploitation_analysis": result["exploitation_info"],
                    "session_id": result["session_id"],
                    "vulnerability_id": vuln_id,
                    "message": "Exploitation analysis completed with session tracking"
                }
            
            return result
            
        except Exception as e:
            return {"success": False, "message": f"Exploitation analysis error: {str(e)}"}
    
    @app.post("/api/vulnerability/{vuln_id}/ai-chat-session")
    async def ai_chat_session(vuln_id: str, request: Request):
        """Chat with AI about vulnerability (NEW VERSION)"""
        try:
            data = await request.json()
            user_message = data.get("message", "")
            
            if not user_message:
                return {"success": False, "message": "No message provided"}
            
            findings = await dashboard_manager.get_all_findings()
            vulnerability = None
            
            for finding in findings:
                if finding.get("id") == vuln_id:
                    vulnerability = finding
                    break
            
            if not vulnerability:
                return {"success": False, "message": "Vulnerability not found"}
            
            # Get or create AI session
            ai_session = dashboard_manager.ai_session_manager.get_or_create_session(vuln_id, vulnerability)
            
            # Chat with AI
            result = await ai_session.chat_with_ai(user_message)
            
            if result["success"]:
                # Broadcast to dashboard
                await dashboard_manager.broadcast_update({
                    "type": "ai_chat_message",
                    "vulnerability_id": vuln_id,
                    "session_id": result["session_id"],
                    "user_message": user_message,
                    "ai_response": result["ai_response"],
                    "timestamp": datetime.now().isoformat()
                })
                
                return {
                    "success": True,
                    "ai_response": result["ai_response"],
                    "session_id": result["session_id"],
                    "user_message": user_message,
                    "vulnerability_id": vuln_id,
                    "message": "AI responded with session context"
                }
            
            return result
            
        except Exception as e:
            return {"success": False, "message": f"AI chat error: {str(e)}"}
    
    @app.get("/api/vulnerability/{vuln_id}/session-info")
    async def get_session_info(vuln_id: str):
        """Get complete AI session information"""
        try:
            ai_session = dashboard_manager.ai_session_manager.get_session(vuln_id)
            
            if not ai_session:
                return {
                    "success": False, 
                    "message": "No AI session found for this vulnerability",
                    "vulnerability_id": vuln_id
                }
            
            session_info = ai_session.get_session_info()
            
            return {
                "success": True,
                "session_info": session_info,
                "vulnerability_id": vuln_id,
                "message": "Session information retrieved"
            }
            
        except Exception as e:
            return {"success": False, "message": f"Session info error: {str(e)}"}
    
    @app.get("/api/ai-sessions-overview")
    async def ai_sessions_overview():
        """Get overview of all AI sessions"""
        try:
            all_sessions = dashboard_manager.ai_session_manager.get_all_sessions()
            
            # Create summary
            session_summary = {
                "total_sessions": len(all_sessions),
                "active_sessions": len([s for s in all_sessions.values() if s.get("status") == "active"]),
                "sessions": all_sessions
            }
            
            return {
                "success": True,
                "sessions_overview": session_summary,
                "message": f"Found {len(all_sessions)} AI sessions"
            }
            
        except Exception as e:
            return {"success": False, "message": f"Sessions overview error: {str(e)}"}
