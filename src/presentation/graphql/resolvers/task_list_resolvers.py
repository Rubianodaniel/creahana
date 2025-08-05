from typing import List, Optional
import strawberry
from strawberry.types import Info
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.task_list import TaskList
from src.domain.entities.task import TaskStatus, TaskPriority
from src.application.use_cases.task_list.task_list_service import TaskListService
from src.presentation.shared.dependencies.service_factory import ServiceFactory
from src.presentation.graphql.types.task_list_types import (
    TaskListType,
    TaskListWithTasksType,
    TaskType,
    TaskListCreateInput,
    TaskListUpdateInput,
    task_list_to_graphql,
    task_to_graphql
)
from src.infrastructure.database.connection import get_db_session


async def get_session():
    """Helper to get session respecting dependency overrides"""
    session_gen = get_db_session()
    session = await session_gen.__anext__()
    return session




@strawberry.type
class TaskListQuery:
    @strawberry.field
    async def task_list(self, id: int) -> Optional[TaskListType]:
        session = await get_session()
        service = ServiceFactory.create_task_list_service(session)
        result = await service.get(id)
        if not result:
            return None
        return task_list_to_graphql(result)

    @strawberry.field
    async def task_lists(self) -> List[TaskListType]:
        session = await get_session()
        service = ServiceFactory.create_task_list_service(session)
        results = await service.list_all()
        return [task_list_to_graphql(result) for result in results]

    @strawberry.field
    async def task_list_with_tasks(
        self,
        id: int,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Optional[TaskListWithTasksType]:
        session = await get_session()
        service = ServiceFactory.create_task_list_service(session)
        
        # Convert string enums to domain enums
        status_enum = TaskStatus(status) if status else None
        priority_enum = TaskPriority(priority) if priority else None
        
        try:
            result = await service.get_tasks_with_completion(id, status_enum, priority_enum)
            return TaskListWithTasksType(
                id=result.task_list.id,
                title=result.task_list.title,
                description=result.task_list.description,
                user_id=result.task_list.user_id,
                is_active=result.task_list.is_active,
                created_at=result.task_list.created_at,
                updated_at=result.task_list.updated_at,
                tasks=[task_to_graphql(task) for task in result.tasks],
                completion_percentage=result.completion_percentage,
                total_tasks=result.total_tasks,
                completed_tasks=result.completed_tasks
            )
        except ValueError:
            return None


@strawberry.type
class TaskListMutation:
    @strawberry.mutation
    async def create_task_list(self, input: TaskListCreateInput) -> TaskListType:
        session = await get_session()
        service = ServiceFactory.create_task_list_service(session)
        
        task_list = TaskList(
            title=input.title,
            description=input.description,
            user_id=input.user_id
        )
        
        result = await service.create(task_list)
        return task_list_to_graphql(result)

    @strawberry.mutation
    async def update_task_list(self, id: int, input: TaskListUpdateInput) -> Optional[TaskListType]:
        session = await get_session()
        service = ServiceFactory.create_task_list_service(session)
        
        task_list = TaskList(
            title=input.title,
            description=input.description,
            user_id=input.user_id
        )
        
        try:
            result = await service.update(id, task_list)
            return task_list_to_graphql(result)
        except ValueError:
            return None

    @strawberry.mutation
    async def delete_task_list(self, id: int) -> bool:
        session = await get_session()
        service = ServiceFactory.create_task_list_service(session)
        return await service.delete(id)