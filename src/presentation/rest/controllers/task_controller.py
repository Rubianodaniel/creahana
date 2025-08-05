from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.task.task_service import TaskService
from src.domain.entities.task import Task
from src.infrastructure.database.connection import get_db_session
from src.presentation.rest.dtos.task_schemas import (
    TaskCreateSchema,
    TaskResponseSchema,
    TaskUpdateSchema,
)
from src.presentation.rest.dtos.task_status_schemas import TaskStatusUpdateSchema
from src.presentation.shared.dependencies.service_factory import ServiceFactory

router = APIRouter(prefix="/tasks", tags=["tasks"])


async def get_task_service(
    session: AsyncSession = Depends(get_db_session),
) -> TaskService:
    return ServiceFactory.create_task_service(session=session)


@router.post("/", response_model=TaskResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreateSchema,
    service: TaskService = Depends(get_task_service),
):
    task = Task(
        title=task_data.title,
        description=task_data.description,
        task_list_id=task_data.task_list_id,
        status=task_data.status,
        priority=task_data.priority,
        assigned_user_id=task_data.assigned_user_id,
        due_date=task_data.due_date,
    )
    result = await service.create(task)
    return TaskResponseSchema.model_validate(result)


@router.get("/{task_id}", response_model=TaskResponseSchema)
async def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
):
    result = await service.get(task_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskResponseSchema.model_validate(result)


@router.get("/", response_model=List[TaskResponseSchema])
async def list_tasks(
    service: TaskService = Depends(get_task_service),
):
    results = await service.list_all()
    return [TaskResponseSchema.model_validate(result) for result in results]


@router.put("/{task_id}", response_model=TaskResponseSchema)
async def update_task(
    task_id: int,
    task_data: TaskUpdateSchema,
    service: TaskService = Depends(get_task_service),
):
    task = Task(
        title=task_data.title,
        description=task_data.description,
        task_list_id=task_data.task_list_id,
        status=task_data.status,
        priority=task_data.priority,
        assigned_user_id=task_data.assigned_user_id,
        due_date=task_data.due_date,
    )
    try:
        result = await service.update(task_id, task)
        return TaskResponseSchema.model_validate(result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
):
    success = await service.delete(task_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@router.patch("/{task_id}/status", response_model=TaskResponseSchema)
async def change_task_status(
    task_id: int,
    status_data: TaskStatusUpdateSchema,
    service: TaskService = Depends(get_task_service),
):
    try:
        result = await service.change_status(task_id, status_data.status)
        return TaskResponseSchema.model_validate(result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
