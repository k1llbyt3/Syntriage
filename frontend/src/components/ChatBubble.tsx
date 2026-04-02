"use client";
import { motion } from "framer-motion";
import { User, ShieldCheck, HeartPulse } from "lucide-react";

interface ChatBubbleProps {
  content: string;
  role: "user" | "assistant";
}

export default function ChatBubble({ content, role }: ChatBubbleProps) {
  const isUser = role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, x: isUser ? 20 : -20, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      transition={{ type: "spring", damping: 20, stiffness: 100 }}
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-6 group`}
    >
      <div className={`flex flex-col ${isUser ? "items-end" : "items-start"} max-w-[85%]`}>
        {/* Identity Label */}
        <div className="flex items-center gap-2 mb-1 px-2 opacity-40 group-hover:opacity-100 transition-opacity">
          {!isUser && <HeartPulse className="w-3 h-3 text-primary-teal-light" />}
          <span className="text-[10px] font-bold uppercase tracking-widest text-white">
            {isUser ? "Patient" : "Smart Coordinator"}
          </span>
          {isUser && <User className="w-3 h-3 text-white" />}
        </div>

        <div
          className={`relative p-5 rounded-3xl ${
            isUser
              ? "bg-primary-teal/80 backdrop-blur-md text-white rounded-tr-none shadow-[0_0_20px_rgba(13,148,136,0.3)]"
              : "glass-card text-foreground rounded-tl-none border-white/10 shadow-[0_0_15px_rgba(255,255,255,0.05)]"
          }`}
        >
          <p className="text-sm leading-relaxed font-medium tracking-tight">
            {content}
          </p>
          
          {/* Subtle Glow for Assistant */}
          {!isUser && (
            <div className="absolute -inset-0.5 bg-primary-teal/10 blur-xl opacity-0 group-hover:opacity-100 transition-opacity rounded-3xl -z-10" />
          )}
        </div>
      </div>
    </motion.div>
  );
}
