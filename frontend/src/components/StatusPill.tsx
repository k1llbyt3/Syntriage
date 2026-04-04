"use client";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, Database, Shield, Calendar, ClipboardCheck } from "lucide-react";

interface StatusPillProps {
  status: string;
}

export default function StatusPill({ status }: StatusPillProps) {
  // Map common status words to icons
  const getIcon = () => {
    const s = status.toLowerCase();
    if (s.includes("triage")) return <Activity className="w-4 h-4" />;
    if (s.includes("history") || s.includes("allergy")) return <Database className="w-4 h-4" />;
    if (s.includes("insurance")) return <Shield className="w-4 h-4" />;
    if (s.includes("schedule") || s.includes("availability")) return <Calendar className="w-4 h-4" />;
    if (s.includes("thinking")) return <ClipboardCheck className="w-4 h-4" />;
    return <Activity className="w-4 h-4" />;
  };

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={status}
        initial={{ opacity: 0, y: 10, filter: "blur(10px)" }}
        animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
        exit={{ opacity: 0, y: -10, filter: "blur(10px)" }}
        className="flex items-center gap-2.5 px-4 py-2 glass-card border-primary-teal/40 bg-primary-teal/10 rounded-full"
      >
        <div className="relative">
          <motion.div
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ repeat: Infinity, duration: 2 }}
            className="text-primary-teal-light"
          >
            {getIcon()}
          </motion.div>
        </div>
        <span className="text-[11px] font-bold uppercase tracking-wider text-primary-teal-light">
          {status}
        </span>
      </motion.div>
    </AnimatePresence>
  );
}
