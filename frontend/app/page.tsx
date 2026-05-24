"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { Toaster, toast } from "react-hot-toast";
import axios from "axios";

// Import shadcn/ui components (we'll create simple versions first)
import LogStream from "./components/LogStream";
import IncidentCard from "./components/IncidentCard";
import Timeline from "./components/Timeline";
import DependencyGraph from "./components/DependencyGraph";
import ConfidenceRanking from "./components/ConfidenceRanking";
import ChatPanel from "./components/ChatPanel";
import Heatmap from "./components/Heatmap";
import AlertBanner from "./components/AlertBanner";
import ReplayButton from "./components/ReplayButton";

// Types
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
  timeline: Array<{
    timestamp: string;
    event: string;
    service?: string;
    details: string;
  }>;
  recommendations: Array<{
    action: string;
    type: string;
    description: string;
    estimated_impact: string;
  }>;
  analysis_timestamp: string;
}

const API_BASE_URL = "http://localhost:8000";

export default function Home() {
  // State
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [incidentStatus, setIncidentStatus] = useState<any>(null);
  const [analysis, setAnalysis] = useState<RootCauseAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Fetch logs from backend
  const fetchLogs = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/logs/?limit=100`);
      if (response.data.success) {
        setLogs(response.data.logs);
      }
    } catch (error) {
      console.error("Failed to fetch logs:", error);
    }
  }, []);

  // Fetch incident status
  const fetchIncidentStatus = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/logs/incident-status`);
      setIncidentStatus(response.data);
      if (response.data.active) {
        toast.custom((t) => (
          <AlertBanner
            visible={t.visible}
            type="critical"
            title="Incident Detected!"
            message={`Active incident: ${response.data.type || "Unknown"} affecting ${response.data.affected_services?.join(", ")}`}
            onDismiss={() => toast.dismiss(t.id)}
          />
        ), { duration: 5000 });
      }
    } catch (error) {
      console.error("Failed to fetch incident status:", error);
    }
  }, []);

  // Trigger root cause analysis
  const triggerAnalysis = useCallback(async () => {
    if (!logs.length) return;
    setIsAnalyzing(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/analyze/`, {
        logs: logs,
        incident_id: incidentStatus?.active ? `incident_${Date.now()}` : undefined,
      });
      if (response.data.success && response.data.analysis) {
        setAnalysis(response.data.analysis);
        setSelectedIncidentId(response.data.analysis.incident_id);
        toast.success("Root cause analysis completed!");
      } else {
        toast.error("Analysis failed: " + (response.data.error || "Unknown error"));
      }
    } catch (error: any) {
      console.error("Analysis error:", error);
      toast.error("Failed to analyze: " + (error.message || "Network error"));
    } finally {
      setIsAnalyzing(false);
    }
  }, [logs, incidentStatus]);

  // Generate more logs (simulate real-time)
  const generateLogs = useCallback(async () => {
    try {
      await axios.post(`${API_BASE_URL}/logs/generate?count=5`);
      await fetchLogs();
    } catch (error) {
      console.error("Failed to generate logs:", error);
    }
  }, [fetchLogs]);

  // Trigger an incident (for demo)
  const triggerIncident = useCallback(async (type: string) => {
    try {
      await axios.post(`${API_BASE_URL}/logs/trigger-incident?incident_type=${type}&duration=15`);
      toast.success(`Incident "${type}" triggered!`);
      await fetchLogs();
      await fetchIncidentStatus();
      // Auto-analyze after triggering incident
      setTimeout(() => triggerAnalysis(), 2000);
    } catch (error) {
      console.error("Failed to trigger incident:", error);
      toast.error("Failed to trigger incident");
    }
  }, [fetchLogs, fetchIncidentStatus, triggerAnalysis]);

  // Replay last incident (use stored analysis)
  const replayIncident = useCallback(() => {
    if (analysis?.timeline) {
      toast.success("Replaying incident timeline...");
      // The ReplayButton component handles animation
    }
  }, [analysis]);

  // Auto-refresh logs every 3 seconds if enabled
  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(() => {
        fetchLogs();
        fetchIncidentStatus();
      }, 3000);
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [autoRefresh, fetchLogs, fetchIncidentStatus]);

  // Initial load
  useEffect(() => {
    fetchLogs();
    fetchIncidentStatus();
  }, [fetchLogs, fetchIncidentStatus]);

  return (
    <main className="min-h-screen p-6">
      <Toaster position="top-right" />
      
      {/* Header */}
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold neon-text">RootPilot AI</h1>
          <p className="text-gray-400 mt-1">AI-Powered Incident Root Cause Analyzer</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => triggerIncident("db_connection_exhaustion")}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition"
          >
            🔥 Trigger DB Incident
          </button>
          <button
            onClick={() => triggerIncident("payment_timeout")}
            className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 rounded-lg transition"
          >
            💸 Trigger Payment Incident
          </button>
          <button
            onClick={() => triggerIncident("redis_memory_exhaustion")}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition"
          >
            📀 Trigger Redis Incident
          </button>
          <button
            onClick={generateLogs}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition"
          >
            Generate Logs
          </button>
          <button
            onClick={triggerAnalysis}
            disabled={isAnalyzing}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition disabled:opacity-50"
          >
            {isAnalyzing ? "Analyzing..." : "Analyze Root Cause"}
          </button>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-4 py-2 rounded-lg transition ${
              autoRefresh ? "bg-gray-700" : "bg-gray-600"
            }`}
          >
            {autoRefresh ? "⏸ Pause" : "▶ Auto"}
          </button>
        </div>
      </div>

      {/* Alert banner for active incident */}
      {incidentStatus?.active && (
        <div className="mb-6">
          <AlertBanner
            visible={true}
            type="critical"
            title={`🚨 Active Incident: ${incidentStatus.type || "Unknown"}`}
            message={`Affected services: ${incidentStatus.affected_services?.join(", ")}`}
            onDismiss={() => {}}
          />
        </div>
      )}

      {/* Main grid: 2 columns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column: Logs + Timeline */}
        <div className="lg:col-span-2 space-y-6">
          {/* Log Stream */}
          <div className="glass-card p-4">
            <h2 className="text-xl font-semibold mb-3 flex items-center gap-2">
              📡 Live Log Stream
              {incidentStatus?.active && <span className="text-red-500 text-sm animate-pulse">● INCIDENT ACTIVE</span>}
            </h2>
            <LogStream logs={logs} />
          </div>

          {/* Timeline + Replay */}
          <div className="glass-card p-4">
            <div className="flex justify-between items-center mb-3">
              <h2 className="text-xl font-semibold">⏱ Incident Timeline</h2>
              <ReplayButton onReplay={replayIncident} />
            </div>
            <Timeline timeline={analysis?.timeline || []} />
          </div>

          {/* Dependency Graph */}
          <div className="glass-card p-4">
            <h2 className="text-xl font-semibold mb-3">🔗 System Dependency Graph</h2>
            <DependencyGraph affectedServices={incidentStatus?.affected_services || []} />
          </div>
        </div>

        {/* Right column: Analysis, Confidence, Chat, Heatmap */}
        <div className="space-y-6">
          {/* Incident Card */}
          <div className="glass-card p-4">
            <IncidentCard
              active={incidentStatus?.active || false}
              type={incidentStatus?.type}
              affectedServices={incidentStatus?.affected_services || []}
              analysis={analysis}
            />
          </div>

          {/* Confidence Ranking */}
          {analysis && analysis.root_causes.length > 0 && (
            <div className="glass-card p-4">
              <h2 className="text-xl font-semibold mb-3">🎯 Root Cause Confidence</h2>
              <ConfidenceRanking causes={analysis.root_causes} />
            </div>
          )}

          {/* Recommendations */}
          {analysis && analysis.recommendations.length > 0 && (
            <div className="glass-card p-4">
              <h2 className="text-xl font-semibold mb-3">💡 Fix Recommendations</h2>
              <div className="space-y-2">
                {analysis.recommendations.map((rec, idx) => (
                  <div key={idx} className="border-l-2 border-neon-blue pl-3 py-1">
                    <p className="font-semibold">{rec.action}</p>
                    <p className="text-sm text-gray-400">{rec.description}</p>
                    <p className="text-xs text-gray-500 mt-1">Impact: {rec.estimated_impact}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Chat Panel */}
          <div className="glass-card p-4">
            <h2 className="text-xl font-semibold mb-3">💬 Ask RootPilot AI</h2>
            <ChatPanel logs={logs} analysis={analysis} incidentId={selectedIncidentId} />
          </div>

          {/* Heatmap */}
          <div className="glass-card p-4">
            <h2 className="text-xl font-semibold mb-3">🔥 Incident Heatmap</h2>
            <Heatmap logs={logs} />
          </div>
        </div>
      </div>
    </main>
  );
}