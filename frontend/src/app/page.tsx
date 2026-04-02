"use client";
import { useState } from "react";
import ChatBubble from "@/components/ChatBubble";
import StatusPill from "@/components/StatusPill";
import { useChat } from "@/hooks/useChat";
import { 
  Send, 
  Wifi, 
  WifiOff, 
  LayoutDashboard, 
  Sparkles
} from "lucide-react";
import Link from "next/link";

export default function Home() {
  const { messages, status, sendMessage, isConnected } = useChat();
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim() || !isConnected) return;
    sendMessage(input);
    setInput("");
  };

  return (
    <main className="flex h-screen bg-[#0a0a0b] text-[#e0e0e0] overflow-hidden font-sans">
      
      <section className="flex-1 flex flex-col relative h-full">
        {/* TOP NAV BAR (Minimalist) */}
        <header className="px-6 py-4 border-b border-white/5 flex items-center justify-between bg-[#0a0a0b] z-20">
          <div className="flex items-center gap-2">
            <div className="p-1 bg-white/10 rounded">
              <Sparkles className="w-3 h-3 text-white/50" />
            </div>
            <span className="text-sm font-bold text-white/70 tracking-tight">VitalSync</span>
          </div>

          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              {isConnected ? <Wifi className="w-3 h-3 text-emerald-success" /> : <WifiOff className="w-3 h-3 text-vibrant-coral" />}
              <span className="text-[10px] font-bold uppercase tracking-widest opacity-30">{isConnected ? 'ONLINE' : 'OFFLINE'}</span>
            </div>
            <Link href="/dashboard" className="p-2 hover:bg-white/5 transition-colors text-white/40 hover:text-white rounded-lg">
              <LayoutDashboard className="w-4 h-4" />
            </Link>
          </div>
        </header>

        {/* MESSAGES */}
        <div className="flex-1 overflow-y-auto px-4 py-8 scrollbar-hide">
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.map((msg, i) => (
              <ChatBubble key={i} role={msg.role as any} content={msg.content} />
            ))}
            {status && (
              <div className="flex justify-center py-4">
                <StatusPill status={status} />
              </div>
            )}
          </div>
        </div>

        {/* INPUT BAR */}
        <div className="px-6 py-10 bg-[#0a0a0b]">
          <div className="max-w-3xl mx-auto">
            <div className="flex items-center bg-white/5 p-1 rounded-xl border border-white/10 focus-within:border-white/20 transition-colors">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                disabled={!isConnected}
                placeholder={isConnected ? "Describe symptoms or ask about records..." : "Reconnecting..."}
                className="flex-1 bg-transparent border-none py-3 px-6 text-sm text-white focus:outline-none"
              />
              <button
                onClick={handleSend}
                disabled={!isConnected}
                className="p-3 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-all disabled:opacity-30"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
