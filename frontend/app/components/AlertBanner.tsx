"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X, AlertTriangle, AlertCircle, Info } from "lucide-react";

interface AlertBannerProps {
  visible: boolean;
  type: "critical" | "warning" | "info";
  title: string;
  message: string;
  onDismiss: () => void;
}

const alertConfig = {
  critical: {
    icon: AlertTriangle,
    bgColor: "bg-red-500/10",
    borderColor: "border-red-500/50",
    textColor: "text-red-400",
    iconColor: "#ff3333",
  },
  warning: {
    icon: AlertCircle,
    bgColor: "bg-yellow-500/10",
    borderColor: "border-yellow-500/50",
    textColor: "text-yellow-400",
    iconColor: "#ffcc00",
  },
  info: {
    icon: Info,
    bgColor: "bg-blue-500/10",
    borderColor: "border-blue-500/50",
    textColor: "text-blue-400",
    iconColor: "#00f3ff",
  },
};

export default function AlertBanner({ visible, type, title, message, onDismiss }: AlertBannerProps) {
  const config = alertConfig[type];
  const Icon = config.icon;

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -50 }}
          className={`fixed top-4 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-md ${config.bgColor} border ${config.borderColor} rounded-lg shadow-lg backdrop-blur-sm`}
        >
          <div className="flex items-start p-4 gap-3">
            <div className="flex-shrink-0">
              <Icon className="w-5 h-5" style={{ color: config.iconColor }} />
            </div>
            <div className="flex-1">
              <h3 className={`font-semibold ${config.textColor}`}>{title}</h3>
              <p className="text-sm text-gray-300 mt-1">{message}</p>
            </div>
            <button
              onClick={onDismiss}
              className="flex-shrink-0 text-gray-400 hover:text-gray-200 transition"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          {/* Pulsing bottom bar for critical alerts */}
          {type === "critical" && (
            <div className="h-1 bg-red-500 animate-pulse rounded-b-lg" />
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}