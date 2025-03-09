from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

# Schema for Wallet (since a member has a wallet)
class WalletSchema(BaseModel):
    wallet_id: str
    public_address: str

    class Config:
        orm_mode = True

class MemberWalletBaseSchema(BaseModel):
    """Base schema for MemberWallet"""
    wallet_id: UUID4
    member_id: UUID4
    is_primary: bool = False


class MemberWalletCreateSchema(MemberWalletBaseSchema):
    """Schema for creating a new MemberWallet"""
    pass  # Since all required fields are already in the base schema


class MemberWalletResponseSchema(MemberWalletBaseSchema):
    """Response schema for returning MemberWallet details"""
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows SQLAlchemy models to be converted to Pydantic