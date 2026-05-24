"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Play, RotateCcw } from "lucide-react";

interface ReplayButtonProps {
  onReplay: () => void;
  disabled?: boolean;
}

export default function ReplayButton({ onReplay, disabled = false }: ReplayButtonProps) {
  const [isReplaying, setIsReplaying] = useState(false);

  const handleReplay = () => {
    if (disabled || isReplaying) return;
    setIsReplaying(true);
    onReplay();
    // Reset after animation duration
    setTimeout(() => setIsReplaying(false), 2000);
  };

  return (
    <motion.button
      onClick={handleReplay}
      disabled={disabled || isReplaying}
      className={`
        flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all
        ${disabled ? "opacity-50 cursor-not-allowed bg-gray-700" : "bg-neon-blue/20 hover:bg-neon-blue/30 border border-neon-blue/50"}
      `}
      whileTap={{ scale: 0.95 }}
    >
      {isReplaying ? (
        <>
          <RotateCcw className="w-4 h-4 animate-spin" />
          <span>Replaying...</span>
        </>
      ) : (
        <>
          <Play className="w-4 h-4" />
          <span>Replay Incident</span>
        </>
      )}
    </motion.button>
  );
}