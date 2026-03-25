from pydantic import BaseModel
from datetime import datetime

class PaymentCreate(BaseModel):
    listing_id: int

class PaymentResponse(BaseModel):
    id: int
    amount: float
    status: str
    reference: str
    created_at: datetime
    listing_id: int
    buyer_id: int
    seller_id: int

    class Config:
        from_attributes = True