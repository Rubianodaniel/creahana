from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.auth.auth_service import AuthService
from src.domain.entities.user import User
from src.infrastructure.database.connection import get_db_session
from src.presentation.shared.dependencies.service_factory import ServiceFactory

# OAuth2 scheme for token authentication
security = HTTPBearer()


async def get_auth_service(session: AsyncSession = Depends(get_db_session)) -> AuthService:
    """Dependency to get AuthService instance."""
    return ServiceFactory.create_auth_service(session=session)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Get current authenticated user from JWT token.
    Use this dependency for protected endpoints.
    Raises 401 if no token or invalid token.
    """
    token = credentials.credentials
    user = await auth_service.verify_token(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )
    
    return user