from pydantic import BaseModel, Field

from datetime import datetime
from typing import Optional, List
from uuid import uuid4

class CreateCommunity(BaseModel):
    community_name: str
    community_leader: str = Field(..., min_length=10, max_length=10)

class CommunityResponse(CreateCommunity):
    community_id: uuid4

    class Config:
        from_attributes = True


class CommunityListResponse(BaseModel):
    community_id: str
    community_name: str
    leader_name: str | None
    total_members: int
    reward_points: float
   # date_added: datetime


    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}  # Convert datetime to ISO string



class MemberResponse(BaseModel):
    user_id: str
    mobile_number: str
    account_type: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    suffix_name: Optional[str]
    is_activated: bool
    is_kyc_verified: bool

class LeaderResponse(BaseModel):
    user_id: str
    mobile_number: str
    account_type: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    suffix_name: Optional[str]
    is_activated: bool
    is_kyc_verified: bool

class CommunityDetailsResponse(BaseModel):
    community_name: str
    reward_points: float  # Add reward_points
    leader: LeaderResponse
    members: List[MemberResponse]
