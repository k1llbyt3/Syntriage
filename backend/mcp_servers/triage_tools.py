def evaluate_urgency(symptoms: str):
    """Evaluates the urgency level based on symptoms."""
    symptoms = symptoms.lower()
    # Basic logic for now - in production this would use LLM
    high_urgency = ["chest pain", "shortness of breath", "severe bleeding", "unconscious"]
    med_urgency = ["fever", "severe pain", "broken bone"]
    
    if any(keyword in symptoms for keyword in high_urgency):
        return {"urgency": "ER", "advice": "Please call 911 or go to the nearest ER immediately."}
    elif any(keyword in symptoms for keyword in med_urgency):
        return {"urgency": "High", "advice": "Seek medical attention within 24 hours."}
    else:
        return {"urgency": "Low/Med", "advice": "Monitor symptoms and book a routine follow-up."}

def check_medical_protocol(symptoms: str):
    """Checks the medical protocol knowledge base for safety data based on symptoms."""
    symptoms_lower = symptoms.lower()
    if "chest pain" in symptoms_lower or "shortness of breath" in symptoms_lower:
        return {"protocol": "Immediate ER admission", "safety_data": "High risk of cardiac event or pulmonary embolism. Do not wait."}
    elif "fever" in symptoms_lower:
        return {"protocol": "Standard fever management", "safety_data": "Monitor temperature. If > 103F for 48h, escalate to urgent care."}
    else:
        return {"protocol": "Routine assessment", "safety_data": "Standard clinical guidelines apply."}

def trigger_consensus_debate(triage_score: str, triage_reasoning: str, history_agent_findings: str):
    """
    Triggers a debate between the Triage Agent and History Agent to determine the final,
    safest urgency score for the patient. Use this when there's a potential risk identified
    in the patient's history that contradicts a low triage score.
    """
    score = triage_score.lower()
    findings = history_agent_findings.lower()
    
    risk_factors = ["diabetes", "heart", "immunocompromised", "asthma", "hypertension", "copd", "kidney disease", "pregnancy", "elderly", "infant"]
    
    if score in ["low", "med", "low/med", "low/med urgency"] and any(risk in findings for risk in risk_factors):
        return {
            "final_urgency": "High",
            "resolution": "History Agent overrode Triage Agent. Chronic condition detected requires elevated urgency.",
            "debate_transcript": f"Triage Agent: Score {triage_score} based on {triage_reasoning}. History Agent: Risk factors found: {history_agent_findings}. Consensus: Escalating to High."
        }
    
    return {
        "final_urgency": triage_score,
        "resolution": "Agents agree on the urgency score.",
        "debate_transcript": f"Triage Agent: Score {triage_score} based on {triage_reasoning}. History Agent: Reviewed findings: {history_agent_findings}. Consensus: Maintaining original score."
    }
