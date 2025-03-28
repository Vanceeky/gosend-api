from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class RewardSchema(BaseModel):
    id: str
    reward_source_type: str
    reward_points: float
    reward_from: str
    reward_from_name: str  # Added full name
    receiver: str
    receiver_name: str  # Added full name
    title: str
    description: Optional[str] = None
    status: str
    reference_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class RewardListSchema(BaseModel):
    receiver: str
    total_rewards: float
    rewards: List[RewardSchema]

    model_config = {"from_attributes": True}
