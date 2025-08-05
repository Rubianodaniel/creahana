from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from src.domain.entities.task_list import TaskList
from src.domain.exceptions.task_list_exceptions import TaskListHasTasksException
from src.infrastructure.database.models.task_list_model import TaskListModel
from src.infrastructure.repositories.sqlalchemy_task_list_repository import (
    SQLAlchemyTaskListRepository,
)


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repository(mock_session):
    return SQLAlchemyTaskListRepository(mock_session)


@pytest.fixture
def sample_task_list():
    return TaskList(id=1, title="Test List", user_id=123, description="Test description")


@pytest.fixture
def sample_task_list_model():
    return TaskListModel(id=1, title="Test List", user_id=123, description="Test description")


class TestSQLAlchemyTaskListRepository:
    @pytest.mark.asyncio
    async def test_create_task_list(self, repository, mock_session, sample_task_list, sample_task_list_model):
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.add = MagicMock()

        result = await repository.create(sample_task_list)

        mock_session.add.assert_called_once()
        mock_session.refresh.assert_called_once()
        assert result.title == sample_task_list.title
        assert result.user_id == sample_task_list.user_id

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, mock_session, sample_task_list_model):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_task_list_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repository.get_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.title == "Test List"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repository.get_by_id(999)

        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_task_list_success(self, repository, mock_session, sample_task_list, sample_task_list_model):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_task_list_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        result = await repository.update(sample_task_list)

        assert result.title == sample_task_list.title
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_task_list_not_found(self, repository, mock_session, sample_task_list):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="TaskList with id 1 not found"):
            await repository.update(sample_task_list)

    @pytest.mark.asyncio
    async def test_delete_task_list_success(self, repository, mock_session, sample_task_list_model):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_task_list_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock()

        result = await repository.delete(1)

        assert result is True
        mock_session.delete.assert_called_once_with(sample_task_list_model)
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_task_list_not_found(self, repository, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repository.delete(999)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_task_list_with_foreign_key_constraint(self, repository, mock_session, sample_task_list_model):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_task_list_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock(side_effect=IntegrityError("", "", "foreign key constraint fails"))
        mock_session.rollback = AsyncMock()

        with pytest.raises(TaskListHasTasksException) as exc_info:
            await repository.delete(1)

        assert exc_info.value.task_list_id == 1
        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_all_task_lists(self, repository, mock_session, sample_task_list_model):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_task_list_model]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repository.list_all()

        assert len(result) == 1
        assert result[0].title == "Test List"
        mock_session.execute.assert_called_once()
