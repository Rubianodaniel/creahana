from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext

from src.infrastructure.database.connection import get_db_session


class GraphQLContext(BaseContext):
    """Custom GraphQL context that provides database session."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session


async def get_db_session_dependency():
    """Dependency that properly handles async session lifecycle."""
    async for session in get_db_session():
        yield session


async def get_graphql_context(
    db_session: AsyncSession = Depends(get_db_session_dependency),
) -> GraphQLContext:
    """Context getter for GraphQL that injects database session using FastAPI dependency."""
    return GraphQLContext(db_session=db_session)
