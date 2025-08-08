from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.exceptions.user_exceptions import DuplicateEmailException, DuplicateUsernameException
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.mappers import user_to_domain, user_to_model
from src.infrastructure.database.models.user_model import UserModel


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        try:
            user_model = user_to_model(user)
            self.session.add(user_model)
            await self.session.flush()
            await self.session.refresh(user_model)
            return user_to_domain(user_model)
        except IntegrityError as e:
            # No hacer rollback aquí - solo lanzar la excepción apropiada
            error_msg = str(e).lower()
            if "email" in error_msg and ("unique" in error_msg or "duplicate" in error_msg):
                raise DuplicateEmailException(user.email)
            elif "username" in error_msg and ("unique" in error_msg or "duplicate" in error_msg):
                raise DuplicateUsernameException(user.username)
            # Re-raise other integrity errors
            raise e

    async def get(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
        user_model = result.scalar_one_or_none()
        return user_to_domain(user_model) if user_model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        user_model = result.scalar_one_or_none()
        return user_to_domain(user_model) if user_model else None