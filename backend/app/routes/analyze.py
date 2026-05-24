from fastapi import APIRouter, HTTPException
from typing import List, Optional
from ..models import AnalyzeRequest, AnalyzeResponse, LogEntry, RootCauseAnalysis
from ..services.root_cause import analyzer
from ..utils.helpers import generate_id, format_timestamp

router = APIRouter(prefix="/analyze", tags=["Root Cause Analysis"])

@router.post("/", response_model=AnalyzeResponse)
async def analyze_root_cause(request: AnalyzeRequest):
    """
    Analyze logs to identify root cause of an incident.
    
    Expects a list of log entries and optional incident_id.
    Returns structured root cause analysis with timeline, recommendations, and confidence scores.
    """
    try:
        # Validate input
        if not request.logs or len(request.logs) == 0:
            return AnalyzeResponse(
                success=False,
                analysis=None,
                error="No logs provided for analysis"
            )
        
        # Generate incident_id if not provided
        incident_id = request.incident_id or generate_id("incident")
        
        # Perform root cause analysis using LLM
        analysis = await analyzer.analyze(request.logs, incident_id)
        
        return AnalyzeResponse(
            success=True,
            analysis=analysis,
            error=None
        )
        
    except Exception as e:
        return AnalyzeResponse(
            success=False,
            analysis=None,
            error=f"Analysis failed: {str(e)}"
        )

@router.post("/batch", response_model=List[AnalyzeResponse])
async def analyze_multiple(requests: List[AnalyzeRequest]):
    """Analyze multiple log batches (for testing or batch processing)."""
    results = []
    for req in requests:
        result = await analyze_root_cause(req)
        results.append(result)
    return results

@router.get("/health")
async def health_check():
    """Simple health check for the analyze service."""
    return {"status": "healthy", "service": "root-cause-analyzer"}