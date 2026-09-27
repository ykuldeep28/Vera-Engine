from datetime import datetime, timezone
from fastapi import APIRouter, Response, status
from app.schemas.inbound import ContextPushPayload
from app.schemas.outbound import ContextResponseSuccess, ContextResponseConflict
from app.store.context_store import ContextStore

router = APIRouter()

@router.post("/v1/context")
async def push_context(payload: ContextPushPayload, response: Response):
    success, current_version = ContextStore.upsert_context(
        scope_type=payload.scope,
        scope_id=payload.context_id,
        version=payload.version,
        data=payload.payload
    )

    if not success:
        response.status_code = status.HTTP_409_CONFLICT
        return ContextResponseConflict(
            accepted=False,
            reason="stale_version",
            current_version=current_version
        )

    now_iso = datetime.now(timezone.utc).isoformat()
    return ContextResponseSuccess(
        accepted=True,
        ack_id=f"ack_{payload.context_id}_v{payload.version}",
        stored_at=now_iso
    )
