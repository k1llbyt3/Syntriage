"use client";
import { useState, useEffect, useRef, useCallback } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([
    { 
      role: "assistant", 
      content: "Welcome to VitalSync. I am your Clinical Coordinator. To assist you today, I will need your Name and Email to access your records. Please describe your symptoms or let me know if you would like to schedule an appointment." 
    }
  ]);
  const [status, setStatus] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect to WebSocket
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const socket = new WebSocket(`${protocol}//localhost:8000/ws/chat`);
    socketRef.current = socket;

    socket.onopen = () => setIsConnected(true);
    socket.onclose = () => setIsConnected(false);
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === "status") {
        setStatus(data.content);
      } else if (data.type === "message") {
        setMessages(prev => [...prev, { role: "assistant", content: data.content }]);
        setStatus(null);
      } else if (data.type === "error") {
        setMessages(prev => [...prev, { role: "assistant", content: `Error: ${data.content}` }]);
        setStatus(null);
      }
    };

    return () => {
      socket.close();
    };
  }, []);

  const sendMessage = useCallback((content: string) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      setMessages(prev => [...prev, { role: "user", content }]);
      socketRef.current.send(JSON.stringify({ message: content }));
    }
  }, []);

  return { messages, status, sendMessage, isConnected };
};
