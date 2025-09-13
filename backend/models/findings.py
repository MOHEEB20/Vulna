"""Data models for vulnerability findings and HTTP traffic analysis."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class RiskLevel(str, Enum):
    """Risk severity levels."""
    CRITICAL = "CRITICAL"    # 9-10
    HIGH = "HIGH"           # 7-8
    MEDIUM = "MEDIUM"       # 4-6
    LOW = "LOW"            # 1-3
    INFO = "INFO"          # 0


class HttpMethod(str, Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class HttpRequest(BaseModel):
    """HTTP request data model."""
    method: HttpMethod
    url: str
    headers: Dict[str, str] = Field(default_factory=dict)
    body: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class HttpResponse(BaseModel):
    """HTTP response data model."""
    status_code: int
    headers: Dict[str, str] = Field(default_factory=dict)
    body: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}



class VulnerabilityFinding(BaseModel):
    """Enhanced vulnerability finding from LLM analysis."""
    id: str = Field(..., description="Unique finding identifier")
    risk_score: int = Field(..., ge=0, le=10, description="Risk score 0-10")
    risk_level: RiskLevel = Field(..., description="Risk severity level")
    owasp_categories: List[str] = Field(default_factory=list)
    cwe_ids: List[str] = Field(default_factory=list)
    title: str = Field(..., description="Finding title")
    description: str = Field(..., description="Detailed description")
    suggestion: str = Field(..., description="Remediation suggestion")
    confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence")
    
    # NEW: Enhanced fields for better context
    affected_url: str = Field(default="", description="Primary affected URL")
    request_method: str = Field(default="", description="HTTP method of vulnerable request")
    request_headers: Dict[str, str] = Field(default_factory=dict, description="Request headers")
    request_body: Optional[str] = Field(default=None, description="Request body content")
    response_status: Optional[int] = Field(default=None, description="Response status code")
    response_headers: Dict[str, str] = Field(default_factory=dict, description="Response headers")
    response_body: Optional[str] = Field(default=None, description="Response body content")
    
    # NEW: Proof of Concept and exploitation details
    proof_of_concept: Optional[str] = Field(default=None, description="PoC code or curl command")
    exploitation_steps: List[str] = Field(default_factory=list, description="Step-by-step exploitation")
    impact: str = Field(default="", description="Business impact description")
    affected_parameters: List[str] = Field(default_factory=list, description="Vulnerable parameters")
    
    # NEW: AI conversation support
    ai_conversation: List[Dict[str, str]] = Field(default_factory=list, description="AI chat history")
    related_request_ids: List[str] = Field(default_factory=list, description="Related request IDs")
    
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class TrafficAnalysis(BaseModel):
    """Complete traffic analysis result."""
    id: str = Field(..., description="Unique analysis identifier")
    request: HttpRequest
    response: Optional[HttpResponse] = None
    finding: Optional[VulnerabilityFinding] = None
    analysis_duration: float = Field(..., description="Analysis time in seconds")
    llm_tokens_used: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class QueueItem(BaseModel):
    """Queue item for LLM processing."""
    id: str
    request: HttpRequest
    response: Optional[HttpResponse] = None
    priority: int = Field(default=0, description="Processing priority")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
