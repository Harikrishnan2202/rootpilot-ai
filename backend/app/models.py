from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

# ========== Enums ==========
class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    CRITICAL = "critical"

class ServiceName(str, Enum):
    API_GATEWAY = "api-gateway"
    AUTH_SERVICE = "auth-service"
    PAYMENT_SERVICE = "payment-service"
    DATABASE = "database"
    REDIS_CACHE = "redis-cache"

# ========== Log Models ==========
class LogEntry(BaseModel):
    timestamp: str  # ISO format or "HH:MM:SS"
    service: ServiceName
    level: str  # INFO, WARNING, ERROR, DEBUG
    message: str
    metadata: Optional[Dict[str, Any]] = None

# ========== Incident Models ==========
class Incident(BaseModel):
    id: str
    title: str
    severity: Severity
    start_time: str
    end_time: Optional[str] = None
    affected_services: List[ServiceName]
    status: str  # "active", "resolved", "investigating"
    logs: List[LogEntry] = []

# ========== Root Cause Analysis Models ==========
class RootCauseCandidate(BaseModel):
    cause: str
    confidence: float  # 0-100
    explanation: str
    affected_services: List[str]

class TimelineEvent(BaseModel):
    timestamp: str
    event: str
    service: Optional[str] = None
    details: str

class FixRecommendation(BaseModel):
    action: str
    type: str  # "immediate", "short-term", "long-term"
    description: str
    estimated_impact: str

class RootCauseAnalysis(BaseModel):
    incident_id: str
    summary: str
    root_causes: List[RootCauseCandidate]
    timeline: List[TimelineEvent]
    recommendations: List[FixRecommendation]
    analysis_timestamp: str

# ========== Request Models ==========
class AnalyzeRequest(BaseModel):
    logs: List[LogEntry]
    incident_id: Optional[str] = None

class ChatRequest(BaseModel):
    question: str
    incident_id: Optional[str] = None
    logs_context: Optional[List[LogEntry]] = None

class ChatContextRequest(BaseModel):
    session_id: str
    logs: List[LogEntry]
    analysis: Optional[Dict[str, Any]] = None

# ========== Response Models ==========
class AnalyzeResponse(BaseModel):
    success: bool
    analysis: Optional[RootCauseAnalysis] = None
    error: Optional[str] = None

class ChatResponse(BaseModel):
    success: bool
    answer: str
    error: Optional[str] = None

class LogsResponse(BaseModel):
    success: bool
    logs: List[LogEntry]
    count: int
    error: Optional[str] = None

# ========== Health Check ==========
class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    timestamp: str
