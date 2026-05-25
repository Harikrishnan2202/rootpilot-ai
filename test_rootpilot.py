#!/usr/bin/env python3
"""
RootPilot AI - Comprehensive Test Suite
Demonstrates all major features and API endpoints
"""

import requests
import json
from datetime import datetime, timedelta
import time

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3001"

# Colors for output
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

def print_header(text):
    print(f"\n{BLUE}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    print(f"{YELLOW}→ {text}{RESET}")

# ============================================================================
# TEST 1: HEALTH CHECK
# ============================================================================
def test_health_check():
    print_header("TEST 1: HEALTH CHECK")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success("Backend is healthy")
            print(f"  Status: {data['status']}")
            print(f"  LLM Provider: {data['llm_provider']}")
            print(f"  Timestamp: {data['timestamp']}")
            return True
        else:
            print_error(f"Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Connection failed: {str(e)}")
        return False

# ============================================================================
# TEST 2: GENERATE LOGS
# ============================================================================
def test_generate_logs():
    print_header("TEST 2: GENERATE LOGS")
    try:
        response = requests.post(f"{BASE_URL}/logs/generate?count=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Generated {data['generated']} log entries")
            print(f"  Total stored: {data['total_stored']}")
            return True
        else:
            print_error(f"Failed to generate logs: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

# ============================================================================
# TEST 3: RETRIEVE LOGS
# ============================================================================
def test_retrieve_logs():
    print_header("TEST 3: RETRIEVE LOGS")
    try:
        response = requests.get(f"{BASE_URL}/logs/?limit=10", timeout=5)
        if response.status_code == 200:
            data = response.json()
            logs = data.get('logs', [])
            print_success(f"Retrieved {len(logs)} logs")
            
            print(f"\n  Sample Logs:")
            for i, log in enumerate(logs[:3], 1):
                print(f"\n  Log #{i}:")
                print(f"    Service: {log.get('service', 'N/A')}")
                print(f"    Level: {log.get('level', 'N/A')}")
                print(f"    Message: {log.get('message', 'N/A')}")
                print(f"    Timestamp: {log.get('timestamp', 'N/A')}")
            return True
        else:
            print_error(f"Failed to retrieve logs: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

# ============================================================================
# TEST 4: FILTER LOGS BY SERVICE
# ============================================================================
def test_filter_logs_by_service():
    print_header("TEST 4: FILTER LOGS BY SERVICE")
    try:
        services = ["api-gateway", "database", "payment-service"]
        for service in services:
            response = requests.get(f"{BASE_URL}/logs/?service={service}&limit=5", timeout=5)
            if response.status_code == 200:
                logs = response.json().get('logs', [])
                print_success(f"Service '{service}': {len(logs)} logs found")
        return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

# ============================================================================
# TEST 5: FILTER LOGS BY LEVEL
# ============================================================================
def test_filter_logs_by_level():
    print_header("TEST 5: FILTER LOGS BY LEVEL")
    try:
        levels = ["INFO", "WARNING", "ERROR"]
        for level in levels:
            response = requests.get(f"{BASE_URL}/logs/?level={level}&limit=5", timeout=5)
            if response.status_code == 200:
                logs = response.json().get('logs', [])
                print_success(f"Level '{level}': {len(logs)} logs found")
        return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

# ============================================================================
# TEST 6: ANALYZE ROOT CAUSE
# ============================================================================
def test_analyze_root_cause():
    print_header("TEST 6: ANALYZE ROOT CAUSE - AI ANALYSIS")
    
    # Create realistic incident logs
    now = datetime.now()
    sample_logs = [
        {
            "timestamp": (now - timedelta(minutes=5)).isoformat(),
            "service": "payment-service",
            "level": "ERROR",
            "message": "Connection timeout to database"
        },
        {
            "timestamp": (now - timedelta(minutes=4)).isoformat(),
            "service": "database",
            "level": "WARNING",
            "message": "Connection pool at 95% capacity"
        },
        {
            "timestamp": (now - timedelta(minutes=3)).isoformat(),
            "service": "api-gateway",
            "level": "ERROR",
            "message": "Request timeout - payment service unresponsive"
        },
        {
            "timestamp": (now - timedelta(minutes=2)).isoformat(),
            "service": "payment-service",
            "level": "ERROR",
            "message": "Failed transaction: ORD925873"
        },
        {
            "timestamp": (now - timedelta(minutes=1)).isoformat(),
            "service": "auth-service",
            "level": "INFO",
            "message": "User session invalidated due to timeout"
        }
    ]
    
    try:
        print_info("Sending incident logs for AI analysis...")
        print(f"  Total logs: {len(sample_logs)}")
        
        response = requests.post(
            f"{BASE_URL}/analyze",
            json={"logs": sample_logs},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print_success("Root cause analysis completed")
            print(f"\n  Incident Summary:")
            print(f"    - Timestamp: {data.get('timestamp', 'N/A')}")
            print(f"    - Services Affected: {len(data.get('services_affected', []))}")
            
            print(f"\n  Root Causes:")
            for i, cause in enumerate(data.get('root_causes', [])[:3], 1):
                print(f"    {i}. {cause.get('cause', 'N/A')}")
                print(f"       Confidence: {cause.get('confidence', 'N/A')}%")
                print(f"       Service: {cause.get('service', 'N/A')}")
            
            print(f"\n  Timeline Events: {len(data.get('timeline', []))}")
            for i, event in enumerate(data.get('timeline', [])[:3], 1):
                print(f"    {i}. {event.get('event', 'N/A')} @ {event.get('time', 'N/A')}")
            
            print(f"\n  Recommendations:")
            for i, rec in enumerate(data.get('recommendations', [])[:3], 1):
                print(f"    {i}. {rec.get('action', 'N/A')}")
                print(f"       Priority: {rec.get('priority', 'N/A')}")
            
            return True
        else:
            print_error(f"Analysis failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

# ============================================================================
# TEST 7: CHAT WITH AI
# ============================================================================
def test_chat_with_ai():
    print_header("TEST 7: CHAT WITH AI - Q&A")
    
    questions = [
        "What is the current system status?",
        "Which service is having the most errors?",
        "What should I do to fix this incident?",
    ]
    
    try:
        for question in questions:
            print_info(f"Question: {question}")
            
            response = requests.post(
                f"{BASE_URL}/chat/",
                json={"question": question, "logs_context": []},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"AI Response:")
                print(f"  {data.get('answer', 'No response')}\n")
            else:
                print_error(f"Chat failed: {response.status_code}")
        
        return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

# ============================================================================
# TEST 8: INCIDENT STATUS
# ============================================================================
def test_incident_status():
    print_header("TEST 8: INCIDENT STATUS")
    try:
        response = requests.get(f"{BASE_URL}/logs/incident-status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success("Incident status retrieved")
            print(f"  Status: {data.get('status', 'N/A')}")
            print(f"  Error Count: {data.get('error_count', 0)}")
            print(f"  Warning Count: {data.get('warning_count', 0)}")
            print(f"  Info Count: {data.get('info_count', 0)}")
            return True
        else:
            print_error(f"Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
def run_all_tests():
    print(f"\n{BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         RootPilot AI - COMPREHENSIVE TEST SUITE             ║")
    print("║                  Testing All Features                       ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    
    print_info(f"Frontend: {FRONTEND_URL}")
    print_info(f"Backend: {BASE_URL}")
    print_info(f"API Docs: {BASE_URL}/docs\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("Generate Logs", test_generate_logs),
        ("Retrieve Logs", test_retrieve_logs),
        ("Filter by Service", test_filter_logs_by_service),
        ("Filter by Level", test_filter_logs_by_level),
        ("Root Cause Analysis", test_analyze_root_cause),
        ("Chat with AI", test_chat_with_ai),
        ("Incident Status", test_incident_status),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            time.sleep(1)  # Small delay between tests
        except Exception as e:
            print_error(f"Test error: {str(e)}")
            results.append((name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {status} - {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n{GREEN}All tests passed! System is fully operational.{RESET}")
    else:
        print(f"\n{YELLOW}Some tests failed. Please check the output above.{RESET}")

if __name__ == "__main__":
    run_all_tests()
