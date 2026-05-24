"use client";

import { motion } from "framer-motion";
import { cn } from "../lib/utils";

interface TimelineEvent {
  timestamp: string;
  event: string;
  service?: string;
  details: string;
}

interface TimelineProps {
  timeline: TimelineEvent[];
  className?: string;
}

const eventIcons: Record<string, string> = {
  ERROR: "❌",
  WARNING: "⚠️",
  INFO: "ℹ️",
  default: "📌",
};

const eventColors: Record<string, string> = {
  ERROR: "border-red-500 bg-red-500/10",
  WARNING: "border-yellow-500 bg-yellow-500/10",
  INFO: "border-blue-500 bg-blue-500/10",
};

export default function Timeline({ timeline, className }: TimelineProps) {
  if (!timeline || timeline.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No timeline events yet.</p>
        <p className="text-xs mt-1">Run root cause analysis to generate incident timeline.</p>
      </div>
    );
  }

  return (
    <div className={cn("relative pl-6 space-y-4", className)}>
      {/* Vertical line */}
      <div className="absolute left-2 top-0 bottom-0 w-0.5 bg-gradient-to-b from-neon-blue via-purple-500 to-neon-pink" />
      
      {timeline.map((event, idx) => {
        const icon = eventIcons[event.event] || eventIcons.default;
        const colorClass = eventColors[event.event] || eventColors.INFO;
        
        return (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="relative"
          >
            {/* Dot on timeline */}
            <div className={cn(
              "absolute -left-[1.85rem] top-1 w-3 h-3 rounded-full border-2",
              event.event === "ERROR" ? "bg-red-500 border-red-300" :
              event.event === "WARNING" ? "bg-yellow-500 border-yellow-300" :
              "bg-blue-500 border-blue-300"
            )} />
            
            {/* Event card */}
            <div className={cn("rounded-lg border p-3 ml-2", colorClass)}>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-lg">{icon}</span>
                <span className="text-xs font-mono text-gray-400">{event.timestamp}</span>
                <span className={cn(
                  "px-2 py-0.5 rounded text-xs font-bold",
                  event.event === "ERROR" ? "bg-red-500/30 text-red-200" :
                  event.event === "WARNING" ? "bg-yellow-500/30 text-yellow-200" :
                  "bg-blue-500/30 text-blue-200"
                )}>
                  {event.event}
                </span>
                {event.service && (
                  <span className="px-2 py-0.5 rounded text-xs bg-white/10 text-gray-300">
                    {event.service}
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-200 mt-2 leading-relaxed">{event.details}</p>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}