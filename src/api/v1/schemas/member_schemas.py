from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime

from api.v1.schemas.wallet_schemas import WalletSchema

# Enum for account types
class AccountTypeEnum(str, Enum):
    MEMBER = "MEMBER"
    MERCHANT = "MERCHANT"
    INVESTOR = "INVESTOR"
    LEADER = "LEADER"
    HUB = "HUB"
    ADMIN = "ADMIN"
    SUPERADMIN = "SUPERADMIN"
    CUSTOMER_SUPPORT = "CUSTOMER_SUPPORT"


# Schema for Member Details
class MemberDetailsSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    suffix_name: Optional[str] = None

    class Config:
        orm_mode = True


# Schema for Member Address
class MemberAddressSchema(BaseModel):
    house_number: Optional[str] = None
    street_name: Optional[str] = None  # Make this optional
    barangay: Optional[str] = None  # Make this optional
    city: Optional[str] = None  # Make this optional
    province: Optional[str] = None  # Make this optional
    region: Optional[str] = None  # Make this optional

    class Config:
        orm_mode = True





# Schema for Creating a Member
class MemberCreateSchema(BaseModel):
    mobile_number: str
    #mpin: str  # Should be 4 digits (validation can be added)
    account_type: AccountTypeEnum = AccountTypeEnum.MEMBER
    #referral_id: str
    details: MemberDetailsSchema
    address: MemberAddressSchema

    class Config:
        orm_mode = True


# Schema for Reading a Member (Response Schema)
class MemberReadSchema(BaseModel):
    member_id: str
    mobile_number: str
    account_type: AccountTypeEnum
    referral_id: str
    is_activated: bool
    is_kyc_verified: bool
    details: Optional[MemberDetailsSchema] = None
    address: Optional[MemberAddressSchema] = None
    wallet: Optional[WalletSchema] = None

    class Config:
        orm_mode = True



class WalletResponse(BaseModel):
    wallet_balance: float
    reward_points: Optional[float] = 0.0

class MemberListResponse(BaseModel):
    user_id: str
    mobile_number: str
    #community_name: str
    status: bool
    is_activated: bool
    is_kyc_verified: bool
    community_name: str
    community_id: str
    created_at: str
    updated_at: str
    user_address: MemberAddressSchema
    user_details: MemberDetailsSchema
    wallet: WalletResponse



class MemberInfoSchema(BaseModel):
    member_id: str
    mobile_number: str
    referral_id: str
    account_type: str
    is_activated: bool
    is_kyc_verified: bool
    details: Optional[MemberDetailsSchema] = None
    address: Optional[MemberAddressSchema] = None
    wallet: Optional[WalletResponse] = None

    class Config:
        orm_mode = True



class PurchaseHistorySchema(BaseModel):
    purchase_id: str
    business_name: str
    amount: float
    reference_id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
