import httpx
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command

from main import app  # Asegúrate de que esta importación sea correcta
from src.infrastructure.database.connection import Base, get_db_session
from src.infrastructure.config.settings import settings


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Aplica las migraciones de Alembic una vez por sesión de prueba."""
    test_db_url = settings.test_database_url
    if not test_db_url:
        raise ValueError("La variable de entorno TEST_DATABASE_URL no está configurada")

    sync_url = test_db_url.replace("postgresql+asyncpg://", "postgresql://")
    
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", sync_url)
    
    command.upgrade(alembic_cfg, "head")
    yield




@pytest.fixture(scope="session")
def event_loop(request):
    """Crea una instancia del bucle de eventos para toda la sesión de pruebas."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Crea un motor de base de datos asíncrono compartido para toda la sesión."""
    engine = create_async_engine(settings.test_database_url)
    yield engine
    await engine.dispose()


# --- Fixtures de Alcance de Función (Se ejecutan para cada test) ---

@pytest.fixture
async def db_session(test_engine):
    """
    Proporciona una sesión de base de datos aislada por transacción para cada test.
    """
    # (Este fixture está bien, no se necesita cambiar)
    connection = await test_engine.connect()
    trans = await connection.begin()
    
    TestingSessionLocal = sessionmaker(
        bind=connection, class_=AsyncSession, expire_on_commit=False
    )
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()


@pytest.fixture
async def test_client(db_session: AsyncSession):
    """
    Crea un cliente de prueba de httpx asíncrono que utiliza la sesión de BD de prueba.
    """
    def override_get_db_session():
        """Sobrescribe la dependencia para inyectar la sesión de prueba."""
        yield db_session

    # Se aplica la sobrescritura de la dependencia
    app.dependency_overrides[get_db_session] = override_get_db_session

    # Se usa httpx.AsyncClient en lugar de TestClient
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client