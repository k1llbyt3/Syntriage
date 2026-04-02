import google.generativeai as genai
from core.config import settings
from agents.prompts import COORDINATOR_SYSTEM_PROMPT
from mcp_servers.triage_tools import evaluate_urgency
from mcp_servers.schedule_tools import check_availability, book_appointment
from mcp_servers.history_tools import update_allergies, add_medication
from mcp_servers.notes_tools import save_patient_note
from mcp_servers.insurance_tools import verify_coverage
from mcp_servers.profile_tools import get_patient_profile

genai.configure(api_key=settings.GOOGLE_API_KEY)

# Define tools for Gemini to use
tools = [
    evaluate_urgency,
    check_availability,
    book_appointment,
    update_allergies,
    add_medication,
    save_patient_note,
    verify_coverage,
    get_patient_profile # New tool for recognition
]

class CoordinatorAgent:
    def __init__(self):
        # Gemini 2.0 Flash for high-speed coordination
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=COORDINATOR_SYSTEM_PROMPT,
            tools=tools,
        )
        self.chat = self.model.start_chat(
            history=[], 
            enable_automatic_function_calling=True
        )

    async def get_response(self, user_input: str):
        try:
            response = self.chat.send_message(user_input)
            return response.text
        except Exception as e:
            print(f"Agent Hub Error: {e}")
            return f"SYSTEM_LOG: AGENT_HUB_COMM_FAIL: {str(e)}"

coordinator = CoordinatorAgent()
