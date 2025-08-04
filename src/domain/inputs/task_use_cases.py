from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.task import Task, TaskStatus, TaskPriority


class TaskUseCases(ABC):
    @abstractmethod
    async def create(self, task: Task) -> Task:
        pass

    @abstractmethod
    async def get(self, task_id: int) -> Optional[Task]:
        pass

    @abstractmethod
    async def update(self, task_id: int, task: Task) -> Task:
        pass

    @abstractmethod
    async def delete(self, task_id: int) -> bool:
        pass

    @abstractmethod
    async def change_status(self, task_id: int, status: TaskStatus) -> Task:
        pass

    @abstractmethod
    async def get_by_filters(
        self,
        task_list_id: Optional[int] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
    ) -> List[Task]:
        pass

    @abstractmethod
    async def calculate_completion_percentage(self, task_list_id: int) -> float:
        pass
