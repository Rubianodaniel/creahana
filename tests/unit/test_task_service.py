import pytest
from unittest.mock import AsyncMock, Mock
from src.domain.entities.task import Task, TaskStatus, TaskPriority
from src.application.use_cases.task.task_service import TaskService
from src.application.dtos.task_dto import TaskFiltersDTO


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def task_service(mock_repository):
    return TaskService(mock_repository)


@pytest.fixture
def sample_task():
    return Task(
        id=1,
        title="Test Task",
        task_list_id=123,
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
    )


class TestTaskService:
    @pytest.mark.asyncio
    async def test_create_task(self, task_service, mock_repository, sample_task):
        mock_repository.create = AsyncMock(return_value=sample_task)

        result = await task_service.create(sample_task)

        assert result == sample_task
        mock_repository.create.assert_called_once_with(sample_task)

    @pytest.mark.asyncio
    async def test_get_task(self, task_service, mock_repository, sample_task):
        mock_repository.get_by_id = AsyncMock(return_value=sample_task)

        result = await task_service.get(1)

        assert result == sample_task
        mock_repository.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_change_status_success(
        self, task_service, mock_repository, sample_task
    ):
        updated_task = Task(
            id=1,
            title="Test Task",
            task_list_id=123,
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.MEDIUM,
        )
        mock_repository.get_by_id = AsyncMock(return_value=sample_task)
        mock_repository.update = AsyncMock(return_value=updated_task)

        result = await task_service.change_status(1, TaskStatus.COMPLETED)

        assert result == updated_task
        assert sample_task.status == TaskStatus.COMPLETED
        mock_repository.get_by_id.assert_called_once_with(1)
        mock_repository.update.assert_called_once_with(sample_task)

    @pytest.mark.asyncio
    async def test_change_status_task_not_found(self, task_service, mock_repository):
        mock_repository.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="Task with id 999 not found"):
            await task_service.change_status(999, TaskStatus.COMPLETED)

    @pytest.mark.asyncio
    async def test_get_by_filters(self, task_service, mock_repository, sample_task):
        filters = TaskFiltersDTO(task_list_id=123, status=TaskStatus.PENDING)
        tasks = [sample_task]
        mock_repository.get_tasks_by_filters = AsyncMock(return_value=tasks)

        result = await task_service.get_by_filters(filters)

        assert result == tasks
        mock_repository.get_tasks_by_filters.assert_called_once_with(
            123, TaskStatus.PENDING, None
        )

    @pytest.mark.asyncio
    async def test_calculate_completion_percentage_with_tasks(
        self, task_service, mock_repository
    ):
        tasks = [
            Task(id=1, title="Task 1", task_list_id=123, status=TaskStatus.COMPLETED),
            Task(id=2, title="Task 2", task_list_id=123, status=TaskStatus.PENDING),
            Task(id=3, title="Task 3", task_list_id=123, status=TaskStatus.COMPLETED),
            Task(id=4, title="Task 4", task_list_id=123, status=TaskStatus.IN_PROGRESS),
        ]
        mock_repository.get_by_task_list_id = AsyncMock(return_value=tasks)

        result = await task_service.calculate_completion_percentage(123)

        assert result == 50.0
        mock_repository.get_by_task_list_id.assert_called_once_with(123)

    @pytest.mark.asyncio
    async def test_calculate_completion_percentage_no_tasks(
        self, task_service, mock_repository
    ):
        mock_repository.get_by_task_list_id = AsyncMock(return_value=[])

        result = await task_service.calculate_completion_percentage(123)

        assert result == 0.0
        mock_repository.get_by_task_list_id.assert_called_once_with(123)
