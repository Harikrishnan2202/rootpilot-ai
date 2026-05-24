"use client";

import { useEffect, useRef } from "react";
import { cn } from "../lib/utils";

interface LogEntry {
  timestamp: string;
  service: string;
  level: string;
  message: string;
}

interface LogStreamProps {
  logs: LogEntry[];
  maxHeight?: string;
}

const levelColors = {
  INFO: "text-blue-400",
  WARNING: "text-yellow-400",
  ERROR: "text-red-400",
  DEBUG: "text-gray-400",
};

const serviceColors: Record<string, string> = {
  "api-gateway": "bg-purple-500/20 text-purple-300 border-purple-500/30",
  "auth-service": "bg-indigo-500/20 text-indigo-300 border-indigo-500/30",
  "payment-service": "bg-green-500/20 text-green-300 border-green-500/30",
  "database": "bg-cyan-500/20 text-cyan-300 border-cyan-500/30",
  "redis-cache": "bg-red-500/20 text-red-300 border-red-500/30",
};

export default function LogStream({ logs, maxHeight = "400px" }: LogStreamProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  const getServiceBadge = (service: string) => {
    const colorClass = serviceColors[service] || "bg-gray-500/20 text-gray-300 border-gray-500/30";
    return (
      <span className={cn("px-2 py-0.5 rounded text-xs font-mono border", colorClass)}>
        {service}
      </span>
    );
  };

  const getLevelBadge = (level: string) => {
    const color = levelColors[level as keyof typeof levelColors] || "text-gray-400";
    return (
      <span className={cn("font-mono text-xs font-bold", color)}>
        [{level}]
      </span>
    );
  };

  return (
    <div
      ref={containerRef}
      className="bg-black/50 rounded-lg p-3 font-mono text-sm overflow-y-auto"
      style={{ maxHeight }}
    >
      {logs.length === 0 ? (
        <div className="text-gray-500 text-center py-8">
          No logs yet. Click &quot;Generate Logs&quot; to start streaming.
        </div>
      ) : (
        <div className="space-y-1">
          {logs.map((log, idx) => (
            <div
              key={idx}
              className="log-line font-mono text-xs py-1 border-b border-gray-800/50 hover:bg-white/5 transition-colors"
            >
              <div className="flex flex-wrap items-start gap-2">
                <span className="text-gray-500 shrink-0">{log.timestamp}</span>
                {getServiceBadge(log.service)}
                {getLevelBadge(log.level)}
                <span className="text-gray-300 break-all flex-1">{log.message}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
