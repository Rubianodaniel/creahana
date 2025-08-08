from typing import List, Optional

from src.application.dtos.task_list_with_tasks_dto import TaskListWithTasksDTO
from src.domain.entities.task import TaskPriority, TaskStatus
from src.domain.entities.task_list import TaskList
from src.domain.exceptions.task_list_exceptions import InvalidUserException
from src.domain.inputs.task_list_use_cases import TaskListUseCases
from src.domain.outputs.task_list_repository import TaskListRepository
from src.domain.outputs.task_repository import TaskRepository
from src.domain.repositories.user_repository import UserRepository


class TaskListService(TaskListUseCases):
    def __init__(self, repository: TaskListRepository, task_repository: TaskRepository, user_repository: UserRepository):
        self.repository = repository
        self.task_repository = task_repository
        self.user_repository = user_repository

    async def create(self, task_list: TaskList) -> TaskList:
        # Validate user exists only if user_id is provided and not None
        if task_list.user_id is not None:
            user = await self.user_repository.get(task_list.user_id)
            if not user:
                raise InvalidUserException(task_list.user_id)
        
        return await self.repository.create(task_list)

    async def get(self, task_list_id: int) -> Optional[TaskList]:
        return await self.repository.get_by_id(task_list_id)

    async def update(self, task_list_id: int, task_list: TaskList) -> TaskList:
        # Get current task list to preserve unmodified fields
        current_task_list = await self.repository.get_by_id(task_list_id)
        if not current_task_list:
            raise ValueError("Task list not found")

        # Validate user exists if user_id is being updated and is not None
        final_user_id = task_list.user_id if task_list.user_id is not None else current_task_list.user_id
        if final_user_id is not None:
            user = await self.user_repository.get(final_user_id)
            if not user:
                raise InvalidUserException(final_user_id)

        # Update only the fields that are provided (not None)
        updated_task_list = TaskList(
            id=task_list_id,
            title=task_list.title if task_list.title is not None else current_task_list.title,
            description=task_list.description if task_list.description is not None else current_task_list.description,
            user_id=final_user_id,
            is_active=current_task_list.is_active,
            created_at=current_task_list.created_at,
            updated_at=current_task_list.updated_at,
        )

        return await self.repository.update(updated_task_list)

    async def delete(self, task_list_id: int) -> bool:
        return await self.repository.delete(task_list_id)

    async def list_all(self) -> List[TaskList]:
        return await self.repository.list_all()

    async def get_tasks_with_completion(
        self,
        task_list_id: int,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
    ) -> TaskListWithTasksDTO:
        """Get tasks for a task list with filters and completion percentage."""
        # Verify task list exists
        task_list = await self.repository.get_by_id(task_list_id)
        if not task_list:
            raise ValueError("Task list not found")

        # Get filtered tasks
        filtered_tasks = await self.task_repository.get_tasks_by_filters(task_list_id, status, priority)

        # If no filters applied, use filtered_tasks for completion calculation
        if status is None and priority is None:
            all_tasks = filtered_tasks
        else:
            # Only get all tasks if filters were applied
            all_tasks = await self.task_repository.get_by_task_list_id(task_list_id)

        # Calculate completion percentage
        if all_tasks:
            completed_tasks_count = len([task for task in all_tasks if task.status == TaskStatus.COMPLETED])
            completion_percentage = (completed_tasks_count / len(all_tasks)) * 100
        else:
            completed_tasks_count = 0
            completion_percentage = 0.0

        return TaskListWithTasksDTO(
            task_list=task_list,
            tasks=filtered_tasks,
            completion_percentage=round(completion_percentage, 2),
            total_tasks=len(all_tasks),
            completed_tasks=completed_tasks_count,
        )
