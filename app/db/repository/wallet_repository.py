from sqlalchemy import (
    select,
    insert,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.wallets import Wallet


async def get_wallet_by_wallet_uuid(
    session: AsyncSession,
    wallet_uuid: str,
) -> Wallet:
    stmt = (
        select(Wallet)
        .where(Wallet.id == wallet_uuid)
    )
    
    result = await session.execute(stmt)
    
    return result.scalar_one_or_none()


async def top_up_wallet(
    session: AsyncSession,
    wallet_uuid: str,
    amount: float,
) -> str:
    wallet = await get_wallet_by_wallet_uuid(
        session=session,
        wallet_uuid=wallet_uuid,
    )
    
    wallet.balance += amount
    
    session.commit()
    
    return {
        "status": "Successfull"
    }


async def write_off_from_wallet(
    session: AsyncSession,
    wallet_uuid: str,
    amount: float,
) -> str:
    wallet = await get_wallet_by_wallet_uuid(
        session=session,
        wallet_uuid=wallet_uuid,
    )
    
    wallet.balance -= amount
    
    session.commit()
    
    return {
        "status": "Successfull"
    }
