from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.auth.auth_service import AuthService
from src.application.use_cases.task.task_service import TaskService
from src.application.use_cases.task_list.task_list_service import TaskListService
from src.application.use_cases.user.user_service import UserService
from src.infrastructure.repositories.sqlalchemy_task_list_repository import (
    SQLAlchemyTaskListRepository,
)
from src.infrastructure.repositories.sqlalchemy_task_repository import (
    SQLAlchemyTaskRepository,
)
from src.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)


class ServiceFactory:
    @staticmethod
    def create_task_list_service(session: AsyncSession) -> TaskListService:
        task_list_repository = SQLAlchemyTaskListRepository(session)
        task_repository = SQLAlchemyTaskRepository(session)
        user_repository = SQLAlchemyUserRepository(session)
        return TaskListService(task_list_repository, task_repository, user_repository)

    @staticmethod
    def create_task_service(session: AsyncSession) -> TaskService:
        repository = SQLAlchemyTaskRepository(session)
        return TaskService(repository)

    @staticmethod
    def create_user_service(session: AsyncSession) -> UserService:
        repository = SQLAlchemyUserRepository(session)
        return UserService(repository)

    @staticmethod
    def create_auth_service(session: AsyncSession) -> AuthService:
        repository = SQLAlchemyUserRepository(session)
        return AuthService(repository)
