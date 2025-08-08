from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.task.task_service import TaskService
from src.application.use_cases.task_list.task_list_service import TaskListService
from src.domain.entities.task import TaskPriority, TaskStatus
from src.domain.entities.task_list import TaskList
from src.domain.entities.user import User
from src.infrastructure.database.connection import get_db_session
from src.presentation.rest.middleware.auth_middleware import get_current_user
from src.presentation.rest.dtos.task_list_schemas import (
    TaskListCreateSchema,
    TaskListResponseSchema,
    TaskListUpdateSchema,
    TaskListWithTasksResponseSchema,
)
from src.presentation.rest.dtos.task_schemas import TaskResponseSchema
from src.presentation.shared.dependencies.service_factory import ServiceFactory

router = APIRouter(prefix="/task-lists", tags=["task-lists"])


async def get_task_list_service(
    session: AsyncSession = Depends(get_db_session),
) -> TaskListService:
    return ServiceFactory.create_task_list_service(session)


async def get_task_service(
    session: AsyncSession = Depends(get_db_session),
) -> TaskService:
    return ServiceFactory.create_task_service(session)


@router.post("/", response_model=TaskListResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_task_list(
    task_list_data: TaskListCreateSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    service: TaskListService = Depends(get_task_list_service),
):
    task_list = TaskList(
        title=task_list_data.title,
        description=task_list_data.description,
        user_id=task_list_data.user_id,
    )
    result = await service.create(task_list)
    return TaskListResponseSchema.model_validate(result)


@router.get("/{task_list_id}", response_model=TaskListResponseSchema)
async def get_task_list(
    task_list_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    service: TaskListService = Depends(get_task_list_service),
):
    result = await service.get(task_list_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task list not found")
    return TaskListResponseSchema.model_validate(result)


@router.get("/", response_model=List[TaskListResponseSchema])
async def list_task_lists(
    current_user: Annotated[User, Depends(get_current_user)],
    service: TaskListService = Depends(get_task_list_service),
):
    results = await service.list_all()
    return [TaskListResponseSchema.model_validate(result) for result in results]


@router.put("/{task_list_id}", response_model=TaskListResponseSchema)
async def update_task_list(
    task_list_id: int,
    task_list_data: TaskListUpdateSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    service: TaskListService = Depends(get_task_list_service),
):
    task_list = TaskList(
        title=task_list_data.title,
        description=task_list_data.description,
        user_id=task_list_data.user_id,
    )
    try:
        result = await service.update(task_list_id, task_list)
        return TaskListResponseSchema.model_validate(result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{task_list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_list(
    task_list_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    service: TaskListService = Depends(get_task_list_service),
):
    success = await service.delete(task_list_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task list not found")


@router.get("/{task_list_id}/tasks", response_model=TaskListWithTasksResponseSchema)
async def get_task_list_with_tasks(
    task_list_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    service: TaskListService = Depends(get_task_list_service),
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by task priority"),
):
    """Get a task list with its tasks, filtered by status and/or priority, including completion percentage."""
    try:
        result = await service.get_tasks_with_completion(task_list_id, status, priority)

        # Create response combining task_list data with additional fields
        task_list_data = TaskListResponseSchema.model_validate(result.task_list).model_dump()

        return TaskListWithTasksResponseSchema(
            **task_list_data,
            tasks=[TaskResponseSchema.model_validate(task) for task in result.tasks],
            completion_percentage=result.completion_percentage,
            total_tasks=result.total_tasks,
            completed_tasks=result.completed_tasks,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
