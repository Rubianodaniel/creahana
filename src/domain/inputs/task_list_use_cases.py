from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.task_list import TaskList


class TaskListUseCases(ABC):
    @abstractmethod
    async def create(self, task_list: TaskList) -> TaskList:
        pass

    @abstractmethod
    async def get(self, task_list_id: int) -> Optional[TaskList]:
        pass

    @abstractmethod
    async def update(self, task_list_id: int, task_list: TaskList) -> TaskList:
        pass

    @abstractmethod
    async def delete(self, task_list_id: int) -> bool:
        pass

    @abstractmethod
    async def list_all(self) -> List[TaskList]:
        pass
