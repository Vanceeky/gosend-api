from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import uuid4
from datetime import datetime


class MerchantBase(BaseModel):
    mobile_number: str = Field(..., min_length=10, max_length=10)
    business_name: str
    business_type: str
    discount: Optional[float] = None
    merchant_wallet: Optional[float] = 0.00
    reward_points: Optional[float] = 0.00
    #qr_code_url: str


class MerchantCreate(MerchantBase):
    latitude: str
    longitude: str
    region: str
    province: str
    municipality_city: str
    barangay: str
    street: Optional[str] = None

class MerchantResponse(MerchantBase):
    merchant_id: str

    class Config:
        from_attributes = True

class MerchantPurchaseHistorySchema(BaseModel):
    purchase_id: str
    merchant_id: str
    name: str
    amount: float
    reference_id: str
    status: str
    purchase_date: datetime

    class Config:
        from_attributes = True


class MerchantPurchaseHistoryListResponse(BaseModel):
    purchases: List[MerchantPurchaseHistorySchema]



