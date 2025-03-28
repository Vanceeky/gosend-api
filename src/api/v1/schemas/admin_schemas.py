from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class AccountTypeEnum(str, Enum):
    ADMIN = 'ADMIN'
    CUSTOMER_SUPPORT = 'CUSTOMER_SUPPORT'
    INVESTOR = 'INVESTOR'


class AdminAccountCreate(BaseModel):
    mobile_number: str = Field(..., min_length=10, max_length=10)
    username: str
    password: str
    account_type: AccountTypeEnum = AccountTypeEnum.CUSTOMER_SUPPORT

    class Config:
        orm_mode = True

class AdminAccountResponse(BaseModel):
    id: str
    mobile_number: str = Field(..., min_length=10, max_length=10)
    username: str
    account_type: AccountTypeEnum
    account_url: str

class AdminLoginRequest(BaseModel):
    username: str
    password: str


class ProcessActivation(BaseModel):
    Transaction_id: str
    otp_code: Optional[str]
    member_id: str