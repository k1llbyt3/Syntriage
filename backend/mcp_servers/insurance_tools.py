def verify_coverage(provider_name: str, member_id: str):
    """Simulates insurance coverage verification."""
    # Mocking external API
    valid_providers = ["BlueShield", "Aetna", "UnitedHealth", "Cigna"]
    if provider_name in valid_providers:
        return {"status": "Verified", "copay": 25, "coverage_level": "Full"}
    else:
        return {"status": "Provider Not Found", "message": "Please check your provider details or pay out of pocket."}
