import pytest
from unittest.mock import AsyncMock

from src.application.use_cases.user.user_service import UserService
from src.domain.entities.user import User


@pytest.fixture
def mock_user_repository():
    return AsyncMock()


@pytest.fixture
def user_service(mock_user_repository):
    return UserService(mock_user_repository)


@pytest.fixture
def sample_user():
    return User(
        id=1,
        email="test@example.com",
        username="testuser",
        is_active=True
    )


@pytest.mark.asyncio
async def test_create_user_success(user_service, mock_user_repository, sample_user):
    """Test successful user creation."""
    # Arrange
    mock_user_repository.create.return_value = sample_user
    
    # Act
    result = await user_service.create(sample_user)
    
    # Assert
    mock_user_repository.create.assert_called_once_with(sample_user)
    assert result == sample_user


@pytest.mark.asyncio
async def test_get_user_success(user_service, mock_user_repository, sample_user):
    """Test successful user retrieval."""
    # Arrange
    mock_user_repository.get.return_value = sample_user
    
    # Act
    result = await user_service.get(1)
    
    # Assert
    mock_user_repository.get.assert_called_once_with(1)
    assert result == sample_user


@pytest.mark.asyncio
async def test_get_user_not_found(user_service, mock_user_repository):
    """Test getting a non-existent user."""
    # Arrange
    mock_user_repository.get.return_value = None
    
    # Act
    result = await user_service.get(999)
    
    # Assert
    mock_user_repository.get.assert_called_once_with(999)
    assert result is None


@pytest.mark.asyncio
async def test_get_user_invalid_id(user_service, mock_user_repository):
    """Test getting user with invalid ID."""
    # Act & Assert
    with pytest.raises(ValueError, match="User ID must be positive"):
        await user_service.get(0)
    
    with pytest.raises(ValueError, match="User ID must be positive"):
        await user_service.get(-1)
    
    # Repository should not be called
    mock_user_repository.get.assert_not_called()