"use client";

import { motion } from "framer-motion";

interface RootCause {
  cause: string;
  confidence: number;
  explanation: string;
  affected_services: string[];
}

interface ConfidenceRankingProps {
  causes: RootCause[];
}

const confidenceColor = (confidence: number) => {
  if (confidence >= 80) return "bg-red-500";
  if (confidence >= 60) return "bg-yellow-500";
  return "bg-blue-500";
};

export default function ConfidenceRanking({ causes }: ConfidenceRankingProps) {
  if (!causes || causes.length === 0) {
    return (
      <div className="text-center py-6 text-gray-500">
        <p>No root cause analysis available.</p>
      </div>
    );
  }

  // Sort by confidence descending
  const sortedCauses = [...causes].sort((a, b) => b.confidence - a.confidence);

  return (
    <div className="space-y-4">
      {sortedCauses.map((cause, idx) => (
        <motion.div
          key={idx}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: idx * 0.1 }}
          className="space-y-1"
        >
          <div className="flex justify-between items-center text-sm">
            <span className="font-medium text-gray-200">{cause.cause}</span>
            <span className="text-xs font-mono text-gray-400">
              {cause.confidence}% confidence
            </span>
          </div>
          <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${cause.confidence}%` }}
              transition={{ duration: 0.6, delay: idx * 0.1 }}
              className={`h-full rounded-full ${confidenceColor(cause.confidence)}`}
            />
          </div>
          {cause.explanation && (
            <p className="text-xs text-gray-400 mt-1">{cause.explanation}</p>
          )}
          {cause.affected_services && cause.affected_services.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1">
              {cause.affected_services.map(service => (
                <span key={service} className="px-1.5 py-0.5 rounded text-xs bg-gray-700 text-gray-300">
                  {service}
                </span>
              ))}
            </div>
          )}
        </motion.div>
      ))}
    </div>
  );
}