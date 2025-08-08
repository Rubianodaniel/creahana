

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext

from src.domain.entities.user import User
from src.infrastructure.database.connection import get_db_session
from src.presentation.rest.middleware.auth_middleware import get_current_user


class GraphQLContext(BaseContext):
    """Custom GraphQL context that provides database session and user."""

    def __init__(self, db_session: AsyncSession, current_user: User):
        self.db_session = db_session
        self.current_user = current_user


async def get_db_session_dependency():
    """Dependency that properly handles async session lifecycle."""
    async for session in get_db_session():
        yield session


async def get_graphql_context(
    db_session: AsyncSession = Depends(get_db_session_dependency),
    current_user: User = Depends(get_current_user),
) -> GraphQLContext:
    """Context getter for GraphQL that injects database session and user using FastAPI dependency."""
    return GraphQLContext(db_session=db_session, current_user=current_user)
