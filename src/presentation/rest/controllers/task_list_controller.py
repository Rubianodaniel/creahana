from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.task_list import TaskList
from src.application.use_cases.task_list.task_list_service import TaskListService
from src.infrastructure.database.connection import get_db_session
from src.presentation.shared.dependencies.service_factory import ServiceFactory
from src.presentation.rest.schemas.task_list_schemas import (
    TaskListCreateSchema,
    TaskListUpdateSchema,
    TaskListResponseSchema,
)

router = APIRouter(prefix="/task-lists", tags=["task-lists"])


async def get_task_list_service(
    session: AsyncSession = Depends(get_db_session),
) -> TaskListService:
    return ServiceFactory.create_task_list_service(session)


@router.post("/", response_model=TaskListResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_task_list(
    task_list_data: TaskListCreateSchema,
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
    service: TaskListService = Depends(get_task_list_service),
):
    result = await service.get(task_list_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task list not found"
        )
    return TaskListResponseSchema.model_validate(result)


@router.get("/", response_model=List[TaskListResponseSchema])
async def list_task_lists(
    service: TaskListService = Depends(get_task_list_service),
):
    results = await service.list_all()
    return [TaskListResponseSchema.model_validate(result) for result in results]


@router.put("/{task_list_id}", response_model=TaskListResponseSchema)
async def update_task_list(
    task_list_id: int,
    task_list_data: TaskListUpdateSchema,
    service: TaskListService = Depends(get_task_list_service),
):
    task_list = TaskList(
        id=task_list_id,
        title=task_list_data.title,
        description=task_list_data.description,
        user_id=1,
    )
    try:
        result = await service.update(task_list_id, task_list)
        return TaskListResponseSchema.model_validate(result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{task_list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_list(
    task_list_id: int,
    service: TaskListService = Depends(get_task_list_service),
):
    success = await service.delete(task_list_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task list not found"
        )