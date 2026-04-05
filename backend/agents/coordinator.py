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
        print(f"DEBUG: Initializing Syntriage Stateless Orchestrator (v3.3 - QUOTA BYPASS)...")
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # 2026 MULTI-GEN POOL: Spreading load across different model families to avoid project-wide 429s
        self.model_pool = [
            "gemini-1.5-flash-lite",  # Family A: High legacy quota
            "gemini-2.5-flash-lite",  # Family B: High current quota
            "gemini-3.1-flash-lite",  # Family C: Next-gen quota
            "gemini-1.5-pro"          # Family D: Emergency fallback
        ]
        self.active_model_index = 0
        self.exhausted_models = set()

    def _to_dict(self, obj):
        if hasattr(obj, "items"):
            return {k: self._to_dict(v) for k, v in obj.items()}
        elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes)):
            return [self._to_dict(v) for v in obj]
        return obj

    def prune_history(self, history, max_turns=3):
        """Extreme pruning to 3 turns to stay under Token/Minute (TPM) limits."""
        if len(history) > max_turns * 2:
            return history[-(max_turns * 2):]
        return history

    async def get_response_with_widgets(self, user_input: str, history=None):
        """
        Processes a request with persistent failover and quota-saving logic.
        """
        ROLE_NAMES = {
            "gemini-1.5-flash-lite": "Care Assistant",
            "gemini-2.5-flash-lite": "Clinical Specialist",
            "gemini-3.1-flash-lite": "Expert Coordinator",
            "gemini-1.5-pro": "System Recovery"
        }
        
        current_history = self.prune_history(history or [])
        last_error_was_quota = False

        for attempt in range(len(self.model_pool)):
            model_name = self.model_pool[self.active_model_index]
            
            if model_name in self.exhausted_models:
                self.active_model_index = (self.active_model_index + 1) % len(self.model_pool)
                continue

            role_name = ROLE_NAMES.get(model_name, "Clinical AI")
            
            try:
                # OPTIMIZATION: Use a lighter system prompt if we've hit errors already
                sys_prompt = COORDINATOR_SYSTEM_PROMPT
                if attempt > 0:
                    sys_prompt = "You are a helpful clinical assistant. Answer briefly. Use tools if needed."

                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=sys_prompt.format(
                        current_time=datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
                    ),
                    tools=tools if attempt == 0 else None, # Disable tools on later failovers to save tokens
                )
                
                chat = model.start_chat(history=current_history, enable_automatic_function_calling=True if attempt == 0 else False)
                
                time_context = f"Today is {datetime.now().strftime('%A, %B %d')}. "
                response = chat.send_message(time_context + user_input, request_options={"retry": None})

                responseText = ""
                if response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, "text"):
                            responseText += part.text
                
                if not responseText:
                    responseText = "Acknowledged. How can I help?"

                # Extract widgets only if tools were enabled
                widget_data = None
                if attempt == 0:
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
                print(f"QUOTA FAILOVER: Model {model_name} failed. Error: {error_msg}")
                
                if "429" in error_msg or "quota" in error_msg:
                    last_error_was_quota = True
                    self.exhausted_models.add(model_name)
                    await asyncio.sleep(1) # Small throttle
                
                self.active_model_index = (self.active_model_index + 1) % len(self.model_pool)
                continue

        if last_error_was_quota:
            self.exhausted_models.clear()
            return "RETRY_WAIT_55", None, "System Recovery", current_history

        return "Syntriage is experiencing temporary latency. Please refresh.", None, "System Recovery", current_history

coordinator = CoordinatorAgent()
