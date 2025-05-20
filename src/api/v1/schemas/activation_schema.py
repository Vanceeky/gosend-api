from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ActivationHistorySchema(BaseModel):
    activation_id: str
    member_id: str  # Add this
    activated_member_name: str
    activated_at: datetime
    amount: float
    currency: str
    status: str
    reference_id: str
    activated_by: str  # Add this
    activated_by_role: Optional[str]  # Add this
    extra_metadata: Optional[str] = None
    created_at: str

    class Config:
        orm_mode = True
