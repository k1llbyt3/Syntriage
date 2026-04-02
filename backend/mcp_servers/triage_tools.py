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
