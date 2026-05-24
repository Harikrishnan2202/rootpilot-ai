import json
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
        
        try:
            if self.provider == "gemini":
                genai.configure(api_key=Config.GEMINI_API_KEY)
                # Try models in order of preference
                model_names = ['gemini-1.5-flash-latest', 'gemini-1.5-flash', 'gemini-pro', 'gemini-pro-vision']
                for model_name in model_names:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        break
                    except Exception:
                        continue
                
                if not self.model:
                    self.model = genai.GenerativeModel('gemini-pro')
            elif self.provider == "openai":
                self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
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
                return "The AI assistant is currently being configured. Please ensure your API keys are set in the .env file and restart the backend server."
            
            if self.provider == "gemini" and self.model:
                response = self.model.generate_content(prompt)
                answer = response.text.strip()
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
                return "The AI model is currently unavailable. The backend may not have valid API credentials configured. Please check your GEMINI_API_KEY or OPENAI_API_KEY in the .env file."
            elif "invalid_api_key" in error_msg or "unauthorized" in error_msg or "401" in error_msg:
                return "Authentication failed with the AI service. Please verify your API key is valid and properly configured in the .env file."
            elif "rate_limit" in error_msg or "429" in error_msg:
                return "The AI service is rate-limited. Please wait a moment and try again."
            elif "timeout" in error_msg:
                return "The AI service request timed out. Please try again."
            else:
                # Generic fallback with helpful context
                return f"The AI service encountered an error. Please ensure your API keys are configured correctly. Error: {str(e)[:80]}"
    
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