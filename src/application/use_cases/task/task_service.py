from typing import List, Optional
from src.domain.entities.task import Task, TaskStatus
from src.domain.inputs.task_use_cases import TaskUseCases
from src.domain.outputs.task_repository import TaskRepository
from src.application.dtos.task_dto import TaskFiltersDTO


class TaskService(TaskUseCases):
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    async def create(self, task: Task) -> Task:
        return await self.repository.create(task)

    async def get(self, task_id: int) -> Optional[Task]:
        return await self.repository.get_by_id(task_id)

    async def update(self, task_id: int, task: Task) -> Task:
        task.id = task_id
        return await self.repository.update(task)

    async def delete(self, task_id: int) -> bool:
        return await self.repository.delete(task_id)

    async def change_status(self, task_id: int, status: TaskStatus) -> Task:
        task = await self.repository.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} not found")

        task.status = status
        return await self.repository.update(task)

    async def get_by_filters(self, filters: TaskFiltersDTO) -> List[Task]:
        return await self.repository.get_tasks_by_filters(
            filters.task_list_id, filters.status, filters.priority
        )

    async def calculate_completion_percentage(self, task_list_id: int) -> float:
        tasks = await self.repository.get_by_task_list_id(task_list_id)
        if not tasks:
            return 0.0

        completed_tasks = [
            task for task in tasks if task.status == TaskStatus.COMPLETED
        ]
        return (len(completed_tasks) / len(tasks)) * 100
