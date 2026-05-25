import json
from collections import Counter
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from openai import OpenAI

from ..config import Config
from ..models import LogEntry, RootCauseAnalysis
from ..utils.helpers import truncate_string

class ChatEngine:
    """
    Natural language chat interface for incident Q&A.
    Allows users to ask questions about logs, root causes, and recommendations.
    """
    
    def __init__(self):
        self.provider = Config.LLM_PROVIDER
        self.conversation_history = {}  # Store history per session/incident
        self.model = None
        self.client = None
        self.gemini_model_names = ['gemini-1.5-flash', 'gemini-pro']
        
        try:
            if self.provider == "gemini":
                if not Config.GEMINI_API_KEY:
                    print("Warning: GEMINI_API_KEY is not set. Chat fallback responses will be used.")
                    return
                genai.configure(api_key=Config.GEMINI_API_KEY)
                # Try models in order of preference
                for model_name in self.gemini_model_names:
                    self.model = genai.GenerativeModel(model_name)
                    break
                
                if not self.model:
                    self.model = genai.GenerativeModel('gemini-pro')
            elif self.provider == "openai":
                if not Config.OPENAI_API_KEY:
                    print("Warning: OPENAI_API_KEY is not set. Chat fallback responses will be used.")
                    return
                self.client = OpenAI(api_key=Config.OPENAI_API_KEY, timeout=15.0)
        except Exception as e:
            print(f"Warning: ChatEngine LLM initialization error: {e}. Fallback responses will be used.")
    
    def _build_chat_prompt(self, question: str, logs: List[LogEntry], analysis: Optional[RootCauseAnalysis] = None) -> str:
        """Build a contextual prompt for the LLM."""
        
        # Format recent logs (last 20)
        log_texts = []
        for log in logs[-20:]:
            log_texts.append(f"[{log.timestamp}] {log.service.value} | {log.level} | {log.message}")
        logs_str = "\n".join(log_texts)
        
        # Include analysis if available
        analysis_str = ""
        if analysis:
            analysis_str = f"""
=== ROOT CAUSE ANALYSIS ===
Summary: {analysis.summary}
Top Root Cause: {analysis.root_causes[0].cause if analysis.root_causes else "Unknown"} (confidence {analysis.root_causes[0].confidence if analysis.root_causes else 0}%)
Recommendations: {', '.join([r.action for r in analysis.recommendations[:2]])}
"""
        
        prompt = f"""You are RootPilot AI, an SRE assistant helping debug system incidents.

=== RECENT LOGS ===
{logs_str}
{analysis_str}
=== END OF CONTEXT ===

User Question: {question}

Instructions:
- Answer concisely and helpfully (2-4 sentences usually).
- Use the logs and analysis to inform your answer.
- If you don't know, say so honestly.
- Suggest specific actions when appropriate.
- Keep a professional but friendly tone.
- Do NOT mention that you are an AI language model.

Answer:"""
        return prompt
    
    async def chat(self, question: str, logs: List[LogEntry], analysis: Optional[RootCauseAnalysis] = None, session_id: Optional[str] = None) -> str:
        """
        Process a chat question and return an answer.
        
        Args:
            question: User's natural language question
            logs: Current logs for context
            analysis: Optional root cause analysis for richer answers
            session_id: Optional session identifier for conversation history
            
        Returns:
            String answer
        """
        if not question or not question.strip():
            return "Please ask a question about the incident or logs."
        
        prompt = self._build_chat_prompt(question, logs, analysis)
        
        # For OpenAI, we can include conversation history if session_id provided
        if session_id and self.provider == "openai":
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
            messages = self.conversation_history[session_id] + [{"role": "user", "content": prompt}]
        else:
            messages = [{"role": "user", "content": prompt}]
        
        try:
            if not self.model and not self.client:
                # LLM not initialized, provide helpful fallback
                return self._fallback_answer(question, logs, analysis)
            
            if self.provider == "gemini" and self.model:
                answer = self._generate_with_gemini(prompt).strip()
            elif self.provider == "openai" and self.client:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=300
                )
                answer = response.choices[0].message.content.strip()
            else:
                return "The configured LLM provider is not properly initialized. Please check your backend configuration."
            
            # Store in history if session_id provided (OpenAI)
            if session_id and self.provider == "openai":
                self.conversation_history[session_id].append({"role": "user", "content": question})
                self.conversation_history[session_id].append({"role": "assistant", "content": answer})
                # Limit history length
                if len(self.conversation_history[session_id]) > 10:
                    self.conversation_history[session_id] = self.conversation_history[session_id][-10:]
            
            return answer
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Specific error handling for common issues
            if "not found" in error_msg or "api_version" in error_msg or "model" in error_msg:
                return self._fallback_answer(question, logs, analysis)
            elif "invalid_api_key" in error_msg or "unauthorized" in error_msg or "401" in error_msg:
                return self._fallback_answer(question, logs, analysis)
            elif "rate_limit" in error_msg or "429" in error_msg:
                return self._fallback_answer(question, logs, analysis)
            elif "timeout" in error_msg:
                return self._fallback_answer(question, logs, analysis)
            else:
                # Generic fallback with helpful context
                return self._fallback_answer(question, logs, analysis)

    def _generate_with_gemini(self, prompt: str) -> str:
        """Try configured Gemini model names before falling back."""
        last_error = None
        for model_name in self.gemini_model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                last_error = e
        raise last_error or RuntimeError("No Gemini models were available")

    def _fallback_answer(
        self,
        question: str,
        logs: List[LogEntry],
        analysis: Optional[RootCauseAnalysis] = None
    ) -> str:
        """Local, deterministic answer when the configured LLM is unavailable."""
        level_counts = Counter(log.level for log in logs)
        service_errors = Counter(log.service.value for log in logs if log.level == "ERROR")
        service_warnings = Counter(log.service.value for log in logs if log.level == "WARNING")
        top_error_service = service_errors.most_common(1)
        top_warning_service = service_warnings.most_common(1)
        latest_problem = next((log for log in reversed(logs) if log.level in {"ERROR", "WARNING"}), None)

        if analysis and analysis.root_causes:
            top_cause = analysis.root_causes[0]
            return (
                f"The current analysis points to {top_cause.cause} "
                f"with {top_cause.confidence}% confidence. "
                f"Start with {analysis.recommendations[0].action.lower() if analysis.recommendations else 'checking the affected service logs'}."
            )

        if top_error_service:
            service, count = top_error_service[0]
            latest_text = f" Latest signal: {latest_problem.service.value} reported \"{truncate_string(latest_problem.message, 90)}\"." if latest_problem else ""
            return (
                f"I found {count} error log{'s' if count != 1 else ''} in {service}. "
                f"Across the current window there are {level_counts.get('ERROR', 0)} errors and {level_counts.get('WARNING', 0)} warnings."
                f"{latest_text}"
            )

        if top_warning_service:
            service, count = top_warning_service[0]
            return (
                f"No critical errors are visible in the current logs, but {service} has {count} warning "
                f"log{'s' if count != 1 else ''}. I would watch that service first and generate more logs if the issue continues."
            )

        return "The current logs look healthy: no errors or warnings are visible in the latest sample."
    
    def get_suggested_questions(self, logs: List[LogEntry], analysis: Optional[RootCauseAnalysis] = None) -> List[str]:
        """Generate suggested follow-up questions based on context."""
        questions = []
        
        # Based on analysis
        if analysis and analysis.root_causes:
            top_cause = analysis.root_causes[0].cause
            questions.append(f"Why did {top_cause.split()[0]} happen?")
            questions.append("How can I prevent this in the future?")
        
        # Based on logs
        error_services = set()
        for log in logs[-20:]:
            if log.level == "ERROR":
                error_services.add(log.service.value)
        if error_services:
            services_str = ", ".join(list(error_services)[:2])
            questions.append(f"What's wrong with {services_str}?")
        
        # Generic helpful questions
        if not questions:
            questions = [
                "What is the current system status?",
                "Show me critical errors",
                "What should I do first?"
            ]
        
        return questions[:4]

# Singleton instance
chat_engine = ChatEngine()
