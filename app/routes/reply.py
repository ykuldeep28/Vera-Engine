from fastapi import APIRouter
from app.schemas.inbound import ReplyPayload
from app.schemas.outbound import ReplyResponse
from app.reply.reply_engine import ReplyEngine

router = APIRouter()

@router.post("/v1/reply", response_model=ReplyResponse)
async def reply(payload: ReplyPayload):
    text = payload.get_text()
    turn = payload.turn_number or 1
    result = ReplyEngine.handle_reply(
        conversation_id=payload.conversation_id,
        message_text=text,
        merchant_id=payload.merchant_id,
        customer_id=payload.customer_id,
        turn_number=turn
    )
    return ReplyResponse(**result)
