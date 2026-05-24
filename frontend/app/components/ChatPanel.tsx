"use client";

import { useState, useRef, useEffect } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { Send, Loader2 } from "lucide-react";

interface LogEntry {
  timestamp: string;
  service: string;
  level: string;
  message: string;
}

interface RootCauseAnalysis {
  incident_id: string;
  summary: string;
  root_causes: Array<{
    cause: string;
    confidence: number;
    explanation: string;
    affected_services: string[];
  }>;
  recommendations: Array<{
    action: string;
    type: string;
    description: string;
    estimated_impact: string;
  }>;
}

interface ChatPanelProps {
  logs: LogEntry[];
  analysis?: RootCauseAnalysis | null;
  incidentId?: string | null;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const API_BASE_URL = "http://localhost:8000";

// Client-side timestamp renderer to avoid hydration mismatch
function ClientTimestamp({ timestamp }: { timestamp: Date }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <span className="text-xs text-gray-500">--:-- --</span>;
  }

  return <span className="text-xs text-gray-500">{timestamp.toLocaleTimeString()}</span>;
}

export default function ChatPanel({ logs, analysis, incidentId }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Hi! I'm RootPilot AI. Ask me anything about the incident, logs, or how to fix issues.",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Fetch suggested questions when logs or analysis change
  useEffect(() => {
    const fetchSuggestions = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/chat/suggestions`, {
          params: { session_id: incidentId || "default" },
        });
        if (response.data.success) {
          setSuggestions(response.data.suggestions.slice(0, 3));
        }
      } catch (error) {
        console.error("Failed to fetch suggestions:", error);
        setSuggestions([
          "What is the current system status?",
          "What caused the last incident?",
          "How can I prevent this?",
        ]);
      }
    };
    if (logs.length > 0) {
      fetchSuggestions();
    }
  }, [logs, analysis, incidentId]);

  const sendMessage = async (question: string) => {
    if (!question.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: question,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Prepare logs context (last 50 logs)
      const logsContext = logs.slice(-50);

      const response = await axios.post(`${API_BASE_URL}/chat/`, {
        question: question,
        incident_id: incidentId || undefined,
        logs_context: logsContext,
      });

      if (response.data.success) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: response.data.answer,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        throw new Error(response.data.error || "Failed to get answer");
      }
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `⚠️ Sorry, I couldn't process your question. Error: ${error.message || "Network error"}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion);
  };

  return (
    <div className="flex flex-col h-[400px]">
      {/* Messages container */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-3 pr-2">
        {messages.map((msg) => (
          <motion.div
            key={msg.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-lg px-3 py-2 ${
                msg.role === "user"
                  ? "bg-neon-blue/20 text-white border border-neon-blue/30"
                  : "bg-gray-800/50 text-gray-200 border border-gray-700"
              }`}
            >
              <p className="text-sm">{msg.content}</p>
              <ClientTimestamp timestamp={msg.timestamp} />
            </div>
          </motion.div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-800/50 rounded-lg px-3 py-2 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-neon-blue" />
              <span className="text-sm text-gray-400">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested questions */}
      {suggestions.length > 0 && messages.length < 3 && (
        <div className="mb-3">
          <p className="text-xs text-gray-500 mb-2">Suggested questions:</p>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => handleSuggestionClick(suggestion)}
                className="text-xs px-2 py-1 rounded-full bg-gray-800 hover:bg-gray-700 text-gray-300 transition"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input form */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about the incident..."
          className="flex-1 px-3 py-2 rounded-lg bg-gray-900 border border-gray-700 text-white text-sm focus:outline-none focus:border-neon-blue"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="px-3 py-2 rounded-lg bg-neon-blue/20 hover:bg-neon-blue/30 border border-neon-blue/50 disabled:opacity-50 transition"
        >
          <Send className="w-4 h-4 text-neon-blue" />
        </button>
      </form>
    </div>
  );
}