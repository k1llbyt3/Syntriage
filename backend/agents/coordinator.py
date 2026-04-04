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
from mcp_servers.notes_tools import save_patient_note, save_clinical_note
from mcp_servers.insurance_tools import verify_coverage, verify_billing_status
from mcp_servers.profile_tools import get_patient_profile, register_patient
import json
from datetime import datetime


def update_status(status_message: str):
    """
    Pushes a real-time status update to the patient's UI.
    """
    return f"STATUS_UPDATE: {status_message}"


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
    verify_coverage,
    verify_billing_status,
    get_patient_profile,
    register_patient,
    update_status,
    transfer_to_agent,
]


class CoordinatorAgent:
    def __init__(self):
        print(f"DEBUG: Initializing Syntriage Tiered Clinical Orchestrator (v2.5)...")
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # Tiered Model Pool (Verified 2026 Stable IDs)
        self.model_pool = [
            "gemini-3.1-pro-preview", # Tier 1: Primary Coordinator
            "gemini-2.5-flash",       # Tier 2: Triage Reasoning
            "gemini-2.5-flash-lite"   # Tier 3: Registry Server
        ]
        self.active_model_index = 0
        self.chat_sessions = {}  # Store chat sessions per model if needed

    def _get_active_session(self, model_name: str):
        if model_name not in self.chat_sessions:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=COORDINATOR_SYSTEM_PROMPT.format(current_time=datetime.now().strftime("%A, %B %d, %Y %I:%M %p")),
                tools=tools,
            )
            self.chat_sessions[model_name] = model.start_chat(
                history=[], enable_automatic_function_calling=True
            )
        return self.chat_sessions[model_name]

    def _to_dict(self, obj):
        # Robust conversion for MapComposite/RepeatedComposite
        if hasattr(obj, "items"):
            return {k: self._to_dict(v) for k, v in obj.items()}
        elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes)):
            return [self._to_dict(v) for v in obj]
        return obj

    async def get_response_with_widgets(self, user_input: str):
        """
        Parallel Model Failover: Attempts to process through the model pool
        if a quota (429) or discovery (404) error occurs.
        """
        # Clinical Identity Branding (Professional naming only)
        ROLE_NAMES = {
            "gemini-3.1-pro-preview": "Smart Coordinator",
            "gemini-2.5-flash": "Clinical Triage Specialist",
            "gemini-2.5-flash-lite": "Patient Registry Specialist"
        }
        
        last_error = None
        
        # Try up to 3 models in the pool
        for _ in range(len(self.model_pool)):
            model_name = self.model_pool[self.active_model_index]
            role_name = ROLE_NAMES.get(model_name, "Clinical AI")
            print(f"DEBUG: Attempting turn with {model_name}...")
            
            try:
                chat = self._get_active_session(model_name)
                # Rule 1: Parallel Tools + No SDK Retries (we handle retries via failover)
                response = chat.send_message(user_input, request_options={"retry": None})

                # ROBUST RESPONSE HANDLING
                responseText = ""
                try:
                    if response.candidates and response.candidates[0].content.parts:
                        for part in response.candidates[0].content.parts:
                            if hasattr(part, "text"):
                                responseText += part.text
                    
                    if not responseText:
                        # Check if it was blocked
                        finish_reason = response.candidates[0].finish_reason if response.candidates else "Unknown"
                        if finish_reason != 1: # 1 is SUCCESS in many versions, but check safety
                             responseText = f"[Response Filtered: Protocol Safety Triggered (Reason: {finish_reason})]"
                        else:
                             responseText = "Clinical request processed. How can I assist further?"
                except Exception as parse_error:
                    print(f"DEBUG: Response parsing error: {parse_error}")
                    responseText = "Request acknowledged. Syntriage is coordinating the next steps."

                widget_data = None
                history = chat.history
                if history:
                    for msg in history[-5:]:
                        for part in msg.parts:
                            if hasattr(part, "function_response"):
                                name = part.function_response.name
                                # Convert specialized protocol objects to pure dicts/lists
                                resp = self._to_dict(part.function_response.response)

                                if name == "get_available_slots":
                                    widget_data = {"type": "time_slots", "data": resp}
                                elif name == "update_status":
                                    widget_data = {"type": "status_update", "content": resp}
                                elif name == "trigger_consensus_debate":
                                    widget_data = {"type": "debate_event", "data": resp}

                return responseText, widget_data
                
            except Exception as e:
                last_error = str(e)
                print(f"DEBUG: {model_name} Error: {last_error}")
                # Rotate to next model in pool on 429 (Quota) or 404 (Not Found)
                self.active_model_index = (self.active_model_index + 1) % len(self.model_pool)
                continue

        # If all models in the pool fail
        return f"SYSTEM_LOG: PARALLELA_POOL_EXHAUSTED: {last_error}", None


coordinator = CoordinatorAgent()
