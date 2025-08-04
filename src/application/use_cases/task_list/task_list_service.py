from typing import List, Optional
from src.domain.entities.task_list import TaskList
from src.domain.inputs.task_list_use_cases import TaskListUseCases
from src.domain.outputs.task_list_repository import TaskListRepository


class TaskListService(TaskListUseCases):
    def __init__(self, repository: TaskListRepository):
        self.repository = repository

    async def create(self, task_list: TaskList) -> TaskList:
        return await self.repository.create(task_list)

    async def get(self, task_list_id: int) -> Optional[TaskList]:
        return await self.repository.get_by_id(task_list_id)

    async def update(self, task_list_id: int, task_list: TaskList) -> TaskList:
        task_list.id = task_list_id
        return await self.repository.update(task_list)

    async def delete(self, task_list_id: int) -> bool:
        return await self.repository.delete(task_list_id)

    async def list_all(self) -> List[TaskList]:
        return await self.repository.list_all()
