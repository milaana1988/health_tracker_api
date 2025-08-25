from datetime import datetime
from typing import Any, Dict

# Minimal FHIR Observation constructor for our health score
# NOTE: This is a pragmatic subset for the assignment, not a full FHIR model.


def build_health_observation(user_id: int, score_payload: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    components = []

    def comp(code: str, display: str, value: float, unit: str = "points"):
        return {
            "code": {
                "coding": [
                    {
                        "system": "http://example.org/fhir/CodeSystem/health-metrics",
                        "code": code,
                        "display": display,
                    }
                ],
                "text": display,
            },
            "valueQuantity": {
                "value": round(float(value), 2),
                "unit": unit,
                "system": "http://unitsofmeasure.org",
            },
        }

    c = score_payload.get("components", {})
    components.append(comp("steps-score", "Steps sub-score", c.get("steps_score", 0)))
    components.append(comp("sleep-score", "Sleep sub-score", c.get("sleep_score", 0)))
    components.append(comp("glucose-score", "Glucose sub-score", c.get("glucose_score", 0)))

    observation = {
        "resourceType": "Observation",
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "activity",
                        "display": "Activity",
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "76484-0",
                    "display": "Composite health score",
                }
            ],
            "text": "Composite health score",
        },
        "subject": {"reference": f"Patient/{user_id}"},
        "effectiveDateTime": now,
        "valueQuantity": {
            "value": score_payload.get("score", 0.0),
            "unit": "points",
            "system": "http://unitsofmeasure.org",
        },
        "component": components,
        "note": [{"text": f"Window since {score_payload.get('since')}"}],
    }
    return observation
