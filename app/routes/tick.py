from fastapi import APIRouter
from app.schemas.inbound import TickPayload
from app.schemas.outbound import TickResponse, ActionItem
from app.engine.decision_engine import DecisionEngine

router = APIRouter()

@router.post("/v1/tick", response_model=TickResponse)
async def tick(payload: TickPayload):
    actions_raw = DecisionEngine.process_tick(payload.available_triggers)
    actions = [ActionItem(**act) for act in actions_raw]
    return TickResponse(actions=actions)
