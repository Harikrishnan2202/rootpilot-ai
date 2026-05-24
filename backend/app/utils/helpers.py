import hashlib
from datetime import datetime
from typing import List, Dict, Any
import re

def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    unique_hash = hashlib.md5(timestamp.encode()).hexdigest()[:8]
    if prefix:
        return f"{prefix}_{unique_hash}"
    return unique_hash

def format_timestamp(dt: datetime = None) -> str:
    """Format datetime to ISO string or current time if None."""
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()

def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """Extract simple keywords from text (lowercase, alphanumeric, common tech terms)."""
    # Simple extraction: find words that look like error codes or service names
    # For hackathon, this is sufficient; can be enhanced with NLP later.
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9_\-]{2,}\b', text.lower())
    # Filter out common stop words
    stop_words = {'the', 'and', 'for', 'with', 'from', 'this', 'that', 'was', 'are', 'been'}
    keywords = [w for w in words if w not in stop_words]
    # Return unique, limited
    seen = set()
    unique_keywords = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)
        if len(unique_keywords) >= max_keywords:
            break
    return unique_keywords

def calculate_severity(logs: List[Any]) -> str:
    """
    Calculate incident severity based on log levels and keywords.
    Returns: "critical", "medium", or "low"
    """
    error_count = 0
    critical_keywords = ["fail", "timeout", "crash", "outage", "dead", "corrupt"]
    warning_count = 0
    
    for log in logs:
        level = getattr(log, 'level', '').upper()
        message = getattr(log, 'message', '').lower()
        
        if level == 'ERROR':
            error_count += 1
        elif level == 'WARNING':
            warning_count += 1
        
        # If any critical keyword appears, bump severity
        if any(kw in message for kw in critical_keywords):
            return "critical"
    
    if error_count >= 3 or warning_count >= 10:
        return "critical"
    elif error_count >= 1 or warning_count >= 5:
        return "medium"
    else:
        return "low"

def group_logs_by_service(logs: List[Any]) -> Dict[str, List[Any]]:
    """Group log entries by service name."""
    grouped = {}
    for log in logs:
        service = getattr(log, 'service', 'unknown')
        if service not in grouped:
            grouped[service] = []
        grouped[service].append(log)
    return grouped

def truncate_string(text: str, max_length: int = 200) -> str:
    """Truncate text to max_length and add ellipsis if needed."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Recursively merge two dictionaries."""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result