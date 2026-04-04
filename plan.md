# GSD Implementation Plan: VitalSync V4.0 (The Masterpiece)

**Execution Rule:** Every capability must be an MCP Tool. Logic resides in tools; reasoning resides in agents.

## Phase 1: The MCP Server Layer (The "Hands")

1.  **DB Server (Postgres):** Build MCP tools for `fetch_user`, `fetch_slots`, `create_appointment`, and `save_note`.
2.  **Protocol Server (RAG):** Build an MCP tool `check_medical_protocol(symptoms)` that returns safety data.
3.  **Insurance Server:** Build an MCP tool `verify_billing_status(patient_id)`.

## Phase 2: Agent Personas & Personification (The "Voice")

4.  **Triage Agent:** Specialized in symptom analysis and urgency scoring.
5.  **History Agent:** Specialized in patient background, allergies, and chronic conditions.
6.  **Scheduling Agent:** The purely logical "calendar manager."

## Phase 3: The Multi-Agent Consensus Logic (The "Brain")

7.  **The Debate Protocol:** Implement a workflow in `coordinator.py` where:
    - Triage Agent provides an urgency score.
    - History Agent reviews it against patient history.
    - If they disagree (e.g., Triage says "Low" but History sees "Diabetes"), the Coordinator triggers a "Consensus Tool" to reconcile the two before the user sees a result.

## Phase 4: Modern Glassmorphism UI (The "Face")

8.  **Layout:** Build the Chat UI with `backdrop-blur-xl` and `bg-white/20`. Use Teal (`#14B8A6`) for primary actions.
9.  **Voice-Ready Chat Bar:** Add a pulsing Microphone icon (`lucide-react`) next to the send button.
    - _Note:_ Implement the UI state (colors, animations) but keep the backend hook empty as requested.
10. **Interactive Widgets:** Implement "Time Slot Cards" that pop up in the chat stream when the Scheduling Agent returns data.

## Phase 5: Physician Override Dashboard

11. Build the `/dashboard` page.
12. Show a live feed of "Debated" cases. Allow doctors to see the internal "Reasoning" transcript of why the Triage and History agents assigned a specific score.
13. Add the "Human-in-the-loop" button to override any DB entry.

## Phase 6: Final Integration & Deployment

14. **WebSocket Streaming:** Ensure the UI shows _which_ agent is currently speaking/debating (e.g., "History Agent is cross-referencing triage...").
15. **Render/Vercel Deploy:** \* FastAPI -> Render (Connect `syntriage_prod` DB).
    - Next.js -> Vercel (Point to live WebSocket).
