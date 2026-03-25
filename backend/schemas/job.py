from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobCreate(BaseModel):
    title: str
    description: str
    budget: str
    category: str

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    budget: Optional[str] = None
    category: Optional[str] = None
    is_open: Optional[bool] = None

class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    budget: str
    category: str
    is_open: bool
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True

class JobApplicationCreate(BaseModel):
    cover_letter: str

class JobApplicationResponse(BaseModel):
    id: int
    cover_letter: str
    status: str
    created_at: datetime
    job_id: int
    applicant_id: int

    class Config:
        from_attributes = True