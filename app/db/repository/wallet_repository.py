from decimal import Decimal

from typing import (
    List, 
    Optional,
)

from sqlalchemy import (
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.wallets import Wallet
from app.db.models.transaction import Transaction


async def create_wallet(session: AsyncSession) -> Wallet:
    wallet = Wallet()

    session.add(wallet)

    await session.commit()
    await session.refresh(wallet)

    return wallet


async def get_wallet_by_uuid(
    session: AsyncSession,
    wallet_uuid: str,
) -> Optional[Wallet]:
    stmt = select(Wallet).where(Wallet.id == wallet_uuid)
    result = await session.execute(stmt)

    return result.scalar_one_or_none()


async def get_all_wallets(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> List[Wallet]:
    stmt = select(Wallet).offset(skip).limit(limit)
    result = await session.execute(stmt)

    return result.scalars().all()


async def get_wallets_count(session: AsyncSession) -> int:
    stmt = select(Wallet)
    result = await session.execute(stmt)

    return len(result.scalars().all())


async def update_wallet_balance(
    session: AsyncSession,
    wallet_uuid: str,
    amount: Decimal,
    operation_type: str,
) -> Optional[Wallet]:
    wallet = await get_wallet_by_uuid(session, wallet_uuid)
    if not wallet:
        return None
    
    if operation_type == "DEPOSIT":
        wallet.balance += amount
    elif operation_type == "WITHDRAW":
        if wallet.balance < amount:
            raise ValueError("Insufficient funds")
        wallet.balance -= amount
    
    transaction = Transaction(
        type=operation_type,
        amount=amount,
    )
    session.add(transaction)
    
    await session.commit()
    await session.refresh(wallet)
    
    return wallet
