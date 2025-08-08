from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.user.user_service import UserService
from src.domain.entities.user import User
from src.domain.exceptions.user_exceptions import DuplicateEmailException, DuplicateUsernameException
from src.infrastructure.database.connection import get_db_session
from src.presentation.rest.middleware.auth_middleware import get_current_user
from src.presentation.rest.dtos.user_schemas import UserCreateSchema, UserResponseSchema
from src.presentation.shared.dependencies.service_factory import ServiceFactory

router = APIRouter(prefix="/users", tags=["users"])


async def get_user_service(
    session: AsyncSession = Depends(get_db_session),
) -> UserService:
    return ServiceFactory.create_user_service(session)


@router.post("/", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateSchema,
    service: UserService = Depends(get_user_service),
):
    try:
        user = User(
            email=user_data.email,
            username=user_data.username,
        )
        result = await service.create(user)
        return UserResponseSchema.model_validate(result)
    except DuplicateEmailException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Email already exists: {e.email}")
    except DuplicateUsernameException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Username already exists: {e.username}")


@router.get("/{user_id}", response_model=UserResponseSchema)
async def get_user(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    service: UserService = Depends(get_user_service),
):
    result = await service.get(user_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponseSchema.model_validate(result)
