import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import IntegrityError
from src.domain.entities.task import Task, TaskStatus, TaskPriority
from src.domain.exceptions.task_exceptions import InvalidTaskListException
from src.infrastructure.repositories.sqlalchemy_task_repository import (
    SQLAlchemyTaskRepository,
)
from src.infrastructure.database.models.task_model import TaskModel


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repository(mock_session):
    return SQLAlchemyTaskRepository(mock_session)


@pytest.fixture
def sample_task():
    return Task(
        id=1,
        title="Test Task",
        task_list_id=123,
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
    )


@pytest.fixture
def sample_task_model():
    return TaskModel(
        id=1,
        title="Test Task",
        task_list_id=123,
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
    )


class TestSQLAlchemyTaskRepository:
    @pytest.mark.asyncio
    async def test_create_task(
        self, repository, mock_session, sample_task, sample_task_model
    ):
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.add = MagicMock()

        result = await repository.create(sample_task)

        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()
        assert result.title == sample_task.title
        assert result.task_list_id == sample_task.task_list_id

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, mock_session, sample_task_model):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_task_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repository.get_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.title == "Test Task"
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
    async def test_update_task_success(
        self, repository, mock_session, sample_task, sample_task_model
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_task_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        result = await repository.update(sample_task)

        assert result.title == sample_task.title
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_task_not_found(self, repository, mock_session, sample_task):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="Task with id 1 not found"):
            await repository.update(sample_task)

    @pytest.mark.asyncio
    async def test_delete_task_success(
        self, repository, mock_session, sample_task_model
    ):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_task_model
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock()

        result = await repository.delete(1)

        assert result is True
        mock_session.delete.assert_called_once_with(sample_task_model)
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, repository, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repository.delete(999)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_by_task_list_id(
        self, repository, mock_session, sample_task_model
    ):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_task_model]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repository.get_by_task_list_id(123)

        assert len(result) == 1
        assert result[0].title == "Test Task"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_tasks_by_filters_with_all_filters(
        self, repository, mock_session, sample_task_model
    ):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_task_model]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repository.get_tasks_by_filters(
            task_list_id=123, status=TaskStatus.PENDING, priority=TaskPriority.MEDIUM
        )

        assert len(result) == 1
        assert result[0].title == "Test Task"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_tasks_by_filters_no_filters(
        self, repository, mock_session, sample_task_model
    ):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_task_model]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repository.get_tasks_by_filters()

        assert len(result) == 1
        assert result[0].title == "Test Task"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_tasks_by_filters_only_status(
        self, repository, mock_session, sample_task_model
    ):
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_task_model]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await repository.get_tasks_by_filters(status=TaskStatus.PENDING)

        assert len(result) == 1
        assert result[0].title == "Test Task"

    @pytest.mark.asyncio
    async def test_create_task_with_invalid_task_list_id(
        self, repository, mock_session, sample_task
    ):
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock(
            side_effect=IntegrityError("", "", "foreign key constraint fails task_lists")
        )
        mock_session.rollback = AsyncMock()

        with pytest.raises(InvalidTaskListException) as exc_info:
            await repository.create(sample_task)

        assert exc_info.value.task_list_id == sample_task.task_list_id
        mock_session.rollback.assert_called_once()