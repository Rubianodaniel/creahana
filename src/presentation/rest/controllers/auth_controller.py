from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.auth.auth_service import AuthService
from src.domain.entities.user import User
from src.domain.exceptions.user_exceptions import DuplicateEmailException, DuplicateUsernameException
from src.infrastructure.config.settings import settings
from src.infrastructure.database.connection import get_db_session
from src.presentation.rest.dtos.auth_schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from src.presentation.rest.middleware.auth_middleware import get_current_user
from src.presentation.shared.dependencies.service_factory import ServiceFactory

router = APIRouter(prefix="/auth", tags=["authentication"])


async def get_auth_service(session: AsyncSession = Depends(get_db_session)) -> AuthService:
    return ServiceFactory.create_auth_service(session=session)


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    """Authenticate user and return JWT token."""
    user = await auth_service.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth_service.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(register_data: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)):
    """Register a new user."""
    try:
        user = await auth_service.register_user(email=register_data.email, username=register_data.username, password=register_data.password)
        return UserResponse(id=user.id, email=user.email, username=user.username, is_active=user.is_active)
    except DuplicateEmailException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DuplicateUsernameException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_user_profile(current_user: Annotated[User, Depends(get_current_user)]):
    """Get current user info from JWT token."""
    return UserResponse(id=current_user.id, email=current_user.email, username=current_user.username, is_active=current_user.is_active)
