from pydantic import BaseModel
from typing import Optional
from enum import Enum

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
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    suffix: Optional[str] = None

    class Config:
        orm_mode = True


# Schema for Member Address
class MemberAddressSchema(BaseModel):
    house_number: Optional[str] = None
    street_name: str
    barangay: str
    city: str
    province: str
    region: str

    class Config:
        orm_mode = True





# Schema for Creating a Member
class MemberCreateSchema(BaseModel):
    mobile_number: str
    #mpin: str  # Should be 4 digits (validation can be added)
    account_type: AccountTypeEnum = AccountTypeEnum.MEMBER
    referral_id: str
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
