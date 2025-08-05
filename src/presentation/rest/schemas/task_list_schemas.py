from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TaskListCreateSchema(BaseModel):
    title: str = Field(..., min_length=4)
    description: Optional[str] = None
    user_id: Optional[int] = None


class TaskListUpdateSchema(BaseModel):
    title: str
    description: Optional[str] = None


class TaskListResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: Optional[str] = None
    user_id: Optional[int] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None