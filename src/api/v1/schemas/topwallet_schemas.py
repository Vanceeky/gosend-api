from pydantic import BaseModel

class P2PTransferRequest(BaseModel):
    from_user: str
    to_user: str
    amount: str
    coin: str = "peso"

class P2PprocessRequest(BaseModel):
    Transaction_id: str
    otp: str


class TWP2PTransferRequest(BaseModel):
    to_user: str
    amount: str
    coin: str = "peso"

