import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import google.generativeai as genai
from openai import OpenAI

from ..config import Config
from ..models import (
    LogEntry, RootCauseAnalysis, RootCauseCandidate, 
    TimelineEvent, FixRecommendation, Severity
)
from ..utils.helpers import generate_id, format_timestamp, truncate_string

class RootCauseAnalyzer:
    """
    AI-powered root cause analysis engine.
    Uses LLM (Gemini or OpenAI) to analyze logs and produce structured insights.
    """
    
    def __init__(self):
        self.provider = Config.LLM_PROVIDER
        self.model = None
        self.client = None
        
        try:
            if self.provider == "gemini":
                genai.configure(api_key=Config.GEMINI_API_KEY)
                # Try models in order of preference (latest first)
                model_names = ['gemini-1.5-flash-latest', 'gemini-1.5-flash', 'gemini-pro', 'gemini-pro-vision']
                for model_name in model_names:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        break
                    except Exception:
                        continue
                
                if not self.model:
                    # Fallback to generic initialization
                    self.model = genai.GenerativeModel('gemini-pro')
            elif self.provider == "openai":
                self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        except Exception as e:
            print(f"Warning: LLM initialization error: {e}. Fallback analysis will be used.")
            self.model = None
            self.client = None
    
    def _build_analysis_prompt(self, logs: List[LogEntry], incident_context: Optional[Dict] = None) -> str:
        """Build the prompt for the LLM to analyze logs and find root cause."""
        
        # Format logs for the prompt (limit to avoid token overflow)
        log_texts = []
        for log in logs[-50:]:  # Last 50 logs
            log_texts.append(f"[{log.timestamp}] {log.service.value} | {log.level} | {log.message}")
        logs_str = "\n".join(log_texts)
        
        prompt = f"""You are an expert SRE (Site Reliability Engineer) analyzing system logs to find root cause of an incident.

=== LOGS (most recent first) ===
{logs_str}
=== END OF LOGS ===

Analyze these logs and return a JSON response with the following structure:

{{
    "summary": "Brief one-sentence summary of what happened",
    "root_causes": [
        {{
            "cause": "Brief description of root cause",
            "confidence": 85,
            "explanation": "Detailed explanation of why this is the likely cause",
            "affected_services": ["service1", "service2"]
        }}
    ],
    "timeline": [
        {{
            "timestamp": "HH:MM:SS",
            "event": "What happened",
            "service": "service name (optional)",
            "details": "Specific details"
        }}
    ],
    "recommendations": [
        {{
            "action": "Short action name",
            "type": "immediate|short-term|long-term",
            "description": "What to do and why",
            "estimated_impact": "Expected result"
        }}
    ]
}}

Requirements:
- Return ONLY valid JSON, no extra text.
- confidence should be an integer 0-100.
- Include 2-3 root causes sorted by confidence descending.
- Timeline should have 4-6 key events in chronological order.
- Recommendations: 1-2 immediate, 1 short-term, 1 long-term.
- If no incident, create a plausible analysis from the logs.
- Be specific: mention service names, error types, metrics.
"""
        return prompt
    
    async def analyze(self, logs: List[LogEntry], incident_id: Optional[str] = None) -> RootCauseAnalysis:
        """
        Perform root cause analysis on the provided logs.
        
        Args:
            logs: List of LogEntry objects
            incident_id: Optional incident ID for reference
            
        Returns:
            RootCauseAnalysis object with structured findings
        """
        if not logs:
            # Return a default analysis if no logs
            return RootCauseAnalysis(
                incident_id=incident_id or generate_id("incident"),
                summary="No logs available for analysis.",
                root_causes=[RootCauseCandidate(
                    cause="Insufficient data",
                    confidence=0,
                    explanation="No logs were provided for analysis.",
                    affected_services=[]
                )],
                timeline=[],
                recommendations=[],
                analysis_timestamp=format_timestamp()
            )
        
        # Check if LLM is available
        if not self.model and not self.client:
            return self._fallback_analysis(logs, incident_id, error="LLM not initialized - using heuristic analysis")
        
        prompt = self._build_analysis_prompt(logs)
        
        try:
            if self.provider == "gemini" and self.model:
                response = self.model.generate_content(prompt)
                raw_text = response.text
            elif self.provider == "openai" and self.client:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=2000
                )
                raw_text = response.choices[0].message.content
            else:
                return self._fallback_analysis(logs, incident_id, error="LLM client not properly initialized")
            
            # Extract JSON from response (handle markdown code blocks)
            json_str = raw_text.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.startswith("```"):
                json_str = json_str[3:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            json_str = json_str.strip()
            
            data = json.loads(json_str)
            
            # Parse into Pydantic models
            root_causes = [
                RootCauseCandidate(
                    cause=rc["cause"],
                    confidence=rc["confidence"],
                    explanation=rc["explanation"],
                    affected_services=rc.get("affected_services", [])
                )
                for rc in data.get("root_causes", [])
            ]
            
            timeline = [
                TimelineEvent(
                    timestamp=ev["timestamp"],
                    event=ev["event"],
                    service=ev.get("service"),
                    details=ev.get("details", "")
                )
                for ev in data.get("timeline", [])
            ]
            
            recommendations = [
                FixRecommendation(
                    action=rec["action"],
                    type=rec["type"],
                    description=rec["description"],
                    estimated_impact=rec.get("estimated_impact", "Improved stability")
                )
                for rec in data.get("recommendations", [])
            ]
            
            return RootCauseAnalysis(
                incident_id=incident_id or generate_id("incident"),
                summary=data.get("summary", "Analysis completed."),
                root_causes=root_causes,
                timeline=timeline,
                recommendations=recommendations,
                analysis_timestamp=format_timestamp()
            )
            
        except Exception as e:
            # Fallback: provide a basic analysis without LLM
            return self._fallback_analysis(logs, incident_id, error=str(e))
    
    def _fallback_analysis(self, logs: List[LogEntry], incident_id: Optional[str], error: str) -> RootCauseAnalysis:
        """Fallback analysis when LLM fails."""
        # Simple heuristic: count errors per service
        service_errors = {}
        error_messages = []
        for log in logs:
            if log.level == "ERROR":
                service_errors[log.service.value] = service_errors.get(log.service.value, 0) + 1
                error_messages.append(log.message)
        
        # Determine most affected service
        most_affected = max(service_errors.items(), key=lambda x: x[1])[0] if service_errors else "unknown"
        
        # Build simple timeline from errors
        timeline = []
        for i, log in enumerate(logs[-10:], 1):
            if log.level in ["ERROR", "WARNING"]:
                timeline.append(TimelineEvent(
                    timestamp=log.timestamp,
                    event=log.level,
                    service=log.service.value,
                    details=truncate_string(log.message, 100)
                ))
        
        return RootCauseAnalysis(
            incident_id=incident_id or generate_id("incident"),
            summary=f"High error count detected in {most_affected} service. LLM error: {error[:100]}",
            root_causes=[
                RootCauseCandidate(
                    cause=f"Errors in {most_affected} service",
                    confidence=min(70, len(error_messages) * 10),
                    explanation=f"Found {len(error_messages)} error entries. Sample: {error_messages[0] if error_messages else 'No specific error messages'}",
                    affected_services=list(service_errors.keys())
                )
            ],
            timeline=timeline,
            recommendations=[
                FixRecommendation(
                    action="Check service logs",
                    type="immediate",
                    description="Investigate the failing service logs for more details.",
                    estimated_impact="Identify exact failure point"
                )
            ],
            analysis_timestamp=format_timestamp()
        )

# Singleton instance
analyzer = RootCauseAnalyzer()