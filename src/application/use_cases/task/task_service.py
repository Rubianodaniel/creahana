from typing import List, Optional

from src.application.dtos.task_dto import TaskFiltersDTO
from src.domain.entities.task import Task, TaskStatus
from src.domain.inputs.task_use_cases import TaskUseCases
from src.domain.outputs.task_repository import TaskRepository


class TaskService(TaskUseCases):
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    async def create(self, task: Task) -> Task:
        return await self.repository.create(task)

    async def get(self, task_id: int) -> Optional[Task]:
        return await self.repository.get_by_id(task_id)

    async def update(self, task_id: int, task: Task) -> Task:
        # Get current task to preserve unmodified fields
        current_task = await self.repository.get_by_id(task_id)
        if not current_task:
            raise ValueError("Task not found")

        # Update only the fields that are provided (not None)
        updated_task = Task(
            id=task_id,
            title=task.title if task.title is not None else current_task.title,
            description=task.description if task.description is not None else current_task.description,
            task_list_id=task.task_list_id if task.task_list_id is not None else current_task.task_list_id,
            status=task.status if task.status is not None else current_task.status,
            priority=task.priority if task.priority is not None else current_task.priority,
            assigned_user_id=task.assigned_user_id if task.assigned_user_id is not None else current_task.assigned_user_id,
            due_date=task.due_date if task.due_date is not None else current_task.due_date,
            is_active=current_task.is_active,
            created_at=current_task.created_at,
            updated_at=current_task.updated_at,
        )

        return await self.repository.update(updated_task)

    async def delete(self, task_id: int) -> bool:
        return await self.repository.delete(task_id)

    async def list_all(self) -> List[Task]:
        return await self.repository.list_all()

    async def change_status(self, task_id: int, status: TaskStatus) -> Task:
        task = await self.repository.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} not found")

        task.status = status
        return await self.repository.update(task)

    async def get_by_filters(self, filters: TaskFiltersDTO) -> List[Task]:
        return await self.repository.get_tasks_by_filters(filters.task_list_id, filters.status, filters.priority)

    async def calculate_completion_percentage(self, task_list_id: int) -> float:
        tasks = await self.repository.get_by_task_list_id(task_list_id)
        if not tasks:
            return 0.0

        completed_tasks = [task for task in tasks if task.status == TaskStatus.COMPLETED]
        return (len(completed_tasks) / len(tasks)) * 100
