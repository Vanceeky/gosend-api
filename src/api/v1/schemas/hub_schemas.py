from pydantic import BaseModel, Field

from datetime import datetime
from typing import Optional, List


class CreateHub(BaseModel):
    hub_name: str
    hub_user: str

    region: str
    province: str
    municipality_city: str
    barangay: Optional[str]


    class Config:
        from_attributes = True

class HubListResponse(CreateHub):
    id: str
    reward_points: float
    hub_user_id: str  # Added to include member_id instead of mobile_number
    hub_user_name: str  # Added formatted name field
    created_at: datetime

    
    class Config:
        from_attributes = True