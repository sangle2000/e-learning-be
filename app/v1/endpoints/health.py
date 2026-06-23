from fastapi import APIRouter
from app.schema.health import HealthResponse

router = APIRouter()


@router.get("", response_model=HealthResponse, summary="Check service health")
def get_health() -> HealthResponse:
    """
    Returns a simple JSON indicating that the server is online and operational.
    """
    return HealthResponse(status="ok")
