"use client";

import { useEffect, useState } from "react";
import { cn } from "../lib/utils";

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

// Client-side timestamp renderer to avoid hydration mismatch
function ClientTimestamp({ timestamp }: { timestamp: string }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <span className="text-xs text-gray-500">--:-- -- ----</span>;
  }

  return <span className="text-xs text-gray-500">{new Date(timestamp).toLocaleString()}</span>;
}

interface IncidentCardProps {
  active: boolean;
  type?: string | null;
  affectedServices: string[];
  analysis?: RootCauseAnalysis | null;
}

export default function IncidentCard({ active, type, affectedServices, analysis }: IncidentCardProps) {
  const getSeverityBadge = () => {
    if (!active) {
      return (
        <span className="px-3 py-1 rounded-full text-sm bg-green-500/20 text-green-400 border border-green-500/30">
          ✅ System Healthy
        </span>
      );
    }
    return (
      <span className="px-3 py-1 rounded-full text-sm bg-red-500/20 text-red-400 border border-red-500/30 animate-pulse">
        🔴 Critical Incident
      </span>
    );
  };

  const formatType = (t: string) => {
    return t
      .split("_")
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  return (
    <div className="space-y-4">
      {/* Status Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Incident Status</h3>
        {getSeverityBadge()}
      </div>

      {/* Active Incident Details */}
      {active && type && (
        <div className="space-y-3">
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30">
            <p className="text-sm font-medium text-red-400">Active Incident</p>
            <p className="text-lg font-bold mt-1">{formatType(type)}</p>
            {affectedServices.length > 0 && (
              <div className="mt-2">
                <p className="text-xs text-gray-400">Affected Services:</p>
                <div className="flex flex-wrap gap-2 mt-1">
                  {affectedServices.map(service => (
                    <span key={service} className="px-2 py-0.5 rounded text-xs bg-red-500/20 text-red-300">
                      {service}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* AI Analysis Summary */}
      {analysis && (
        <div className="space-y-3 mt-4 pt-4 border-t border-gray-800">
          <div className="flex items-center gap-2">
            <span className="text-lg">🤖</span>
            <h3 className="text-lg font-semibold">AI Analysis Summary</h3>
          </div>
          <div className="p-3 rounded-lg bg-neon-blue/5 border border-neon-blue/20">
            <p className="text-sm text-gray-300 leading-relaxed">{analysis.summary}</p>
            <p className="text-xs text-gray-500 mt-2">
              Analyzed at: <ClientTimestamp timestamp={analysis.analysis_timestamp} />
            </p>
          </div>

          {/* Top Root Cause Preview */}
          {analysis.root_causes.length > 0 && (
            <div className="mt-3">
              <p className="text-xs text-gray-400 mb-1">Top Root Cause:</p>
              <div className="flex items-center justify-between p-2 rounded bg-yellow-500/10 border border-yellow-500/30">
                <span className="text-sm font-medium">{analysis.root_causes[0].cause}</span>
                <span className="text-xs text-yellow-400">{analysis.root_causes[0].confidence}% confidence</span>
              </div>
            </div>
          )}

          {/* Quick Recommendation */}
          {analysis.recommendations.length > 0 && (
            <div className="mt-3">
              <p className="text-xs text-gray-400 mb-1">Top Recommendation:</p>
              <div className="p-2 rounded bg-green-500/10 border border-green-500/30">
                <p className="text-sm">{analysis.recommendations[0].action}</p>
                <p className="text-xs text-gray-400 mt-1">{analysis.recommendations[0].description}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* No Analysis Placeholder */}
      {!analysis && (
        <div className="text-center py-6 text-gray-500">
          <p className="text-sm">No analysis yet.</p>
          <p className="text-xs mt-1">Click &quot;Analyze Root Cause&quot; to run AI analysis.</p>
        </div>
      )}
    </div>
  );
}
