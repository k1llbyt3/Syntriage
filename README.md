# 🏥 Syntriage: Smart Patient Intake & Care Coordinator

[![Live Demo](https://img.shields.io/badge/demo-syntriage.vercel.app-blueviolet?style=for-the-badge&logo=vercel)](https://syntriage.vercel.app)
[![Tech Stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20Next.js%20%7C%20Gemini-blue?style=for-the-badge)](https://github.com/k1llbyt3/Syntriage)

**Syntriage** is a next-generation clinical orchestration platform designed to streamline patient intake through AI-driven triage, history reconciliation, and smart scheduling. By leveraging a multi-agent architecture and the Model Context Protocol (MCP), Syntriage ensures high-fidelity clinical data collection while prioritizing patient safety.

---

## ✨ Key Features

- **🧠 Multi-Agent Orchestration:** Specialized AI agents (Triage, History, Scheduling, Insurance) collaborate to process patient requests.
- **⚡ Real-time Triage:** WebSocket-based streaming for instant symptom evaluation and clinical status updates.
- **🚨 Emergency Bypass:** Automated detection of high-risk symptoms (e.g., chest pain) with immediate escalation to emergency protocols.
- **⚖️ Clinical Consensus:** Integrated "Debate Logic" where agents reconcile conflicting data (e.g., Triage vs. Medical History) to ensure accuracy.
- **📅 Smart Scheduling:** Automated appointment booking and insurance verification via dedicated MCP tools.
- **🛠️ Provider Dashboard:** Comprehensive view of patient records, clinical notes, and urgency-based case management.

---

## 🛠️ Tech Stack

### Backend
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
- **AI/LLM:** [Google Gemini AI](https://ai.google.dev/) via `google-generativeai`
- **Database:** [SQLModel](https://sqlmodel.tiangolo.com/) & PostgreSQL
- **Real-time:** WebSockets for asynchronous agent-patient interaction
- **Protocol:** [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) for tool-augmented intelligence

### Frontend
- **Framework:** [Next.js 15+](https://nextjs.org/) (React 19)
- **Styling:** [Tailwind CSS 4](https://tailwindcss.com/)
- **Animations:** [Framer Motion](https://www.framer.com/motion/)
- **Icons:** [Lucide React](https://lucide.dev/)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL Database
- Gemini API Key

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables in a `.env` file:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/dbname
   GEMINI_API_KEY=your_api_key_here
   FRONTEND_URL=https://syntriage.vercel.app
   ```
4. Start the server:
   ```bash
   python main.py
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

---

## 📂 Project Structure

```text
.
├── backend/
│   ├── agents/          # AI Agent logic and clinical prompts
│   ├── core/            # Database and app configuration
│   ├── mcp_servers/     # Tool-based servers (History, Insurance, etc.)
│   ├── models/          # SQLModel database schemas
│   └── main.py          # FastAPI entry point & WebSocket handler
├── frontend/
│   ├── src/app/         # Next.js App Router (Dashboard & Chat)
│   ├── src/components/  # UI Components (ChatBubble, StatusPill)
│   └── src/hooks/       # Custom React hooks (useChat)
└── render.yaml          # Deployment configuration
```

---

## 🛡️ Safety & Compliance
Syntriage implements a **Safety-First** approach. The system is designed to detect life-threatening symptoms and immediately redirect users to emergency services. Clinical notes are logged with urgency levels and can be manually overridden by healthcare professionals.

---

## 🔗 Links
- **Live Website:** [syntriage.vercel.app](https://syntriage.vercel.app)
- **GitHub Repository:** [github.com/k1llbyt3/Syntriage](https://github.com/k1llbyt3/Syntriage)

---
*Developed for smart healthcare orchestration.*
