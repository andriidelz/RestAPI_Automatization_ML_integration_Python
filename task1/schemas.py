from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    completed: bool = False

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    status: str
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    project_id: Optional[int] = None
    created_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }
