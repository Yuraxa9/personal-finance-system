"""
Seed script — populates the database with test data.

Usage (inside Docker):
    docker exec -it <backend_container> python seed_data.py

Usage (local, from backend/ directory):
    python seed_data.py
"""
import asyncio
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.account import Account, AccountType
from app.models.category import Category, CategoryType
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.services.auth import hash_password

# ── seed data ────────────────────────────────────────────────────────────────

SYSTEM_CATEGORIES = [
    # Expenses
    {"name": "Еда", "category_type": CategoryType.expense, "color": "#ef4444", "icon": "🍔"},
    {"name": "Транспорт", "category_type": CategoryType.expense, "color": "#f97316", "icon": "🚗"},
    {"name": "Развлечения", "category_type": CategoryType.expense, "color": "#8b5cf6", "icon": "🎬"},
    {"name": "Здоровье", "category_type": CategoryType.expense, "color": "#10b981", "icon": "💊"},
    {"name": "Одежда", "category_type": CategoryType.expense, "color": "#06b6d4", "icon": "👗"},
    # Income
    {"name": "Зарплата", "category_type": CategoryType.income, "color": "#22c55e", "icon": "💼"},
    {"name": "Фриланс", "category_type": CategoryType.income, "color": "#6366f1", "icon": "💻"},
    {"name": "Инвестиции", "category_type": CategoryType.income, "color": "#f59e0b", "icon": "📈"},
]

USERS = [
    {
        "email": "admin@finance.app",
        "password": "admin123",
        "full_name": "Администратор",
        "is_admin": True,
    },
    {
        "email": "user@finance.app",
        "password": "user123",
        "full_name": "Иван Иванов",
        "is_admin": False,
    },
]

ACCOUNTS_TEMPLATE = [
    {"name": "Основная карта", "account_type": AccountType.card, "balance": Decimal("50000.00")},
    {"name": "Наличные", "account_type": AccountType.cash, "balance": Decimal("5000.00")},
]

EXPENSE_DESCRIPTIONS = [
    "Продукты в магазине",
    "Кофе и обед",
    "Бензин",
    "Метро",
    "Кино",
    "Ресторан",
    "Аптека",
    "Новые кроссовки",
    "Подписка на сервис",
    "Такси",
]

INCOME_DESCRIPTIONS = [
    "Зарплата за месяц",
    "Аванс",
    "Фриланс-проект",
    "Дивиденды",
    "Бонус",
]


async def seed(session: AsyncSession) -> None:
    # ── system categories ────────────────────────────────────────────────────
    existing = await session.execute(select(Category).where(Category.is_default.is_(True)))
    if not existing.scalars().first():
        print("Creating system categories…")
        for cat_data in SYSTEM_CATEGORIES:
            session.add(Category(is_default=True, **cat_data))
        await session.commit()
    else:
        print("System categories already exist, skipping.")

    # load categories for transactions
    cat_result = await session.execute(select(Category).where(Category.is_default.is_(True)))
    all_cats = cat_result.scalars().all()
    expense_cats = [c for c in all_cats if c.category_type == CategoryType.expense]
    income_cats = [c for c in all_cats if c.category_type == CategoryType.income]

    # ── users ────────────────────────────────────────────────────────────────
    for user_data in USERS:
        result = await session.execute(select(User).where(User.email == user_data["email"]))
        if result.scalar_one_or_none():
            print(f"User {user_data['email']} already exists, skipping.")
            continue

        print(f"Creating user {user_data['email']}…")
        user = User(
            email=user_data["email"],
            hashed_password=hash_password(user_data["password"]),
            full_name=user_data["full_name"],
            is_admin=user_data["is_admin"],
        )
        session.add(user)
        await session.flush()  # get user.id

        # accounts
        user_accounts = []
        for acc_tmpl in ACCOUNTS_TEMPLATE:
            acc = Account(user_id=user.id, currency="RUB", **acc_tmpl)
            session.add(acc)
            user_accounts.append(acc)
        await session.flush()

        # transactions — 10 per user over last 30 days
        now = datetime.now(timezone.utc)
        for i in range(10):
            is_income = i < 3  # first 3 are income
            tx_date = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            account = random.choice(user_accounts)

            if is_income:
                amount = Decimal(str(round(random.uniform(10000, 80000), 2)))
                category = random.choice(income_cats) if income_cats else None
                description = random.choice(INCOME_DESCRIPTIONS)
                tx_type = TransactionType.income
                account.balance += amount
            else:
                amount = Decimal(str(round(random.uniform(200, 5000), 2)))
                category = random.choice(expense_cats) if expense_cats else None
                description = random.choice(EXPENSE_DESCRIPTIONS)
                tx_type = TransactionType.expense
                account.balance -= amount

            session.add(
                Transaction(
                    user_id=user.id,
                    account_id=account.id,
                    category_id=category.id if category else None,
                    amount=amount,
                    transaction_type=tx_type,
                    description=description,
                    date=tx_date,
                )
            )

        await session.commit()
        print(f"  ✓ accounts and 10 transactions created for {user_data['email']}")

    print("\nSeed complete.")
    print("Credentials:")
    for u in USERS:
        print(f"  {u['email']} / {u['password']}")


async def main() -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        await seed(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
