from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str

class ReviewResponse(BaseModel):
    id: int
    rating: int
    comment: str
    created_at: datetime
    listing_id: int
    reviewer_id: int

    class Config:
        from_attributes = True