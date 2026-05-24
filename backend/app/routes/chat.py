from fastapi import APIRouter, HTTPException
from typing import Optional, List
from ..models import ChatRequest, ChatResponse, LogEntry
from ..services.chat_engine import chat_engine
from ..services.root_cause import analyzer
from ..utils.helpers import generate_id

router = APIRouter(prefix="/chat", tags=["Natural Language Chat"])

# In-memory storage for log context (can be improved with a database)
log_context_store = {}  # session_id -> list of LogEntry
analysis_store = {}     # session_id -> analysis

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Send a natural language question about the incident.
    The AI will answer based on the provided logs and optional analysis.
    """
    try:
        # Validate input
        if not request.question or not request.question.strip():
            return ChatResponse(
                success=False,
                answer="Please provide a question.",
                error="Empty question"
            )
        
        session_id = request.incident_id or generate_id("chat_session")
        
        # Get logs context (if not provided, try to get from store)
        logs = request.logs_context
        if not logs and session_id in log_context_store:
            logs = log_context_store[session_id]
        
        if not logs or len(logs) == 0:
            return ChatResponse(
                success=False,
                answer="No logs available. Please provide logs_context or generate logs first.",
                error="Missing logs context"
            )
        
        # Get analysis if available (either from request or store)
        analysis = None
        if session_id in analysis_store:
            analysis = analysis_store[session_id]
        
        # Process the chat
        answer = await chat_engine.chat(
            question=request.question,
            logs=logs,
            analysis=analysis,
            session_id=session_id
        )
        
        return ChatResponse(
            success=True,
            answer=answer,
            error=None
        )
        
    except Exception as e:
        return ChatResponse(
            success=False,
            answer="Sorry, an error occurred while processing your question.",
            error=str(e)
        )

@router.post("/context")
async def set_chat_context(
    session_id: str,
    logs: List[LogEntry],
    analysis: Optional[dict] = None
):
    """
    Set or update the context (logs and analysis) for a chat session.
    This allows the chat to remember the incident details.
    """
    try:
        log_context_store[session_id] = logs
        if analysis:
            analysis_store[session_id] = analysis
        return {
            "success": True,
            "message": f"Context set for session {session_id}",
            "logs_count": len(logs),
            "analysis_available": analysis is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions")
async def get_suggested_questions(
    session_id: Optional[str] = None,
    logs: Optional[List[LogEntry]] = None
):
    """
    Get suggested follow-up questions based on current context.
    """
    try:
        # Get logs from session or use provided
        context_logs = logs
        if not context_logs and session_id and session_id in log_context_store:
            context_logs = log_context_store[session_id]
        
        if not context_logs or len(context_logs) == 0:
            return {
                "success": True,
                "suggestions": [
                    "What is the current system status?",
                    "Show me critical errors",
                    "What should I do first?"
                ]
            }
        
        # Get analysis if available
        analysis = None
        if session_id and session_id in analysis_store:
            analysis = analysis_store[session_id]
        
        suggestions = chat_engine.get_suggested_questions(context_logs, analysis)
        
        return {
            "success": True,
            "suggestions": suggestions
        }
        
    except Exception as e:
        return {
            "success": False,
            "suggestions": [],
            "error": str(e)
        }

@router.delete("/{session_id}")
async def clear_chat_context(session_id: str):
    """Clear stored context for a session."""
    if session_id in log_context_store:
        del log_context_store[session_id]
    if session_id in analysis_store:
        del analysis_store[session_id]
    return {"success": True, "message": f"Cleared context for session {session_id}"}