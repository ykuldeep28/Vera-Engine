from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

class ContextPushPayload(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    scope: str
    context_id: str
    version: int
    payload: Dict[str, Any]
    delivered_at: Optional[str] = None

class TickPayload(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    now: str
    available_triggers: List[str] = Field(default_factory=list)

class ReplyPayload(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    conversation_id: str
    merchant_id: Optional[str] = None
    customer_id: Optional[str] = None
    from_role: Optional[str] = "merchant"
    message: str
    reply_text: Optional[str] = None  # fallback field if sent as reply_text
    received_at: Optional[str] = None
    turn_number: Optional[int] = 1

    def get_text(self) -> str:
        return self.message if self.message is not None else (self.reply_text or "")
