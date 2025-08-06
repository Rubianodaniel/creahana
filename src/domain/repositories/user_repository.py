from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def get(self, user_id: int) -> Optional[User]:
        pass