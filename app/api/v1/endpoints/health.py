from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.user import User
from app.services.health_score import compute_health_score
from app.services.fhir import build_health_observation
from app.clients.fhir_client import fetch_patient

router = APIRouter()


@router.get("/get_health_score")
async def get_health_score(
    user_id: int, days: int = 30, fhir: bool = True, db: Session = Depends(get_db)
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    payload = compute_health_score(db, user_id=user_id, days=days)
    if fhir:
        return build_health_observation(user_id, payload)
    return payload


@router.get("/external_patient/{patient_id}")
async def external_patient(patient_id: str):
    """Demonstrate integration with external FHIR (fetch Patient)."""
    return await fetch_patient(patient_id)
