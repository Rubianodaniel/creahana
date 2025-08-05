from unittest.mock import AsyncMock, Mock

import pytest

from src.application.use_cases.task_list.task_list_service import TaskListService
from src.domain.entities.task_list import TaskList


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def mock_task_repository():
    return Mock()


@pytest.fixture
def task_list_service(mock_repository, mock_task_repository):
    return TaskListService(mock_repository, mock_task_repository)


@pytest.fixture
def sample_task_list():
    return TaskList(id=1, title="Test List", user_id=123, description="Test description")


class TestTaskListService:
    @pytest.mark.asyncio
    async def test_create_task_list(self, task_list_service, mock_repository, sample_task_list):
        mock_repository.create = AsyncMock(return_value=sample_task_list)

        result = await task_list_service.create(sample_task_list)

        assert result == sample_task_list
        mock_repository.create.assert_called_once_with(sample_task_list)

    @pytest.mark.asyncio
    async def test_get_task_list(self, task_list_service, mock_repository, sample_task_list):
        mock_repository.get_by_id = AsyncMock(return_value=sample_task_list)

        result = await task_list_service.get(1)

        assert result == sample_task_list
        mock_repository.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_task_list_not_found(self, task_list_service, mock_repository):
        mock_repository.get_by_id = AsyncMock(return_value=None)

        result = await task_list_service.get(999)

        assert result is None
        mock_repository.get_by_id.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_update_task_list(self, task_list_service, mock_repository, sample_task_list):
        # Mock the get_by_id call that now happens in update
        current_task_list = TaskList(id=1, title="Current Title", description="Current description", user_id=123)
        mock_repository.get_by_id = AsyncMock(return_value=current_task_list)

        updated_task_list = TaskList(id=1, title="Updated List", user_id=123)
        mock_repository.update = AsyncMock(return_value=updated_task_list)

        result = await task_list_service.update(1, sample_task_list)

        assert result == updated_task_list
        mock_repository.get_by_id.assert_called_once_with(1)
        mock_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_task_list_not_found(self, task_list_service, mock_repository, sample_task_list):
        # Mock get_by_id to return None (task list not found)
        mock_repository.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="Task list not found"):
            await task_list_service.update(999, sample_task_list)

        mock_repository.get_by_id.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_delete_task_list(self, task_list_service, mock_repository):
        mock_repository.delete = AsyncMock(return_value=True)

        result = await task_list_service.delete(1)

        assert result is True
        mock_repository.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_list_all_task_lists(self, task_list_service, mock_repository, sample_task_list):
        task_lists = [sample_task_list]
        mock_repository.list_all = AsyncMock(return_value=task_lists)

        result = await task_list_service.list_all()

        assert result == task_lists
        mock_repository.list_all.assert_called_once()
