from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict

class HealthzResponse(BaseModel):
    status: str = "ok"
    uptime_seconds: int
    contexts_loaded: Dict[str, int]

class MetadataResponse(BaseModel):
    team_name: str
    team_members: List[str]
    model: str
    approach: str
    contact_email: str
    version: str
    submitted_at: str

class ContextResponseSuccess(BaseModel):
    accepted: bool = True
    ack_id: str
    stored_at: str

class ContextResponseConflict(BaseModel):
    accepted: bool = False
    reason: str = "stale_version"
    current_version: int

class ActionItem(BaseModel):
    conversation_id: str
    merchant_id: str
    customer_id: Optional[str] = None
    send_as: str = "vera"
    trigger_id: str
    template_name: str
    template_params: List[str]
    body: str
    cta: str
    suppression_key: str
    rationale: str

class TickResponse(BaseModel):
    actions: List[ActionItem] = []

class ReplyResponse(BaseModel):
    action: str  # 'send' | 'wait' | 'end'
    body: Optional[str] = None
    cta: Optional[str] = None
    wait_seconds: Optional[int] = None
    rationale: str
