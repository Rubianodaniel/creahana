from typing import List, Optional

from pydantic import BaseModel

from src.domain.entities.task import Task, TaskPriority, TaskStatus


class TaskFiltersDTO(BaseModel):
    task_list_id: Optional[int] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None


class TaskListWithCompletionDTO(BaseModel):
    task_list_id: int
    completion_percentage: float
    tasks: List[Task]
