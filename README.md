# 🏥 Syntriage: Next-Gen Clinical Orchestration ⚡

<div align="center">

![Syntriage Banner](https://img.shields.io/badge/SYNTRIAGE-SMART%20HEALTHCARE-blueviolet?style=for-the-badge&logo=at-and-t)

[![Cloud Run](https://img.shields.io/badge/Deployed%20on-Google%20Cloud%20Run-blue?style=for-the-badge&logo=google-cloud)](https://syntriage-frontend-267460236055.europe-west1.run.app)
[![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)](https://syntriage.vercel.app)
[![Tech Stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20Next.js%20%7C%20Gemini-blue?style=for-the-badge)](https://github.com/k1llbyt3/Syntriage)

**Syntriage** is a high-fidelity clinical orchestration platform. It streamlines patient intake through AI-driven triage, multi-agent history reconciliation, and smart scheduling.

[**🌐 Live Demo (Cloud Run)**](https://syntriage-frontend-267460236055.europe-west1.run.app) • [**⚡ Vercel Mirror**](https://syntriage.vercel.app) • [**📂 Repository**](https://github.com/k1llbyt3/Syntriage)

</div>

---

## 🚀 The Vision

Traditional patient intake is slow and prone to error. **Syntriage** leverages a **Multi-Agent Architecture** powered by the **Model Context Protocol (MCP)** to ensure that every patient interaction is medically sound, safe, and efficient.

### 💎 Key Innovations

| Feature | Description |
| :--- | :--- |
| **🧠 Agentic Mesh** | Specialized agents (Triage, History, Scheduling, Insurance) collaborate in real-time. |
| **⚡ Streaming Triage** | WebSocket-driven symptom evaluation with sub-second response times. |
| **🚨 Emergency Protocol** | Hard-coded bypass for high-risk symptoms (e.g., cardiac or stroke indicators). |
| **⚖️ Clinical Consensus** | "Debate Logic" between agents to reconcile conflicting medical histories. |
| **📅 MCP Scheduling** | Direct integration with clinical tools for verified appointment booking. |

---

## 🛠️ Tech Stack & Architecture

### **The Core (Backend)**
- **Runtime:** [Python 3.12+](https://python.org)
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (High-performance async)
- **Intelligence:** [Google Gemini AI](https://ai.google.dev/) via `google-generativeai`
- **Protocol:** [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
- **Storage:** [SQLModel](https://sqlmodel.tiangolo.com/) + PostgreSQL

### **The Experience (Frontend)**
- **Framework:** [Next.js 15+](https://nextjs.org/) (App Router & React 19)
- **Style:** [Tailwind CSS 4](https://tailwindcss.com/)
- **Motion:** [Framer Motion](https://www.framer.com/motion/)
- **Interface:** [Lucide React](https://lucide.dev/) Icons

---

## 📂 Project Anatomy

```bash
.
├── 🐍 backend/
│   ├── agents/          # AI Orchestration & Clinical Prompts
│   ├── mcp_servers/     # Tool-based Intelligence (History, Insurance)
│   ├── core/            # Database & App Config
│   └── main.py          # WebSocket Entry Point
├── ⚛️ frontend/
│   ├── src/app/         # Next.js App Router (Dashboard & Chat)
│   ├── src/components/  # UI Components (StatusPill, TimeSlot)
│   └── src/hooks/       # Business Logic (useChat)
└── ☁️ render.yaml        # Infrastructure as Code
```

---

## 🚦 Quick Start

### 1. Clone & Prep
```bash
git clone https://github.com/k1llbyt3/Syntriage.git
cd Syntriage
```

### 2. Launch Backend
```bash
cd backend
pip install -r requirements.txt
# Set GEMINI_API_KEY & DATABASE_URL in .env
python main.py
```

### 3. Launch Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🛡️ Safety & Compliance
Syntriage is built with a **Safety-First** philosophy. We implement strict heuristic checks for life-threatening conditions, ensuring that AI-driven triage never replaces immediate emergency care when seconds count.

---

<div align="center">
  <sub>Developed with ❤️ for the future of healthcare.</sub>
</div>
