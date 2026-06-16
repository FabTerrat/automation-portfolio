import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

from prompt_builder import PromptBuilder


load_dotenv()


class FakeLLMClient:
    def enrich_transport_response(self, row: dict) -> dict:
        city = str(row.get("departure_city", "")).strip().upper()
        mode = str(row.get("transport_mode", "")).strip()
        preference = str(row.get("transport_preference", "")).strip()

        normalized_city = self._normalize_city(city)
        city_cluster = self._get_city_cluster(normalized_city)

        if mode == "OWN_CAR":
            profile = "DRIVER"
            needs_action = False
        elif mode == "LOOKING_FOR_CARPOOL":
            profile = "PASSENGER"
            needs_action = True
        elif mode == "TRAIN":
            if preference == "TRAIN_CARPOOL":
                profile = "TRAIN_CARPOOL"
                needs_action = True
            else:
                profile = "TRAIN_ONLY"
                needs_action = False
        else:
            profile = "OTHER"
            needs_action = True

        return {
            "normalized_city": normalized_city,
            "city_cluster": city_cluster,
            "alternative_clusters": [],
            "transport_profile": profile,
            "needs_action": needs_action,
            "confidence": 1.0,
            "reason": "Classification déterministe à partir des champs structurés.",
        }

    def _normalize_city(self, city: str) -> str:
        city_mapping = {
            "VILLEURBANNE": "LYON",
            "BRON": "LYON",
            "LYON 8": "LYON",
        }
        return city_mapping.get(city, city)

    def _get_city_cluster(self, normalized_city: str) -> str:
        cluster_mapping = {
            "LYON": "LYON_AREA",
            "GRENOBLE": "GRENOBLE_AREA",
            "ANNECY": "ANNECY_AREA",
            "BRUXELLES": "BRUSSELS_AREA",
            "BORDEAUX": "BORDEAUX_AREA",
            "LILLE": "LILLE_AREA",
            "PARIS": "PARIS_AREA",
        }
        return cluster_mapping.get(normalized_city, "OTHER_AREA")


class OpenAIClient:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY")

        self.client = OpenAI(api_key=api_key)
        self.prompt_builder = PromptBuilder()

    def enrich_transport_response(self, row: dict) -> dict:
        prompt = self.prompt_builder.build_transport_enrichment_prompt(row)

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

        content = response.choices[0].message.content
        json_text = self._extract_json(content)

        return json.loads(json_text)

    def _extract_json(self, content: str) -> str:
        if content is None:
            raise ValueError("Empty LLM response")

        content = content.strip()

        match = re.search(r"\{.*\}", content, re.DOTALL)

        if not match:
            raise ValueError("No JSON object found in LLM response")

        return match.group(0)