import asyncio

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from alembic import command
from alembic.config import Config
from main import app
from src.infrastructure.config.settings import settings
from src.infrastructure.database.connection import Base, get_db_session


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Aplica las migraciones de Alembic una vez por sesión de prueba."""
    test_db_url = settings.test_database_url
    if not test_db_url:
        raise ValueError("La variable de entorno TEST_DATABASE_URL no está configurada")

    # Configurar Alembic para usar la base de datos de test (convertir a sync para migraciones)
    sync_test_db_url = test_db_url.replace("postgresql+asyncpg://", "postgresql://")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", sync_test_db_url)
    
    # Aplicar migraciones
    print(f"Aplicando migraciones a: {test_db_url}")
    command.upgrade(alembic_cfg, "head")
    print("Migraciones aplicadas exitosamente")
    
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
    Usa transacciones anidadas para permitir múltiples operaciones por test.
    """
    connection = await test_engine.connect()
    trans = await connection.begin()

    TestingSessionLocal = sessionmaker(
        bind=connection, 
        class_=AsyncSession, 
        expire_on_commit=False,
        autoflush=False,
        autocommit=False
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


    app.dependency_overrides[get_db_session] = override_get_db_session


    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def e2e_client(test_engine):

    SessionLocal = sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    async def get_e2e_session():
        """Dependency override que crea sesiones reales por request."""
        async with SessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


    app.dependency_overrides[get_db_session] = get_e2e_session

    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client
        
        async with SessionLocal() as cleanup_session:
            from sqlalchemy import text
            result = await cleanup_session.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename != 'alembic_version'
            """))
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                # Disable foreign key constraints
                await cleanup_session.execute(text("SET session_replication_role = 'replica'"))

                # Truncate all tables
                tables_str = ', '.join(tables)
                await cleanup_session.execute(text(f"TRUNCATE TABLE {tables_str} RESTART IDENTITY"))

                # Re-enable foreign key constraints
                await cleanup_session.execute(text("SET session_replication_role = 'origin'"))
                
                await cleanup_session.commit()
