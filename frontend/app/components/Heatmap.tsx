"use client";

import { useMemo } from "react";
import { motion } from "framer-motion";

interface LogEntry {
  timestamp: string;
  service: string;
  level: string;
  message: string;
}

interface HeatmapProps {
  logs: LogEntry[];
}

interface ServiceStats {
  name: string;
  errorCount: number;
  warningCount: number;
  infoCount: number;
  totalCount: number;
  errorRate: number;
}

const serviceDisplayNames: Record<string, string> = {
  "api-gateway": "API Gateway",
  "auth-service": "Auth Service",
  "payment-service": "Payment Service",
  "database": "Database",
  "redis-cache": "Redis Cache",
};

const getHeatColor = (rate: number) => {
  if (rate >= 0.3) return "bg-red-600";
  if (rate >= 0.15) return "bg-orange-500";
  if (rate >= 0.05) return "bg-yellow-500";
  return "bg-green-600";
};

export default function Heatmap({ logs }: HeatmapProps) {
  const stats = useMemo(() => {
    const serviceMap = new Map<string, ServiceStats>();

    // Initialize services
    Object.keys(serviceDisplayNames).forEach(service => {
      serviceMap.set(service, {
        name: service,
        errorCount: 0,
        warningCount: 0,
        infoCount: 0,
        totalCount: 0,
        errorRate: 0,
      });
    });

    // Count logs
    logs.forEach(log => {
      const service = log.service;
      const statsObj = serviceMap.get(service);
      if (statsObj) {
        statsObj.totalCount++;
        if (log.level === "ERROR") statsObj.errorCount++;
        else if (log.level === "WARNING") statsObj.warningCount++;
        else statsObj.infoCount++;
      }
    });

    // Calculate error rate
    const result: ServiceStats[] = [];
    serviceMap.forEach(stat => {
      stat.errorRate = stat.totalCount > 0 ? stat.errorCount / stat.totalCount : 0;
      result.push(stat);
    });

    // Sort by error rate descending
    result.sort((a, b) => b.errorRate - a.errorRate);
    return result;
  }, [logs]);

  const maxErrorRate = useMemo(() => {
    return Math.max(...stats.map(s => s.errorRate), 0.01);
  }, [stats]);

  const getIntensity = (rate: number) => {
    return (rate / maxErrorRate) * 100;
  };

  return (
    <div className="space-y-3">
      {stats.map((stat, idx) => (
        <motion.div
          key={stat.name}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: idx * 0.05 }}
          className="space-y-1"
        >
          <div className="flex justify-between text-xs">
            <span className="font-medium">{serviceDisplayNames[stat.name]}</span>
            <span className="text-gray-400">
              {stat.errorCount} errors / {stat.totalCount} logs
            </span>
          </div>
          <div className="relative w-full h-8 rounded-md overflow-hidden bg-gray-800">
            <div
              className={`absolute inset-0 ${getHeatColor(stat.errorRate)} opacity-80`}
              style={{ width: `${getIntensity(stat.errorRate)}%` }}
            />
            <div className="absolute inset-0 flex items-center justify-between px-2 text-xs font-mono">
              <span>⚠️ {stat.warningCount}</span>
              <span>❌ {stat.errorCount}</span>
              <span>ℹ️ {stat.infoCount}</span>
            </div>
          </div>
          <p className="text-right text-xs text-gray-500">
            error rate: {(stat.errorRate * 100).toFixed(1)}%
          </p>
        </motion.div>
      ))}
    </div>
  );
}