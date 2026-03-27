from pydantic import BaseModel, EmailStr
from typing import Optional

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    matric_number: Optional[str] = None
    phone_number: Optional[str] = None

class RoleUpdate(BaseModel):
    role: str