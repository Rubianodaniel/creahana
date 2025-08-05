from typing import List, Optional

import strawberry
from strawberry.types import Info

from src.domain.entities.task import Task, TaskPriority, TaskStatus
from src.domain.exceptions.task_exceptions import InvalidTaskListException
from src.presentation.graphql.context import GraphQLContext
from src.presentation.graphql.types.task_list_types import (
    TaskCreateInput,
    TaskStatusUpdateInput,
    TaskType,
    TaskUpdateInput,
    task_to_graphql,
)
from src.presentation.shared.dependencies.service_factory import ServiceFactory


@strawberry.type
class TaskQuery:
    @strawberry.field
    async def task(self, id: int, info: Info[GraphQLContext, None]) -> Optional[TaskType]:
        try:
            if id <= 0:
                raise ValueError("Task ID must be a positive integer")

            session = info.context.db_session
            service = ServiceFactory.create_task_service(session)
            result = await service.get(id)

            if not result:
                return None

            return task_to_graphql(result)
        except ValueError as e:
            print(f"GraphQL task validation error: {e}")
            return None
        except Exception as e:
            print(f"GraphQL task error: {e}")
            raise Exception(f"Failed to retrieve task: {str(e)}")

    @strawberry.field
    async def tasks(self, info: Info[GraphQLContext, None]) -> List[TaskType]:
        try:
            session = info.context.db_session
            service = ServiceFactory.create_task_service(session)
            results = await service.list_all()
            return [task_to_graphql(result) for result in results]
        except Exception as e:
            print(f"GraphQL tasks error: {e}")
            raise Exception(f"Failed to retrieve tasks: {str(e)}")


@strawberry.type
class TaskMutation:
    @strawberry.mutation
    async def create_task(self, input: TaskCreateInput, info: Info[GraphQLContext, None]) -> TaskType:
        try:
            session = info.context.db_session
            service = ServiceFactory.create_task_service(session)

            task = Task(
                title=input.title,
                description=input.description,
                task_list_id=input.task_list_id,
                status=TaskStatus(input.status.value),
                priority=TaskPriority(input.priority.value),
                assigned_user_id=input.assigned_user_id,
                due_date=input.due_date,
            )

            result = await service.create(task)
            return task_to_graphql(result)
        except InvalidTaskListException as e:
            print(f"GraphQL createTask error: {e}")
            raise Exception(f"Task list {e.task_list_id} does not exist")
        except Exception as e:
            print(f"GraphQL createTask error: {e}")
            raise Exception(f"Failed to create task: {str(e)}")

    @strawberry.mutation
    async def update_task(self, id: int, input: TaskUpdateInput, info: Info[GraphQLContext, None]) -> Optional[TaskType]:
        session = info.context.db_session
        service = ServiceFactory.create_task_service(session)

        task = Task(
            title=input.title,
            description=input.description,
            task_list_id=input.task_list_id,
            status=TaskStatus(input.status.value) if input.status else None,
            priority=TaskPriority(input.priority.value) if input.priority else None,
            assigned_user_id=input.assigned_user_id,
            due_date=input.due_date,
        )

        try:
            result = await service.update(id, task)
            return task_to_graphql(result)
        except ValueError:
            return None

    @strawberry.mutation
    async def delete_task(self, id: int, info: Info[GraphQLContext, None]) -> bool:
        session = info.context.db_session
        service = ServiceFactory.create_task_service(session)
        return await service.delete(id)

    @strawberry.mutation
    async def change_task_status(self, id: int, input: TaskStatusUpdateInput, info: Info[GraphQLContext, None]) -> Optional[TaskType]:
        session = info.context.db_session
        service = ServiceFactory.create_task_service(session)

        try:
            result = await service.change_status(id, TaskStatus(input.status.value))
            return task_to_graphql(result)
        except ValueError:
            return None
