from typing import Optional

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create(self, user: User) -> User:
        return await self.user_repository.create(user)

    async def get(self, user_id: int) -> Optional[User]:
        if user_id <= 0:
            raise ValueError("User ID must be positive")
        return await self.user_repository.get(user_id)
