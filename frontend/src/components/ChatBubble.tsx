"use client";
import { motion } from "framer-motion";
import { User } from "lucide-react";

import Image from "next/image";

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
          {!isUser && (
            <div className="w-4 h-4 overflow-hidden rounded-full flex items-center justify-center">
              <Image src="/logo.png" alt="Coordinator" width={16} height={16} className="object-cover" />
            </div>
          )}
          <span className="text-[10px] font-semibold uppercase tracking-widest text-white">
            {isUser ? "Patient" : "Smart Coordinator"}
          </span>
          {isUser && <User className="w-3 h-3 text-white" />}
        </div>

        <div
          className={`relative p-5 rounded-3xl ${
            isUser
              ? "bg-primary-teal/80 backdrop-blur-md text-white rounded-tr-none"
              : "glass-card text-foreground rounded-tl-none border-white/10"
          }`}
        >
          <p className="text-sm leading-relaxed font-medium">
            {content}
          </p>
        </div>
      </div>
    </motion.div>
  );
}
