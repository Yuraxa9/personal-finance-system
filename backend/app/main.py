from decimal import Decimal

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_current_user, get_db
from app.models.account import Account
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.routers.accounts import router as accounts_router
from app.routers.auth import router as auth_router
from app.routers.categories import router as categories_router
from app.routers.transactions import router as transactions_router

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(accounts_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(transactions_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/api/v1/stats")
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uid = current_user.id

    total_accounts = await db.scalar(
        select(func.count(Account.id)).where(Account.user_id == uid)
    )
    total_transactions = await db.scalar(
        select(func.count(Transaction.id)).where(Transaction.user_id == uid)
    )

    income_row = await db.scalar(
        select(func.sum(Transaction.amount)).where(
            and_(Transaction.user_id == uid, Transaction.transaction_type == TransactionType.income)
        )
    )
    expense_row = await db.scalar(
        select(func.sum(Transaction.amount)).where(
            and_(Transaction.user_id == uid, Transaction.transaction_type == TransactionType.expense)
        )
    )

    total_income = income_row or Decimal("0.00")
    total_expense = expense_row or Decimal("0.00")

    return {
        "total_accounts": total_accounts or 0,
        "total_transactions": total_transactions or 0,
        "total_income": str(total_income),
        "total_expense": str(total_expense),
        "net_balance": str(total_income - total_expense),
    }
