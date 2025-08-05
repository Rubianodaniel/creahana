from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from src.presentation.rest.schemas.task_schemas import TaskResponseSchema


class TaskListCreateSchema(BaseModel):
    title: str = Field(..., min_length=4)
    description: Optional[str] = None
    user_id: Optional[int] = None


class TaskListUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    user_id: Optional[int] = None


class TaskListResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: Optional[str] = None
    user_id: Optional[int] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TaskListWithTasksResponseSchema(TaskListResponseSchema):
    tasks: List[TaskResponseSchema]
    completion_percentage: float
    total_tasks: int
    completed_tasks: int