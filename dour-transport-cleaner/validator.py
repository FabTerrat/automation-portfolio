ALLOWED_TRANSPORT_PROFILES = {
    "DRIVER",
    "PASSENGER",
    "TRAIN_ONLY",
    "TRAIN_CARPOOL",
    "OTHER",
}


def validate_enrichment(result: dict) -> dict:
    required_fields = [
        "normalized_city",
        "city_cluster",
        "alternative_clusters",
        "transport_profile",
        "needs_action",
        "confidence",
        "reason",
    ]

    for field in required_fields:
        if field not in result:
            raise ValueError(f"Missing field: {field}")

    if result["transport_profile"] not in ALLOWED_TRANSPORT_PROFILES:
        raise ValueError(f"Invalid transport_profile: {result['transport_profile']}")

    if not isinstance(result["needs_action"], bool):
        raise ValueError("needs_action must be a boolean")

    if not isinstance(result["alternative_clusters"], list):
        raise ValueError("alternative_clusters must be a list")

    confidence = result["confidence"]
    if not isinstance(confidence, (int, float)):
        raise ValueError("confidence must be a number")

    if confidence < 0 or confidence > 1:
        raise ValueError("confidence must be between 0 and 1")

    return result