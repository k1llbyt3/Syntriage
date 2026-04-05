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
        print(f"DEBUG: Initializing Syntriage Stateless Orchestrator (v2.7)...")
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # Enhanced Model Pool for failover backups
        self.model_pool = [
            "gemini-2.5-flash-lite",  # Tier 1: Optimized/Cheapest
            "gemini-2.5-flash",       # Tier 2: Reasoning backup
            "gemini-3.1-pro-preview"  # Tier 3: Expert backup
        ]
        self.active_model_index = 0

    def _to_dict(self, obj):
        if hasattr(obj, "items"):
            return {k: self._to_dict(v) for k, v in obj.items()}
        elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes)):
            return [self._to_dict(v) for v in obj]
        return obj

    def prune_history(self, history, max_turns=10):
        """Optimizes API consumption by keeping only the last N turns of context."""
        if len(history) > max_turns * 2: # 2 parts per turn usually
            return history[-(max_turns * 2):]
        return history

    async def get_response_with_widgets(self, user_input: str, history=None):
        """
        Processes a request without persistent session storage.
        Handles 429 errors with a 55s wait (buffer) and console-only logging.
        """
        ROLE_NAMES = {
            "gemini-3.1-pro-preview": "Expert Coordinator",
            "gemini-2.5-flash": "Clinical Specialist",
            "gemini-2.5-flash-lite": "Care Assistant"
        }
        
        # Optimization: Prune history to reduce token consumption
        current_history = self.prune_history(history or [])
        
        # Failover Loop (Backups for all agents)
        for _ in range(len(self.model_pool)):
            model_name = self.model_pool[self.active_model_index]
            role_name = ROLE_NAMES.get(model_name, "Clinical AI")
            
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=COORDINATOR_SYSTEM_PROMPT.format(current_time=datetime.now().strftime("%A, %B %d, %Y %I:%M %p")),
                    tools=tools,
                )
                chat = model.start_chat(history=current_history, enable_automatic_function_calling=True)
                
                time_context = f"[System Context: Today is {datetime.now().strftime('%A, %B %d, %Y')}]\n"
                enriched_input = time_context + user_input
                
                response = chat.send_message(enriched_input, request_options={"retry": None})

                responseText = ""
                if response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, "text"):
                            responseText += part.text
                
                if not responseText:
                    responseText = "Clinical request processed. How can I assist further?"

                widget_data = None
                # Dynamic Role Detection based on Tool Usage
                for msg in reversed(chat.history[-5:]):
                    for part in msg.parts:
                        if hasattr(part, "function_call"):
                            call_name = part.function_call.name
                            if call_name in ["get_patient_records", "fetch_medical_history", "save_clinical_note", "save_patient_note", "update_allergies", "add_medication"]:
                                role_name = "Clinical Records Specialist"
                            elif call_name in ["evaluate_urgency", "check_medical_protocol"]:
                                role_name = "Triage Specialist"
                            elif call_name in ["get_available_slots", "book_slot"]:
                                role_name = "Scheduling Coordinator"
                            elif call_name in ["verify_billing_status", "verify_coverage", "register_insurance_profile"]:
                                role_name = "Insurance Specialist"
                            elif call_name in ["get_patient_profile", "register_patient"]:
                                role_name = "Patient Registry"
                            elif call_name == "trigger_consensus_debate":
                                role_name = "Clinical Consensus Hub"
                            elif call_name == "transfer_to_agent":
                                # Handle explicit transfer call
                                args = self._to_dict(part.function_call.args)
                                if "agent_name" in args:
                                    role_name = f"{args['agent_name'].capitalize()} Specialist"

                        if hasattr(part, "function_response"):
                            name = part.function_response.name
                            resp = self._to_dict(part.function_response.response)
                            if name == "get_available_slots":
                                widget_data = {"type": "time_slots", "data": resp}
                            elif name == "update_status":
                                widget_data = {"type": "status_update", "content": resp}
                            elif name == "trigger_consensus_debate":
                                widget_data = {"type": "debate_event", "data": resp}

                return responseText, widget_data, role_name, chat.history
                
            except Exception as e:
                error_str = str(e)
                print(f"CRITICAL: {model_name} failed: {error_str}")
                
                if "429" in error_str:
                    print("QUOTA EXCEEDED (429): Waiting 55 seconds (buffer active)...")
                    return "RETRY_WAIT_55", None, role_name, current_history
                
                # Failover to next model in pool
                self.active_model_index = (self.active_model_index + 1) % len(self.model_pool)
                continue

        return "Syntriage is currently under extreme load. Please check back in a few minutes.", None, "System Recovery", current_history


coordinator = CoordinatorAgent()
