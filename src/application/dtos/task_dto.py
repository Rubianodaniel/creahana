from typing import Optional, List
from pydantic import BaseModel
from src.domain.entities.task import Task, TaskStatus, TaskPriority


class TaskFiltersDTO(BaseModel):
    task_list_id: Optional[int] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None


class TaskListWithCompletionDTO(BaseModel):
    task_list_id: int
    completion_percentage: float
    tasks: List[Task]
