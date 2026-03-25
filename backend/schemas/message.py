from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    receiver_id: int
    content: str

class MessageResponse(BaseModel):
    id: int
    content: str
    is_read: bool
    created_at: datetime
    sender_id: int
    receiver_id: int

    class Config:
        from_attributes = True