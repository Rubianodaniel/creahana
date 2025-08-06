import pytest
from unittest.mock import AsyncMock, MagicMock

from src.domain.entities.user import User
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def user_repository(mock_session):
    return SQLAlchemyUserRepository(mock_session)


@pytest.fixture
def sample_user():
    return User(
        id=1,
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpass",
        is_active=True
    )


@pytest.mark.asyncio
async def test_create_user_success(user_repository, mock_session, sample_user):
    """Test successful user creation."""
    # Arrange
    mock_user_model = MagicMock()
    mock_user_model.id = 1
    mock_user_model.email = "test@example.com"
    mock_user_model.username = "testuser"
    mock_user_model.hashed_password = "hashedpass"
    mock_user_model.is_active = True
    mock_user_model.created_at = None
    mock_user_model.updated_at = None

    mock_session.flush = AsyncMock()
    mock_session.refresh = AsyncMock()
    
    # Mock the user_to_model and user_to_domain functions
    with pytest.MonkeyPatch().context() as m:
        m.setattr("src.infrastructure.repositories.sqlalchemy_user_repository.user_to_model", 
                 lambda user: mock_user_model)
        m.setattr("src.infrastructure.repositories.sqlalchemy_user_repository.user_to_domain", 
                 lambda model: sample_user)
        
        # Act
        result = await user_repository.create(sample_user)
    
    # Assert
    mock_session.add.assert_called_once_with(mock_user_model)
    mock_session.flush.assert_called_once()
    mock_session.refresh.assert_called_once_with(mock_user_model)
    assert result == sample_user


@pytest.mark.asyncio
async def test_get_user_found(user_repository, mock_session, sample_user):
    """Test getting an existing user."""
    # Arrange
    mock_user_model = MagicMock()
    mock_user_model.id = 1
    mock_user_model.email = "test@example.com"
    mock_user_model.username = "testuser"
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user_model
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    with pytest.MonkeyPatch().context() as m:
        m.setattr("src.infrastructure.repositories.sqlalchemy_user_repository.user_to_domain", 
                 lambda model: sample_user)
        
        # Act
        result = await user_repository.get(1)
    
    # Assert
    assert result == sample_user
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_not_found(user_repository, mock_session):
    """Test getting a non-existent user."""
    # Arrange
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    # Act
    result = await user_repository.get(999)
    
    # Assert
    assert result is None
    mock_session.execute.assert_called_once()