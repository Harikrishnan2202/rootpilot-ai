from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models import LogEntry, TimelineEvent
from ..utils.helpers import truncate_string

class TimelineBuilder:
    """
    Builds a chronological timeline of events from logs.
    Extracts key events (errors, warnings, state changes) and orders them.
    """
    
    def __init__(self):
        # Keywords that indicate significant events
        self.event_keywords = {
            "critical": [
                "crash", "failed", "timeout", "deadlock", "exhausted", 
                "outage", "unavailable", "corrupt", "fatal"
            ],
            "important": [
                "error", "warning", "slow", "high", "low", "retry",
                "connection", "pool", "memory", "cpu", "latency"
            ],
            "info": [
                "started", "stopped", "initialized", "completed", 
                "success", "created", "deleted", "updated"
            ]
        }
    
    def build_timeline(self, logs: List[LogEntry], max_events: int = 15) -> List[TimelineEvent]:
        """
        Build a timeline from log entries.
        
        Args:
            logs: List of log entries (already sorted by timestamp)
            max_events: Maximum number of events to include
            
        Returns:
            List of TimelineEvent objects in chronological order
        """
        if not logs:
            return []
        
        # Sort logs by timestamp (assuming timestamps are comparable strings)
        sorted_logs = sorted(logs, key=lambda x: x.timestamp)
        
        events = []
        for log in sorted_logs:
            # Determine if this log should become a timeline event
            importance = self._calculate_importance(log)
            if importance > 0:
                event = self._log_to_event(log, importance)
                events.append(event)
        
        # Limit number of events
        if len(events) > max_events:
            # Keep most important events (higher importance score)
            events.sort(key=lambda x: self._event_importance_score(x), reverse=True)
            events = events[:max_events]
            # Re-sort by timestamp
            events.sort(key=lambda x: x.timestamp)
        
        return events
    
    def _calculate_importance(self, log: LogEntry) -> int:
        """
        Calculate importance score (0-100) for a log entry.
        Higher score = more likely to be included in timeline.
        """
        score = 0
        message_lower = log.message.lower()
        
        # Level-based scoring
        if log.level == "ERROR":
            score += 50
        elif log.level == "WARNING":
            score += 25
        elif log.level == "INFO":
            score += 5
        else:
            score += 0
        
        # Keyword-based scoring
        for keyword in self.event_keywords["critical"]:
            if keyword in message_lower:
                score += 30
                break
        
        for keyword in self.event_keywords["important"]:
            if keyword in message_lower:
                score += 15
                break
        
        # Service-specific importance
        if any(service in message_lower for service in ["database", "payment", "gateway"]):
            score += 10
        
        # Cap at 100
        return min(score, 100)
    
    def _event_importance_score(self, event: TimelineEvent) -> int:
        """Calculate importance score for a TimelineEvent."""
        score = 0
        if "ERROR" in event.event or "CRITICAL" in event.event:
            score += 50
        elif "WARNING" in event.event:
            score += 25
        
        # Check details for keywords
        details_lower = event.details.lower()
        for keyword in self.event_keywords["critical"]:
            if keyword in details_lower:
                score += 30
                break
        for keyword in self.event_keywords["important"]:
            if keyword in details_lower:
                score += 15
                break
        
        return min(score, 100)
    
    def _log_to_event(self, log: LogEntry, importance: int) -> TimelineEvent:
        """Convert a LogEntry to a TimelineEvent."""
        # Create a concise event description
        if log.level == "ERROR":
            event_type = "ERROR"
        elif log.level == "WARNING":
            event_type = "WARNING"
        else:
            event_type = "INFO"
        
        # Truncate message for details
        details = truncate_string(log.message, 150)
        
        return TimelineEvent(
            timestamp=log.timestamp,
            event=event_type,
            service=log.service.value if log.service else None,
            details=details
        )
    
    def build_crisis_timeline(self, logs: List[LogEntry], incident_start: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Build a detailed crisis timeline with before/during/after phases.
        Returns a list of phase objects with events.
        """
        if not logs:
            return []
        
        sorted_logs = sorted(logs, key=lambda x: x.timestamp)
        
        # If incident_start provided, split logs into phases
        if incident_start:
            before = [l for l in sorted_logs if l.timestamp < incident_start]
            during = [l for l in sorted_logs if l.timestamp >= incident_start]
        else:
            # Find approximate incident start: first ERROR or cluster of warnings
            incident_idx = 0
            for i, log in enumerate(sorted_logs):
                if log.level == "ERROR" or (log.level == "WARNING" and i > 0 and sorted_logs[i-1].level == "WARNING"):
                    incident_idx = max(0, i - 2)
                    break
            before = sorted_logs[:incident_idx]
            during = sorted_logs[incident_idx:]
        
        phases = []
        
        if before:
            phases.append({
                "phase": "BEFORE",
                "description": "Normal operations before incident",
                "events": [self._log_to_event(l, 0) for l in before[-5:]]  # Last 5 events before
            })
        
        if during:
            phases.append({
                "phase": "DURING",
                "description": "Incident unfolding",
                "events": [self._log_to_event(l, self._calculate_importance(l)) for l in during[:10]]  # First 10 during
            })
        
        # After phase (recovery)
        after_logs = [l for l in sorted_logs if l.level == "INFO" and "success" in l.message.lower()]
        if after_logs:
            phases.append({
                "phase": "AFTER",
                "description": "Recovery and resolution",
                "events": [self._log_to_event(l, 0) for l in after_logs[-3:]]
            })
        
        return phases
    
    def get_timeline_summary(self, timeline: List[TimelineEvent]) -> str:
        """
        Generate a human-readable summary of the timeline.
        """
        if not timeline:
            return "No significant events detected."
        
        error_count = sum(1 for e in timeline if "ERROR" in e.event)
        warning_count = sum(1 for e in timeline if "WARNING" in e.event)
        
        if error_count > 0:
            return f"Timeline shows {error_count} errors and {warning_count} warnings. First error at {timeline[0].timestamp}."
        elif warning_count > 0:
            return f"Timeline shows {warning_count} warnings but no critical errors."
        else:
            return f"Timeline shows {len(timeline)} informational events. System appears stable."

# Singleton instance
timeline_builder = TimelineBuilder()