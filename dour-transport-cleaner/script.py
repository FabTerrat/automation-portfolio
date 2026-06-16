import sys
import os
from pathlib import Path

import pandas as pd

from llm_client import FakeLLMClient, OpenAIClient
from validator import validate_enrichment

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "input_responses.csv"
OUTPUT_FILE = BASE_DIR / "data" / "output_responses_enriched.csv"
MATCHES_FILE = BASE_DIR / "data" / "output_matches.csv"

load_dotenv()
USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    return pd.read_csv(path)


def enrich_rows(df: pd.DataFrame) -> pd.DataFrame:
    client = OpenAIClient() if USE_OPENAI else FakeLLMClient()
    enriched_rows = []

    for _, row in df.iterrows():
        row_dict = row.fillna("").to_dict()

        try:
            enrichment = client.enrich_transport_response(row_dict)
            enrichment = validate_enrichment(enrichment)

            enriched_rows.append({
                **row_dict,
                **enrichment,
                "error": "",
            })

        except Exception as error:
            enriched_rows.append({
                **row_dict,
                "normalized_city": "",
                "city_cluster": "",
                "transport_profile": "OTHER",
                "needs_action": True,
                "error": str(error),
                "alternative_clusters": [],
                "confidence": 0,
                "reason": "",
            })

    return pd.DataFrame(enriched_rows)


def calculate_match_score(passenger: dict, driver: dict):
    passenger_cluster = passenger["city_cluster"]
    driver_cluster = driver["city_cluster"]

    alternative_clusters = passenger.get("alternative_clusters", [])

    if passenger_cluster == driver_cluster:
        return 100, "Same departure area"

    if driver_cluster in alternative_clusters:
        return 80, "Alternative departure area"

    return None, None


def generate_matches(enriched_df: pd.DataFrame) -> pd.DataFrame:
    drivers = enriched_df[
        enriched_df["transport_profile"] == "DRIVER"
    ]

    passengers = enriched_df[
        enriched_df["transport_profile"].isin(
            ["PASSENGER", "TRAIN_CARPOOL"]
        )
    ]

    matches = []

    for _, passenger in passengers.iterrows():

        for _, driver in drivers.iterrows():

            available_seats = int(
                float(driver.get("available_seats", 0) or 0)
            )

            if available_seats <= 0:
                continue

            score, reason = calculate_match_score(
                passenger,
                driver,
            )

            if score is None:
                continue

            matches.append(
                {
                    "passenger_name": passenger["name"],
                    "passenger_city": passenger["departure_city"],
                    "driver_name": driver["name"],
                    "driver_city": driver["departure_city"],
                    "city_cluster": driver["city_cluster"],
                    "available_seats": available_seats,
                    "match_score": score,
                    "reason": reason,
                }
            )

    return pd.DataFrame(matches)


def main() -> None:
    try:
        print("Loading input data...")
        df = load_data(INPUT_FILE)

        print("Enriching responses...")
        enriched_df = enrich_rows(df)

        print("Exporting enriched data...")
        enriched_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

        print("Done.")
        print(f"Output file: {OUTPUT_FILE}")

        
        print("Generating carpool match suggestions...")
        matches_df = generate_matches(enriched_df)
        matches_df.to_csv(MATCHES_FILE, index=False, encoding="utf-8")

        print(f"Matches file: {MATCHES_FILE}")

    except Exception as error:
        print(f"Error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()