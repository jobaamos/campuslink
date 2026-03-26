from pydantic import BaseModel
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    message: str
    is_read: bool
    notification_type: str
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True