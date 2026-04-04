"use client";
import { useState, useEffect, useRef, useCallback } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface WidgetData {
  type: string;
  data: Record<string, unknown>;
}

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([
    { 
      role: "assistant", 
      content: "Welcome to Syntriage. I am your Clinical Coordinator. To assist you today, I will need your Name and Email to access your records. Please describe your symptoms or let me know if you would like to schedule an appointment." 
    }
  ]);
  const [status, setStatus] = useState<string | null>(null);
  const [activeAgent, setActiveAgent] = useState<string>("Coordinator");
  const [widgetData, setWidgetData] = useState<WidgetData | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    
    const connect = () => {
      // Connect to WebSocket
      const defaultWsUrl = window.location.protocol === "https:" ? `wss://${window.location.host}/ws/chat` : `ws://127.0.0.1:8000/ws/chat`;
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || defaultWsUrl;
      const socket = new WebSocket(wsUrl);
      socketRef.current = socket;

      socket.onopen = () => {
        setIsConnected(true);
        console.log("WebSocket connected");
      };

      socket.onclose = () => {
        setIsConnected(false);
        console.log("WebSocket disconnected, retrying in 3s...");
        if (timeoutId) clearTimeout(timeoutId);
        timeoutId = setTimeout(connect, 3000);
      };
      
      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === "status") {
            const content = data.content;
            setStatus(content);
            
            // DYNAMIC AGENT DETECTION (PREDICTIVE)
            if (content.toLowerCase().includes("triage") || content.toLowerCase().includes("symptoms")) {
              setActiveAgent("Triage Specialist");
            } else if (content.toLowerCase().includes("history") || content.toLowerCase().includes("records")) {
              setActiveAgent("History Specialist");
            } else if (content.toLowerCase().includes("scheduling") || content.toLowerCase().includes("calendar") || content.toLowerCase().includes("appointment")) {
              setActiveAgent("Scheduling Coordinator");
            } else if (content.toLowerCase().includes("insurance") || content.toLowerCase().includes("billing")) {
              setActiveAgent("Insurance Specialist");
            } else if (content.toLowerCase().includes("consensus") || content.toLowerCase().includes("cross-referencing")) {
              setActiveAgent("Clinical Consensus Hub");
            } else if (content.toLowerCase().includes("orchestrating")) {
              setActiveAgent("Clinical Coordinator");
            }
          } else if (data.type === "agent_role") {
            // EXPLICIT AGENT IDENTITY (FROM BACKEND)
            setActiveAgent(data.content);
          } else if (data.type === "message") {
            setMessages(prev => [...prev, { role: "assistant", content: data.content }]);
            setStatus(null);
          } else if (data.type === "widget") {
            if (data.content.type === "status_update") {
              const content = data.content.content;
              setStatus(content);
              
              // Deduce active agent based on status content
              if (content.toLowerCase().includes("symptoms") || content.toLowerCase().includes("triage")) {
                setActiveAgent("Triage Specialist");
              } else if (content.toLowerCase().includes("records") || content.toLowerCase().includes("history")) {
                setActiveAgent("History Specialist");
              } else if (content.toLowerCase().includes("calendar") || content.toLowerCase().includes("scheduling")) {
                setActiveAgent("Scheduling Coordinator");
              } else if (content.toLowerCase().includes("insurance") || content.toLowerCase().includes("billing")) {
                setActiveAgent("Insurance Specialist");
              } else if (content.toLowerCase().includes("debate") || content.toLowerCase().includes("cross-referencing")) {
                setActiveAgent("Clinical Consensus Hub");
              } else if (content.toLowerCase().includes("finalizing") || content.toLowerCase().includes("documentation")) {
                setActiveAgent("Documentation Agent");
              }
            } else {
              setWidgetData(data.content);
              setStatus(null);
            }
          } else if (data.type === "error") {
            setMessages(prev => [...prev, { role: "assistant", content: `Error: ${data.content}` }]);
            setStatus(null);
          }
        } catch (e) {
          console.error("Failed to parse WebSocket message:", e);
        }
      };

      socket.onerror = (error) => {
        // Prevent noisy logs if the connection was intentionally closed or is already closing
        if (socket.readyState !== WebSocket.CLOSED && socket.readyState !== WebSocket.CLOSING) {
          console.error("WebSocket error:", error);
          socket.close();
        }
      };
    };

    connect();

    return () => {
      if (socketRef.current) {
        socketRef.current.onclose = null; // Prevent reconnection on unmount
        socketRef.current.close();
      }
      clearTimeout(timeoutId);
    };
  }, []);

  const sendMessage = useCallback((content: string) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      setMessages(prev => [...prev, { role: "user", content }]);
      socketRef.current.send(JSON.stringify({ message: content }));
      setActiveAgent("Coordinator");
      setWidgetData(null); // Clear previous widget on new message
    }
  }, []);

  const resetChat = useCallback(() => {
    setMessages([
      { 
        role: "assistant", 
        content: "Secure clinical session re-initialized. I am the Syntriage Clinical Coordinator. How can I assist you with patient triage, scheduling, or medical history review today?" 
      }
    ]);
    setStatus(null);
    setActiveAgent("Coordinator");
    setWidgetData(null);
  }, []);

  return { messages, status, activeAgent, widgetData, sendMessage, resetChat, isConnected };
};
