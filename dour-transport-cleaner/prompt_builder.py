import json


class PromptBuilder:
    def build_transport_enrichment_prompt(self, row: dict) -> str:
        return f"""
You are helping organize transport for volunteers going to Dour Festival.

Your task is to convert a raw Google Form response into a clean JSON object.

Return ONLY valid JSON. No markdown. No explanation.

Allowed transport_profile values:
- DRIVER
- PASSENGER
- TRAIN_ONLY
- TRAIN_CARPOOL
- OTHER

Rules:
- DRIVER = person has their own car.
- PASSENGER = person is looking for a carpool.
- TRAIN_ONLY = person plans to travel only by train.
- TRAIN_CARPOOL = person plans to combine train and carpool.
- OTHER = unclear or unsupported case.
- needs_action should be true if the person probably needs help or coordination.
- confidence must be between 0 and 1.

City clustering examples:
- Lyon, Villeurbanne, Bron, Lyon 8 => LYON_AREA
- Grenoble => GRENOBLE_AREA
- Annecy => ANNECY_AREA
- Bruxelles, Brussels => BRUSSELS_AREA
- Bordeaux => BORDEAUX_AREA
- Lille => LILLE_AREA
- Paris => PARIS_AREA

Input response:
{json.dumps(row, ensure_ascii=False)}

Expected JSON schema:
{{
  "normalized_city": "LYON",
  "city_cluster": "LYON_AREA",
  "alternative_clusters": ["GRENOBLE_AREA"],
  "transport_profile": "PASSENGER",
  "needs_action": true,
  "confidence": 0.85,
  "reason": "Short reason in French"
}}
"""