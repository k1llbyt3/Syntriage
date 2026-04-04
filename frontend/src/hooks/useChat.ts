"use client";
import { useState, useEffect, useRef, useCallback } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface WidgetData {
  type: string;
  data: any;
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
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const socket = new WebSocket(`${protocol}//127.0.0.1:8000/ws/chat`);
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
            setStatus(data.content);
            if (data.content.includes("TRANSFERRED_TO_")) {
              const agent = data.content.split("TRANSFERRED_TO_")[1].split(":")[0];
              setActiveAgent(agent.charAt(0) + agent.slice(1).toLowerCase());
            }
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

  return { messages, status, activeAgent, widgetData, sendMessage, isConnected };
};
