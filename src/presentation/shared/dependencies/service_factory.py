from sqlalchemy.ext.asyncio import AsyncSession
from src.application.use_cases.task_list.task_list_service import TaskListService
from src.application.use_cases.task.task_service import TaskService
from src.infrastructure.repositories.sqlalchemy_task_list_repository import (
    SQLAlchemyTaskListRepository,
)
from src.infrastructure.repositories.sqlalchemy_task_repository import (
    SQLAlchemyTaskRepository,
)


class ServiceFactory:
    @staticmethod
    def create_task_list_service(session: AsyncSession) -> TaskListService:
        repository = SQLAlchemyTaskListRepository(session)
        return TaskListService(repository)

    @staticmethod
    def create_task_service(session: AsyncSession) -> TaskService:
        repository = SQLAlchemyTaskRepository(session)
        return TaskService(repository)