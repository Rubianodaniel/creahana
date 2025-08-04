from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.task import Task, TaskStatus, TaskPriority


class TaskRepository(ABC):
    @abstractmethod
    async def create(self, task: Task) -> Task:
        pass

    @abstractmethod
    async def get_by_id(self, task_id: int) -> Optional[Task]:
        pass

    @abstractmethod
    async def update(self, task: Task) -> Task:
        pass

    @abstractmethod
    async def delete(self, task_id: int) -> bool:
        pass

    @abstractmethod
    async def get_by_task_list_id(self, task_list_id: int) -> List[Task]:
        pass

    @abstractmethod
    async def get_tasks_by_filters(
        self,
        task_list_id: Optional[int] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
    ) -> List[Task]:
        pass
