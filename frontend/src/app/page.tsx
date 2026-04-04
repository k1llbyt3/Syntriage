"use client";
import { useState, useRef, useEffect } from "react";
import ChatBubble from "@/components/ChatBubble";
import StatusPill from "@/components/StatusPill";
import TimeSlot from "@/components/TimeSlot";
import { useChat } from "@/hooks/useChat";
import { 
  Send, 
  WifiOff, 
  Calendar,
  Mic,
  X
} from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";

export default function Home() {
  const { messages, status, activeAgent, widgetData, sendMessage, resetChat, isConnected } = useChat();
  const [input, setInput] = useState("");
  const [showModal, setShowModal] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const handleSend = () => {
    if (!input.trim() || !isConnected) return;
    sendMessage(input);
    setInput("");
  };

  const handleTimeSelect = (time: string) => {
    if (widgetData?.type === "time_slots") {
      const data = widgetData.data as { date: string };
      sendMessage(`I would like to book the ${time} slot on ${data.date}`);
    }
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, status, widgetData]);

  return (
    <main className="relative min-h-screen overflow-hidden bg-neutral-950 flex flex-col font-sans text-[#e0e0e0]">
      {/* MOLECULAR BACKGROUND IMAGE LAYER (WARM OBSIDIAN) */}
      <div 
        className="absolute inset-0 z-0 opacity-30 pointer-events-none transition-opacity duration-1000 bg-[position:center_calc(50%+4px)] bg-no-repeat bg-[size:64%] blur-[3.5px]"
        style={{ 
          backgroundImage: 'url("/warm.png")',
        }} 
      />

      {/* GLOWING ORB BACKGROUND (Warm Amber) */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-amber-950/10 blur-[120px] rounded-full pointer-events-none z-10 opacity-70" />
      
      {/* SECONDARY BALANCE GLOW (Warm Charcoal) */}
      <div className="absolute bottom-[-20%] right-[-10%] w-[60%] h-[60%] bg-orange-950/5 blur-[150px] rounded-full pointer-events-none z-10 opacity-40 transition-all" />

      {/* TOP HEADER CLEAN UNIFIED GRID */}
      <header className="absolute top-4 left-0 w-full flex items-center justify-between px-6 z-[40]">
        
        {/* Left Side: Logo and Title Aligned */}
        <div className="flex items-center gap-6">
          <Image src="/logo.png" alt="Logo" width={80} height={80} className="object-contain" />
          <h1 className="text-3xl font-black italic tracking-[0.3em] text-white">
            SYNTRIAGE
          </h1>
        </div>

        {/* Right Side: Physician Hub Button */}
        <div className="flex items-center gap-3">
          <button 
            onClick={resetChat}
            className="px-6 py-3 bg-white/5 hover:bg-vibrant-coral/10 border border-white/10 hover:border-vibrant-coral/40 rounded-full transition-all group backdrop-blur-2xl shadow-xl flex items-center justify-center"
          >
            <span className="text-[11px] font-bold uppercase tracking-[0.25em] text-white/40 group-hover:text-vibrant-coral transition-colors">
              RESET SESSION
            </span>
          </button>
          <Link 
            href="/dashboard" 
            className="px-8 py-3 bg-white/10 hover:bg-white/20 border border-white/10 hover:border-primary-teal/40 rounded-full transition-all group backdrop-blur-2xl shadow-xl flex items-center justify-center"
          >
            <span className="text-[11px] font-bold uppercase tracking-[0.25em] text-white/60 group-hover:text-primary-teal-light transition-colors">
              PHYSICIAN HUB
            </span>
          </Link>
        </div>
      </header>

      {/* CUSTOM MODAL */}
      <AnimatePresence>
        {showModal && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowModal(false)}
              className="absolute inset-0 bg-black/80 backdrop-blur-sm"
            />
            <motion.div 
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="relative glass-container p-8 max-w-md w-full border border-white/10"
            >
              <button 
                onClick={() => setShowModal(false)}
                className="absolute top-4 right-4 p-2 hover:bg-white/5 rounded-lg transition-colors"
              >
                <X className="w-4 h-4 text-white/40" />
              </button>
              
              <div className="flex flex-col items-center text-center">
                <div className="w-16 h-16 bg-primary-teal/20 rounded-2xl flex items-center justify-center mb-6">
                  <Mic className="w-8 h-8 text-primary-teal-light" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2 uppercase tracking-wide">Voice Logic Locked</h3>
                <p className="text-sm text-white/40 leading-relaxed mb-8 tracking-normal">
                  Voice input is currently being optimized for high-fidelity clinical environments and is not yet available in this session.
                </p>
                <button 
                  onClick={() => setShowModal(false)}
                  className="w-full py-4 bg-primary-teal hover:bg-primary-teal-light text-white font-bold uppercase tracking-[0.3em] text-[10px] rounded-xl transition-all"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      <section className="flex-1 flex flex-col relative h-full pt-20">
        {/* MESSAGES */}
        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto px-6 py-10 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent hover:scrollbar-thumb-white/20 transition-all"
        >
          <div className="max-w-4xl mx-auto space-y-8">
            <AnimatePresence initial={false}>
              {messages.map((msg, i) => (
                <ChatBubble key={i} role={msg.role} content={msg.content} />
              ))}
            </AnimatePresence>
            
            {status && (
              <div className="flex justify-start py-4">
                <StatusPill status={status} />
              </div>
            )}

            {/* WIDGETS */}
            <AnimatePresence>
              {widgetData && widgetData.type === "time_slots" && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  className="glass-container p-8 max-w-2xl"
                >
                  <div className="flex items-center gap-4 mb-6">
                    <div className="p-3 bg-primary-teal/20 rounded-xl">
                      <Calendar className="w-6 h-6 text-primary-teal-light" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-white">Select Appointment Window</h3>
                      <p className="text-xs text-white/40 font-medium uppercase tracking-widest">Available Slots for {(widgetData.data as {date: string}).date}</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 sm:grid-cols-4 gap-3">
                    {(widgetData.data as {available_slots?: string[]}).available_slots?.map((slot: string) => (
                      <TimeSlot 
                        key={slot} 
                        time={slot} 
                        onSelect={handleTimeSelect} 
                      />
                    ))}
                  </div>
                  
                  {(!(widgetData.data as {available_slots?: string[]}).available_slots || (widgetData.data as {available_slots: string[]}).available_slots.length === 0) && (
                    <p className="text-sm text-vibrant-coral font-bold py-4">No slots available or database error occurred.</p>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* THE TACTILE HARDWARE GLASS CONTAINER */}
        <div className="px-8 py-12 relative z-30">
          <div className="max-w-4xl mx-auto mb-4 px-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-primary-teal animate-pulse" />
              <span className="text-[10px] font-black uppercase tracking-[0.2em] text-white/40">
                ACTIVE AGENT: <span className="text-primary-teal-light">{activeAgent}</span>
              </span>
            </div>
            {!isConnected && (
              <span className="text-[10px] font-bold uppercase tracking-widest text-vibrant-coral animate-pulse flex items-center gap-2">
                <WifiOff className="w-3 h-3" /> OFFLINE
              </span>
            )}
          </div>
          <div className="flex items-center w-full max-w-4xl mx-auto rounded-3xl relative overflow-hidden border border-white/10 bg-white/5 backdrop-blur-2xl shadow-[0_8px_32px_0_rgba(0,0,0,0.5)] transition-all group focus-within:shadow-[0_8px_40px_0_rgba(0,0,0,0.7)]">
            
            {/* Edge Glare Effect */}
            <div className="absolute inset-0 pointer-events-none ring-1 ring-inset ring-white/10 rounded-[inherit] z-20" />
            
            {/* Inner Glow Effect */}
            <div className="absolute inset-0 pointer-events-none bg-gradient-to-br from-white/10 to-transparent opacity-30 z-10" />

            {/* Content Layer */}
            <div className="flex items-center w-full p-2 relative z-30">
              <textarea
                rows={1}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = "auto";
                  target.style.height = `${Math.min(target.scrollHeight, 200)}px`;
                }}
                disabled={!isConnected}
                placeholder={isConnected ? "Describe symptoms, ask about your history, or schedule a slot..." : "Reconnecting to clinical hub..."}
                className="flex-1 px-6 py-4 text-sm text-white bg-transparent outline-none placeholder-white/20 resize-none min-h-[56px] max-h-[200px] scrollbar-hide"
              />

              {/* Mic and Send Buttons */}
              <div className="flex gap-2 pr-2 pb-1">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowModal(true)}
                  className="p-4 bg-white/5 text-primary-teal-light rounded-xl hover:bg-white/10 transition-all"
                >
                  <Mic className="w-5 h-5" />
                </motion.button>
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || !isConnected}
                  className="p-4 bg-gradient-to-tr from-primary-teal to-primary-teal-light text-white rounded-xl transition-all shadow-[0_0_20px_rgba(13,148,136,0.3)] hover:shadow-[0_0_30px_rgba(13,148,136,0.4)] active:scale-95 disabled:opacity-20 disabled:grayscale cursor-pointer"
                >
                  <Send className="w-5 h-5 flex-shrink-0" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
