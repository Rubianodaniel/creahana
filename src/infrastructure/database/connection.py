from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    database_url: str

    class Config:
        env_file = ".env"


Base = declarative_base()


def get_settings():
    return DatabaseSettings()


def create_engine():
    settings = get_settings()
    return create_async_engine(settings.database_url, echo=True)


def get_session_factory():
    engine = create_engine()
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncSession:
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()