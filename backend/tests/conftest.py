import pytest
import pytest_asyncio
from decimal import Decimal

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.dependencies import get_db
from app.main import app
from app.models.account import Account, AccountType
from app.models.category import Category, CategoryType
from app.models.user import User
from app.services.auth import create_access_token, hash_password

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine():
    _engine = create_async_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    await _engine.dispose()


@pytest_asyncio.fixture
async def db(engine):
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(engine):
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db):
    user = User(
        email="test@example.com",
        hashed_password=hash_password("testpassword"),
        full_name="Test User",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user):
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_account(db, test_user):
    account = Account(
        user_id=test_user.id,
        name="Test Account",
        account_type=AccountType.card,
        balance=Decimal("1000.00"),
        currency="RUB",
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


@pytest_asyncio.fixture
async def test_category(db, test_user):
    category = Category(
        user_id=test_user.id,
        name="Test Category",
        category_type=CategoryType.expense,
        color="#FF0000",
        icon="shopping",
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category
