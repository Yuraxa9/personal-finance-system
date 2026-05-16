"""
Fuzz testing with Hypothesis.

These tests are intentionally synchronous — Hypothesis generates test cases
and drives them through a dedicated event loop that is separate from the one
pytest-asyncio manages for the regular async test suite.

Each test asserts only that the server never responds with HTTP 500.
"""
import asyncio
from decimal import Decimal

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.dependencies import get_db
from app.main import app
from app.models.account import Account, AccountType
from app.models.user import User
from app.services.auth import create_access_token, hash_password

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# ── shared infrastructure (lazy-initialised on first test run) ────────────────
_loop = asyncio.new_event_loop()
_factory = None
_auth_headers: dict = {}
_account_id: str = ""
_initialized = False


async def _boot() -> None:
    global _factory, _auth_headers, _account_id

    engine = create_async_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    _factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with _factory() as session:
        user = User(
            email="fuzz@example.com",
            hashed_password=hash_password("fuzz_password"),
            full_name="Fuzz User",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        account = Account(
            user_id=user.id,
            name="Fuzz Account",
            account_type=AccountType.card,
            balance=Decimal("999999.00"),
            currency="RUB",
        )
        session.add(account)
        await session.commit()
        await session.refresh(account)

        _auth_headers = {
            "Authorization": f"Bearer {create_access_token({'sub': str(user.id)})}"
        }
        _account_id = str(account.id)


async def _override_get_db():
    async with _factory() as session:
        yield session


def _ensure_init() -> None:
    global _initialized
    if not _initialized:
        _loop.run_until_complete(_boot())
        _initialized = True


def _fuzz(coro):
    """Run *coro* on the shared fuzz event loop with the DB override active."""
    _ensure_init()
    app.dependency_overrides[get_db] = _override_get_db
    return _loop.run_until_complete(coro)


# ── tests ─────────────────────────────────────────────────────────────────────

@given(email=st.text(min_size=0, max_size=200))
@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_register_email(email):
    async def _run():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post(
                "/api/v1/auth/register",
                json={"email": email, "password": "secret123", "full_name": "Fuzz"},
            )
            assert r.status_code != 500

    _fuzz(_run())


@given(password=st.text(min_size=0, max_size=500))
@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_register_password(password):
    async def _run():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post(
                "/api/v1/auth/register",
                json={
                    "email": "fuzz_pw@example.com",
                    "password": password,
                    "full_name": "Fuzz",
                },
            )
            assert r.status_code != 500

    _fuzz(_run())


@given(
    amount=st.one_of(
        st.floats(allow_nan=True, allow_infinity=True),
        st.integers(min_value=-(10**15), max_value=10**15),
        st.text(min_size=1, max_size=20),
    )
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_amount(amount):
    async def _run():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            try:
                r = await c.post(
                    "/api/v1/transactions/",
                    json={
                        "account_id": _account_id,
                        "amount": amount,
                        "transaction_type": "income",
                        "date": "2024-01-15T12:00:00",
                    },
                    headers=_auth_headers,
                )
                assert r.status_code != 500
            except (ValueError, OverflowError):
                # NaN / ±Inf cannot be represented in standard JSON —
                # the error is client-side, not a server bug.
                pass

    _fuzz(_run())


@given(date=st.text(min_size=0, max_size=100))
@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_date(date):
    async def _run():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post(
                "/api/v1/transactions/",
                json={
                    "account_id": _account_id,
                    "amount": "1.00",
                    "transaction_type": "income",
                    "date": date,
                },
                headers=_auth_headers,
            )
            assert r.status_code != 500

    _fuzz(_run())


@given(description=st.text(min_size=0, max_size=10000))
@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_description(description):
    async def _run():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post(
                "/api/v1/transactions/",
                json={
                    "account_id": _account_id,
                    "amount": "1.00",
                    "transaction_type": "income",
                    "date": "2024-01-15T12:00:00",
                    "description": description,
                },
                headers=_auth_headers,
            )
            assert r.status_code != 500

    _fuzz(_run())


@given(name=st.text(min_size=0, max_size=1000))
@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
def test_fuzz_account_name(name):
    async def _run():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post(
                "/api/v1/accounts/",
                json={
                    "name": name,
                    "account_type": "cash",
                    "balance": "0.00",
                    "currency": "RUB",
                },
                headers=_auth_headers,
            )
            assert r.status_code != 500

    _fuzz(_run())
