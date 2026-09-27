import time
from fastapi import APIRouter
from app.config import (
    TEAM_NAME, TEAM_MEMBERS, MODEL_NAME, APPROACH,
    CONTACT_EMAIL, VERSION, SUBMITTED_AT
)
from app.schemas.outbound import HealthzResponse, MetadataResponse
from app.store.context_store import ContextStore

router = APIRouter()
START_TIME = time.time()

@router.get("/v1/healthz", response_model=HealthzResponse)
async def healthz():
    uptime = int(time.time() - START_TIME)
    counts = ContextStore.get_context_counts()
    return HealthzResponse(
        status="ok",
        uptime_seconds=uptime,
        contexts_loaded=counts
    )

@router.get("/v1/metadata", response_model=MetadataResponse)
async def metadata():
    return MetadataResponse(
        team_name=TEAM_NAME,
        team_members=TEAM_MEMBERS,
        model=MODEL_NAME,
        approach=APPROACH,
        contact_email=CONTACT_EMAIL,
        version=VERSION,
        submitted_at=SUBMITTED_AT
    )
