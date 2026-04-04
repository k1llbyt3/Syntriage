# Context: Syntriage (v4.0) - MCP-Native Clinical Orchestrator

## 1. Problem Statement Alignment (STRICT)

- **Primary Agent:** Coordinator (Gemini 2.5 Flash).
- **Sub-Agents:** 5 specialized agents (Triage, Scheduling, Records, Insurance, Consensus).
- **Tools:** Purely MCP-driven. Each sub-agent is a wrapper around a specific MCP Server.
- **Data Sources:** PostgreSQL (Neon) for schedules/tasks, JSON-based RAG for medical protocols.
- **Workflow:** Multi-step (Symptom -> Consensus Debate -> Schedule -> Record).

## 2. The V4 "Masterpiece" Features

- **Consensus Mechanism:** Before a final decision is made, the Triage Agent and Medical History Agent "debate" the urgency level to ensure the highest safety.
- **Voice-Ready UI:** A modern, pulsing microphone icon in the chat bar (UI-ready for future STT implementation).
- **Pure MCP Architecture:** No hardcoded logic in the agents; every external action (DB write, DB read, Protocol check) is an MCP Tool call.

## 3. Tech Stack

- **LLM:** Gemini 2.5 Flash (via Google AI Studio).
- **Protocol:** Model Context Protocol (MCP) Python SDK.
- **Backend:** FastAPI (REST/WebSockets).
- **Database:** PostgreSQL (Neon.tech) with SQLModel.
- **Frontend:** Next.js 14 + Tailwind CSS + Framer Motion (Glassmorphism).
