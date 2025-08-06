from typing import List, Optional

import strawberry
from strawberry.types import Info

from src.domain.entities.task import TaskPriority, TaskStatus
from src.domain.entities.task_list import TaskList
from src.domain.exceptions.task_list_exceptions import TaskListHasTasksException
from src.presentation.graphql.context import GraphQLContext
from src.presentation.graphql.types.task_list_types import (
    TaskListCreateInput,
    TaskListType,
    TaskListUpdateInput,
    TaskListWithTasksType,
    task_list_to_graphql,
    task_to_graphql,
)
from src.presentation.shared.dependencies.service_factory import ServiceFactory


@strawberry.type
class TaskListQuery:
    @strawberry.field
    async def task_list(self, id: int, info: Info[GraphQLContext, None]) -> Optional[TaskListType]:
        try:
            if id <= 0:
                raise ValueError("Task list ID must be a positive integer")

            session = info.context.db_session
            service = ServiceFactory.create_task_list_service(session)
            result = await service.get(id)

            if not result:
                return None

            return task_list_to_graphql(result)
        except ValueError as e:
            print(f"GraphQL task_list validation error: {e}")
            return None
        except Exception as e:
            print(f"GraphQL task_list error: {e}")
            raise Exception(f"Failed to retrieve task list: {str(e)}")

    @strawberry.field
    async def task_lists(self, info: Info[GraphQLContext, None]) -> List[TaskListType]:
        try:
            session = info.context.db_session
            service = ServiceFactory.create_task_list_service(session)
            results = await service.list_all()
            return [task_list_to_graphql(result) for result in results]
        except Exception as e:
            print(f"GraphQL task_lists error: {e}")
            raise Exception(f"Failed to retrieve task lists: {str(e)}")

    @strawberry.field
    async def task_list_with_tasks(
        self,
        id: int,
        info: Info[GraphQLContext, None],
        status: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> Optional[TaskListWithTasksType]:
        try:
            if id <= 0:
                raise ValueError("Task list ID must be a positive integer")

            session = info.context.db_session
            service = ServiceFactory.create_task_list_service(session)

            # Convert string enums to domain enums
            status_enum = TaskStatus(status) if status else None
            priority_enum = TaskPriority(priority) if priority else None

            result = await service.get_tasks_with_completion(id, status_enum, priority_enum)

            if not result:
                return None

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
                completed_tasks=result.completed_tasks,
            )
        except ValueError as e:
            print(f"GraphQL task_list_with_tasks validation error: {e}")
            return None
        except Exception as e:
            print(f"GraphQL task_list_with_tasks error: {e}")
            raise Exception(f"Failed to retrieve task list with tasks: {str(e)}")


@strawberry.type
class TaskListMutation:
    @strawberry.mutation
    async def create_task_list(self, input: TaskListCreateInput, info: Info[GraphQLContext, None]) -> TaskListType:
        session = info.context.db_session
        service = ServiceFactory.create_task_list_service(session)

        task_list = TaskList(title=input.title, description=input.description, user_id=input.user_id)

        result = await service.create(task_list)
        return task_list_to_graphql(result)

    @strawberry.mutation
    async def update_task_list(self, id: int, input: TaskListUpdateInput, info: Info[GraphQLContext, None]) -> Optional[TaskListType]:
        session = info.context.db_session
        service = ServiceFactory.create_task_list_service(session)

        # Get existing task list first
        existing_task_list = await service.get(id)
        if not existing_task_list:
            return None

        # Only update fields that are provided (not None)
        task_list = TaskList(
            title=input.title if input.title is not None else existing_task_list.title,
            description=input.description if input.description is not None else existing_task_list.description,
            user_id=input.user_id if input.user_id is not None else existing_task_list.user_id,
        )

        try:
            result = await service.update(id, task_list)
            return task_list_to_graphql(result)
        except ValueError:
            return None

    @strawberry.mutation
    async def delete_task_list(self, id: int, info: Info[GraphQLContext, None]) -> bool:
        try:
            session = info.context.db_session
            service = ServiceFactory.create_task_list_service(session)
            return await service.delete(id)
        except TaskListHasTasksException as e:
            print(f"GraphQL deleteTaskList error: {e}")
            raise Exception("Cannot delete task list that contains tasks. Please delete all tasks first.")
        except Exception as e:
            print(f"GraphQL deleteTaskList error: {e}")
            raise Exception(f"Failed to delete task list: {str(e)}")
