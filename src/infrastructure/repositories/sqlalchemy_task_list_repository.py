from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.task_list import TaskList
from src.domain.exceptions.task_list_exceptions import TaskListHasTasksException
from src.domain.outputs.task_list_repository import TaskListRepository
from src.infrastructure.database.mappers import TaskListMapper
from src.infrastructure.database.models.task_list_model import TaskListModel


class SQLAlchemyTaskListRepository(TaskListRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, task_list: TaskList) -> TaskList:
        model = TaskListMapper.to_model(task_list)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return TaskListMapper.to_domain(model)

    async def get_by_id(self, task_list_id: int) -> Optional[TaskList]:
        result = await self.session.execute(select(TaskListModel).where(TaskListModel.id == task_list_id))
        model = result.scalar_one_or_none()
        return TaskListMapper.to_domain(model) if model else None

    async def update(self, task_list: TaskList) -> TaskList:
        result = await self.session.execute(select(TaskListModel).where(TaskListModel.id == task_list.id))
        model = result.scalar_one_or_none()

        if not model:
            raise ValueError(f"TaskList with id {task_list.id} not found")

        model.title = task_list.title
        model.description = task_list.description
        model.user_id = task_list.user_id
        model.is_active = task_list.is_active

        await self.session.commit()
        await self.session.refresh(model)
        return TaskListMapper.to_domain(model)

    async def delete(self, task_list_id: int) -> bool:
        try:
            result = await self.session.execute(select(TaskListModel).where(TaskListModel.id == task_list_id))
            model = result.scalar_one_or_none()
            if model:
                await self.session.delete(model)
                await self.session.flush()  # Use flush instead of commit
                return True
            return False
        except IntegrityError as e:
            await self.session.rollback()
            # Check if it's a foreign key constraint error
            if "foreign key constraint" in str(e).lower() or "violates foreign key" in str(e).lower():
                raise TaskListHasTasksException(task_list_id)
            # Re-raise other integrity errors
            raise e

    async def list_all(self) -> List[TaskList]:
        result = await self.session.execute(select(TaskListModel))
        models = result.scalars().all()
        return [TaskListMapper.to_domain(model) for model in models]
