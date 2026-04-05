import google.generativeai as genai
from core.config import settings
from agents.prompts import COORDINATOR_SYSTEM_PROMPT
from mcp_servers.triage_tools import (
    evaluate_urgency,
    check_medical_protocol,
    trigger_consensus_debate,
)
from mcp_servers.schedule_tools import get_available_slots, book_slot
from mcp_servers.history_tools import (
    update_allergies,
    add_medication,
    fetch_medical_history,
)
from mcp_servers.notes_tools import save_patient_note, save_clinical_note, get_patient_records
from mcp_servers.insurance_tools import (
    verify_coverage, 
    verify_billing_status,
    register_insurance_profile
)
from mcp_servers.profile_tools import get_patient_profile, register_patient
import json
import asyncio
from datetime import datetime


def update_status(status_message: str):
    """
    Pushes a real-time status update to the patient's UI.
    """
    return f"STATUS_UPDATE: {status_message}"


def get_current_clinical_time():
    """
    Returns the current clinical system date and time. Use this for all date calculations (today, tomorrow, etc).
    """
    return datetime.now().strftime("%A, %B %d, %Y %I:%M %p")


def transfer_to_agent(agent_name: str):
    """
    Transfers the conversation context to a specialized sub-agent.
    """
    return f"TRANSFERRED_TO_{agent_name.upper()}: I am now operating as the {agent_name}."


# Define tools
tools = [
    evaluate_urgency,
    check_medical_protocol,
    trigger_consensus_debate,
    get_available_slots,
    book_slot,
    update_allergies,
    add_medication,
    fetch_medical_history,
    save_patient_note,
    save_clinical_note,
    get_patient_records,
    verify_coverage,
    verify_billing_status,
    register_insurance_profile,
    get_patient_profile,
    register_patient,
    update_status,
    get_current_clinical_time,
    transfer_to_agent,
]


class CoordinatorAgent:
    def __init__(self):
        print(f"DEBUG: Initializing Syntriage Stateless Orchestrator (v2.9)...")
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # 2026 HIGH-QUOTA POOL: Prioritizing models with the highest daily limits
        self.model_pool = [
            "gemini-3.1-flash-lite",  # 1,500 Requests/Day
            "gemini-3-flash",         # 1,000 Requests/Day
            "gemini-2.5-flash",       # 500 Requests/Day (Fallback)
            "gemini-1.5-flash",       # Stable Backup
            "gemini-2.5-pro"          # Reasoning Specialist
        ]
        self.active_model_index = 0
        self.exhausted_models = set()

    def _to_dict(self, obj):
        if hasattr(obj, "items"):
            return {k: self._to_dict(v) for k, v in obj.items()}
        elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes)):
            return [self._to_dict(v) for v in obj]
        return obj

    def prune_history(self, history, max_turns=8):
        """Reduces token count to prevent TPM (Tokens Per Minute) 429 errors."""
        if len(history) > max_turns * 2:
            return history[-(max_turns * 2):]
        return history

    async def get_response_with_widgets(self, user_input: str, history=None):
        """
        Processes a request with persistent failover logic across sessions.
        """
        ROLE_NAMES = {
            "gemini-3.1-flash-lite": "Care Assistant",
            "gemini-3-flash": "Clinical Specialist",
            "gemini-2.5-flash": "Triage Agent",
            "gemini-1.5-flash": "System Backup",
            "gemini-2.5-pro": "Expert Coordinator"
        }
        
        current_history = self.prune_history(history or [])
        last_error_was_429 = False

        # Attempt to find a working model in the pool
        for attempt in range(len(self.model_pool)):
            model_name = self.model_pool[self.active_model_index]
            
            # If the current model is known to be exhausted, skip it
            if model_name in self.exhausted_models:
                self.active_model_index = (self.active_model_index + 1) % len(self.model_pool)
                continue

            role_name = ROLE_NAMES.get(model_name, "Clinical AI")
            
            try:
                # 1. Initialize Model
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=COORDINATOR_SYSTEM_PROMPT.format(
                        current_time=datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
                    ),
                    tools=tools,
                )
                
                # 2. Start Chat
                chat = model.start_chat(history=current_history, enable_automatic_function_calling=True)
                
                # 3. Process Input
                time_context = f"[Context: {datetime.now().strftime('%A, %B %d, %Y')}]\n"
                response = chat.send_message(time_context + user_input, request_options={"retry": None})

                # 4. Extract Text
                responseText = ""
                if response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, "text"):
                            responseText += part.text
                
                if not responseText:
                    responseText = "Request acknowledged. How can I assist you today?"

                # 5. Extract Widget/Role from Function Calls
                widget_data = None
                for msg in reversed(chat.history[-5:]):
                    for part in msg.parts:
                        if hasattr(part, "function_call"):
                            call_name = part.function_call.name
                            if call_name in ["get_patient_records", "fetch_medical_history", "save_clinical_note"]:
                                role_name = "Records Specialist"
                            elif call_name in ["evaluate_urgency", "check_medical_protocol"]:
                                role_name = "Triage Specialist"
                            elif call_name in ["get_available_slots", "book_slot"]:
                                role_name = "Scheduling Coordinator"

                        if hasattr(part, "function_response"):
                            name = part.function_response.name
                            resp = self._to_dict(part.function_response.response)
                            if name == "get_available_slots":
                                widget_data = {"type": "time_slots", "data": resp}
                            elif name == "update_status":
                                widget_data = {"type": "status_update", "content": resp}

                return responseText, widget_data, role_name, chat.history
                
            except Exception as e:
                error_msg = str(e).lower()
                print(f"FAILOVER ALERT: Model {model_name} failed. Error: {error_msg}")
                
                if "429" in error_msg or "quota" in error_msg:
                    last_error_was_429 = True
                    self.exhausted_models.add(model_name)
                
                # Immediately move to next model for the next attempt
                self.active_model_index = (self.active_model_index + 1) % len(self.model_pool)
                
                # Optional: Brief pause if hitting RPM (Requests Per Minute)
                await asyncio.sleep(0.5)
                continue

        # If all models in the pool are exhausted
        if last_error_was_429:
            self.exhausted_models.clear() # Reset for next session
            return "RETRY_WAIT_55", None, "System Recovery", current_history

        return "Syntriage is experiencing temporary latency. Please refresh and try again.", None, "System Recovery", current_history

coordinator = CoordinatorAgent()
