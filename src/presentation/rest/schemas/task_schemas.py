from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from src.domain.entities.task import TaskStatus, TaskPriority


class TaskCreateSchema(BaseModel):
    title: str = Field(..., min_length=4)
    description: Optional[str] = None
    task_list_id: int
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_user_id: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    task_list_id: Optional[int] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_user_id: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: Optional[str] = None
    task_list_id: int
    status: TaskStatus
    priority: TaskPriority
    assigned_user_id: Optional[int] = None
    due_date: Optional[datetime] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TaskFiltersSchema(BaseModel):
    task_list_id: Optional[int] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None