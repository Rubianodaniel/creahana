from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from src.domain.entities.task import Task, TaskStatus, TaskPriority
from src.domain.outputs.task_repository import TaskRepository
from src.infrastructure.database.models.task_model import TaskModel
from src.infrastructure.database.mappers import TaskMapper


class SQLAlchemyTaskRepository(TaskRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, task: Task) -> Task:
        model = TaskMapper.to_model(task)
        self.session.add(model)
        await self.session.flush()  # Solo flush para obtener ID
        await self.session.refresh(model)
        return TaskMapper.to_domain(model)

    async def get_by_id(self, task_id: int) -> Optional[Task]:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        model = result.scalar_one_or_none()
        return TaskMapper.to_domain(model) if model else None

    async def update(self, task: Task) -> Task:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.id == task.id)
        )
        model = result.scalar_one_or_none()

        if not model:
            raise ValueError(f"Task with id {task.id} not found")

        model.title = task.title
        model.description = task.description
        model.task_list_id = task.task_list_id
        model.status = task.status
        model.priority = task.priority
        model.assigned_user_id = task.assigned_user_id
        model.due_date = task.due_date
        model.is_active = task.is_active

        await self.session.flush()
        await self.session.refresh(model)
        return TaskMapper.to_domain(model)

    async def delete(self, task_id: int) -> bool:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.flush()
            return True
        return False

    async def list_all(self) -> List[Task]:
        result = await self.session.execute(select(TaskModel))
        models = result.scalars().all()
        return [TaskMapper.to_domain(model) for model in models]

    async def get_by_task_list_id(self, task_list_id: int) -> List[Task]:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.task_list_id == task_list_id)
        )
        models = result.scalars().all()
        return [TaskMapper.to_domain(model) for model in models]

    async def get_tasks_by_filters(
        self,
        task_list_id: Optional[int] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
    ) -> List[Task]:
        query = select(TaskModel)
        conditions = []

        if task_list_id is not None:
            conditions.append(TaskModel.task_list_id == task_list_id)
        if status is not None:
            conditions.append(TaskModel.status == status)
        if priority is not None:
            conditions.append(TaskModel.priority == priority)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.session.execute(query)
        models = result.scalars().all()
        return [TaskMapper.to_domain(model) for model in models]