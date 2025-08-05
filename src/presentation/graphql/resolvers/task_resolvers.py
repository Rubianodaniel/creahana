from typing import List, Optional
import strawberry
from src.domain.entities.task import Task, TaskStatus, TaskPriority
from src.application.use_cases.task.task_service import TaskService
from src.presentation.shared.dependencies.service_factory import ServiceFactory
from src.presentation.graphql.types.task_list_types import (
    TaskType,
    TaskCreateInput,
    TaskUpdateInput,
    TaskStatusUpdateInput,
    task_to_graphql
)
from src.infrastructure.database.connection import get_db_session




@strawberry.type
class TaskQuery:
    @strawberry.field
    async def task(self, id: int) -> Optional[TaskType]:
        async for session in get_db_session():
            service = ServiceFactory.create_task_service(session)
            result = await service.get(id)
            if not result:
                return None
            return task_to_graphql(result)

    @strawberry.field
    async def tasks(self) -> List[TaskType]:
        async for session in get_db_session():
            service = ServiceFactory.create_task_service(session)
            results = await service.list_all()
            return [task_to_graphql(result) for result in results]


@strawberry.type
class TaskMutation:
    @strawberry.mutation
    async def create_task(self, input: TaskCreateInput) -> TaskType:
        async for session in get_db_session():
            service = ServiceFactory.create_task_service(session)
            
            try:
                task = Task(
                    title=input.title,
                    description=input.description,
                    task_list_id=input.task_list_id,
                    status=TaskStatus(input.status.value),
                    priority=TaskPriority(input.priority.value),
                    assigned_user_id=input.assigned_user_id,
                    due_date=input.due_date
                )
                
                result = await service.create(task)
                return task_to_graphql(result)
            except Exception as e:
                # Log the error for debugging
                print(f"GraphQL createTask error: {e}")
                raise Exception(f"Failed to create task: {str(e)}")

    @strawberry.mutation
    async def update_task(self, id: int, input: TaskUpdateInput) -> Optional[TaskType]:
        async for session in get_db_session():
            service = ServiceFactory.create_task_service(session)
            
            task = Task(
                title=input.title,
                description=input.description,
                task_list_id=input.task_list_id,
                status=TaskStatus(input.status.value) if input.status else None,
                priority=TaskPriority(input.priority.value) if input.priority else None,
                assigned_user_id=input.assigned_user_id,
                due_date=input.due_date
            )
            
            try:
                result = await service.update(id, task)
                return task_to_graphql(result)
            except ValueError:
                return None

    @strawberry.mutation
    async def delete_task(self, id: int) -> bool:
        async for session in get_db_session():
            service = ServiceFactory.create_task_service(session)
            return await service.delete(id)

    @strawberry.mutation
    async def change_task_status(self, id: int, input: TaskStatusUpdateInput) -> Optional[TaskType]:
        async for session in get_db_session():
            service = ServiceFactory.create_task_service(session)
            
            try:
                result = await service.change_status(id, TaskStatus(input.status.value))
                return task_to_graphql(result)
            except ValueError:
                return None