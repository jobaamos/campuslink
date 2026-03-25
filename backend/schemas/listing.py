from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ListingCreate(BaseModel):
    title: str
    description: str
    price: float
    category: str
    listing_type: str

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    listing_type: Optional[str] = None
    is_available: Optional[bool] = None

class ListingResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    category: str
    listing_type: str
    is_available: bool
    created_at: datetime
    owner_id: int
    owner_name: Optional[str] = None
    owner_role: Optional[str] = None

    class Config:
        from_attributes = True