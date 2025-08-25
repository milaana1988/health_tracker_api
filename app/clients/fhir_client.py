import httpx
from app.core.config import get_settings

settings = get_settings()


async def fetch_patient(patient_id: str) -> dict:
    """Fetch a FHIR Patient resource from an external FHIR server (demo)."""

    base = settings.EXTERNAL_FHIR_BASE_URL.rstrip("/")
    url = f"{base}/Patient/{patient_id}"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()
