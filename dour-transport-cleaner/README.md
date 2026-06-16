# Dour Transport Cleaner

AI-powered transport coordination assistant for volunteer events.

This project was built to help organize transportation for 60–80 volunteers attending the Dour Festival by transforming messy Google Form responses into structured, actionable transport data.

---

## Problem

Event organizers often collect transportation information through Google Forms.

The resulting data usually contains:

- free-text cities
- alternative departure locations
- inconsistent transport preferences
- missing structure for matching drivers and passengers

As the number of volunteers grows, manually reviewing and coordinating transportation becomes time-consuming and error-prone.

---

## Solution

This project enriches raw transport responses using AI and generates carpool suggestions.

Pipeline:

```text
Raw responses
↓
AI enrichment
↓
Data validation
↓
Transport normalization
↓
Carpool matching suggestions
```

---

## Features

### AI enrichment

Transforms free-text responses into structured data:

- normalized city
- city cluster
- alternative clusters
- transport profile
- coordination needs
- confidence score
- reasoning

Example:

Input:

```text
Departure city: Villeurbanne
Alternative city: Lyon
Looking for carpool
```

Output:

```json
{
  "normalized_city": "VILLEURBANNE",
  "city_cluster": "LYON_AREA",
  "alternative_clusters": ["LYON_AREA"],
  "transport_profile": "PASSENGER",
  "needs_action": true
}
```

---

### Validation layer

All AI outputs are validated before being accepted.

Checks include:

- required fields
- allowed transport profiles
- confidence range
- data type validation

This follows a Human-in-the-Loop approach.

---

### Carpool suggestion engine

The system generates transport suggestions based on:

- departure area
- alternative departure areas
- available seats

Scoring example:

| Score | Logic |
|---------|---------|
| 100 | Same departure area |
| 80 | Alternative departure area |
| 60 | Compatible train + carpool route |

Suggestions are recommendations only.

The system never automatically assigns passengers to drivers.

---

## Project Structure

```text
dour-transport-cleaner/
│
├── data/
│   ├── input_responses.csv
│   ├── output_responses_enriched.csv
│   └── output_matches.csv
│
├── script.py
├── llm_client.py
├── prompt_builder.py
├── validator.py
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## Technologies

- Python
- Pandas
- OpenAI API
- dotenv

---

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key
USE_OPENAI=true
```

Run:

```bash
python script.py
```

---

## Example Outputs

### Enriched transport data

Generated file:

```text
output_responses_enriched.csv
```

Contains:

- normalized_city
- city_cluster
- alternative_clusters
- transport_profile
- needs_action
- confidence
- reason

---

### Carpool suggestions

Generated file:

```text
output_matches.csv
```

Example:

| Passenger | Driver | Score |
|------------|------------|------------|
| Julie Robert | Lisa Martin | 100 |
| Maxime Roux | Lisa Martin | 100 |
| Thomas Petit | Lisa Martin | 80 |

---

## Future Improvements

- Google Sheets integration
- Make automation
- Real-time enrichment
- Flask API deployment
- Advanced transport recommendation engine
- Multi-city route optimization

---

## Key Learnings

This project demonstrates:

- AI-assisted data enrichment
- validation of LLM outputs
- structured prompt engineering
- transport matching logic
- automation-oriented system design
- human-in-the-loop decision support

---

## Disclaimer

The matching engine provides suggestions only.

Final transportation decisions remain under human control.