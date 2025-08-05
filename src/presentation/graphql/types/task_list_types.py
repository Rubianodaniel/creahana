from datetime import datetime
from enum import Enum
from typing import List, Optional

import strawberry

from src.domain.entities.task import TaskPriority, TaskStatus


@strawberry.enum
class TaskStatusEnum(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@strawberry.enum
class TaskPriorityEnum(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@strawberry.type
class TaskListType:
    id: int
    title: str
    description: Optional[str] = None
    user_id: Optional[int] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@strawberry.type
class TaskType:
    id: int
    title: str
    description: Optional[str] = None
    task_list_id: int
    status: TaskStatusEnum
    priority: TaskPriorityEnum
    assigned_user_id: Optional[int] = None
    due_date: Optional[datetime] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@strawberry.type
class TaskListWithTasksType:
    id: int
    title: str
    description: Optional[str] = None
    user_id: Optional[int] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tasks: List[TaskType]
    completion_percentage: float
    total_tasks: int
    completed_tasks: int


@strawberry.input
class TaskListCreateInput:
    title: str
    description: Optional[str] = None
    user_id: Optional[int] = None

    def __post_init__(self):
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Title cannot exceed 200 characters")


@strawberry.input
class TaskListUpdateInput:
    title: Optional[str] = None
    description: Optional[str] = None
    user_id: Optional[int] = None


@strawberry.input
class TaskCreateInput:
    title: str
    description: Optional[str] = None
    task_list_id: int
    status: TaskStatusEnum = TaskStatusEnum.PENDING
    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM
    assigned_user_id: Optional[int] = None
    due_date: Optional[datetime] = None


@strawberry.input
class TaskUpdateInput:
    title: Optional[str] = None
    description: Optional[str] = None
    task_list_id: Optional[int] = None
    status: Optional[TaskStatusEnum] = None
    priority: Optional[TaskPriorityEnum] = None
    assigned_user_id: Optional[int] = None
    due_date: Optional[datetime] = None


@strawberry.input
class TaskStatusUpdateInput:
    status: TaskStatusEnum


# Helper functions for conversion
def task_list_to_graphql(domain_obj) -> TaskListType:
    return TaskListType(
        id=domain_obj.id,
        title=domain_obj.title,
        description=domain_obj.description,
        user_id=domain_obj.user_id,
        is_active=domain_obj.is_active,
        created_at=domain_obj.created_at,
        updated_at=domain_obj.updated_at,
    )


def task_to_graphql(domain_obj) -> TaskType:
    # Map domain enum values to GraphQL enum values
    status_mapping = {
        TaskStatus.PENDING: TaskStatusEnum.PENDING,
        TaskStatus.IN_PROGRESS: TaskStatusEnum.IN_PROGRESS,
        TaskStatus.COMPLETED: TaskStatusEnum.COMPLETED,
    }

    priority_mapping = {
        TaskPriority.LOW: TaskPriorityEnum.LOW,
        TaskPriority.MEDIUM: TaskPriorityEnum.MEDIUM,
        TaskPriority.HIGH: TaskPriorityEnum.HIGH,
    }

    return TaskType(
        id=domain_obj.id,
        title=domain_obj.title,
        description=domain_obj.description,
        task_list_id=domain_obj.task_list_id,
        status=status_mapping[domain_obj.status],
        priority=priority_mapping[domain_obj.priority],
        assigned_user_id=domain_obj.assigned_user_id,
        due_date=domain_obj.due_date,
        is_active=domain_obj.is_active,
        created_at=domain_obj.created_at,
        updated_at=domain_obj.updated_at,
    )
