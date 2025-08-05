from pydantic import BaseModel

from src.domain.entities.task import TaskStatus


class TaskStatusUpdateSchema(BaseModel):
    status: TaskStatus
