from decimal import Decimal

from typing import (
    TYPE_CHECKING,
    Annotated,
)

from fastapi import (
    APIRouter, 
    HTTPException, 
    Depends
)

from app.core.config import settings
from app.db.db_helper import db_helper
from app.db.repository.wallet_repository import (
    create_wallet,
    get_wallet_by_uuid,
    get_all_wallets,
    get_wallets_count,
    update_wallet_balance,
)
from app.api.schemas.operations import (
    WalletOperationRequest,
    WalletOperationResponse,
    WalletCreateResponse,
    WalletResponse,
    WalletsListResponse,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix=settings.api.prefix,
    tags=["Wallets"]
)


@router.post(
    "/wallets/create_wallet", 
    response_model=WalletCreateResponse
)
async def create_new_wallet(
    session: Annotated[
        "AsyncSession",
        Depends(db_helper.session_getter)
    ],
):
    wallet = await create_wallet(session)

    return WalletCreateResponse(
        wallet_id=str(wallet.id),
        balance=wallet.balance,
        created_at=wallet.created_at,
    )


@router.get("/wallets/get_wallets", response_model=WalletsListResponse)
async def get_all_wallets_endpoint(
    session: Annotated[
        "AsyncSession",
        Depends(db_helper.session_getter)
    ],
    skip: int = 0,
    limit: int = 100,
):
    wallets = await get_all_wallets(session, skip, limit)
    total = await get_wallets_count(session)
    
    wallet_responses = [
        WalletResponse(
            wallet_id=str(wallet.id),
            balance=wallet.balance,
            created_at=wallet.created_at,
            updated_at=wallet.updated_at,
        )
        for wallet in wallets
    ]
    
    return WalletsListResponse(
        wallets=wallet_responses,
        total=total,
    )


@router.get("/wallets/{wallet_uuid}", response_model=WalletResponse)
async def get_wallet(
    wallet_uuid: str,
    session: Annotated[
        "AsyncSession",
        Depends(db_helper.session_getter)
    ],
):
    wallet = await get_wallet_by_uuid(session, wallet_uuid)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    return WalletResponse(
        wallet_id=str(wallet.id),
        balance=wallet.balance,
        created_at=wallet.created_at,
        updated_at=wallet.updated_at,
    )


@router.post(
    "/wallets/{wallet_uuid}/operation", 
    response_model=WalletOperationResponse
)
async def wallet_operation(
    session: Annotated[
        "AsyncSession",
        Depends(db_helper.session_getter)
    ],
    wallet_uuid: str,
    operation: WalletOperationRequest,
):
    try:
        wallet = await update_wallet_balance(
            session,
            wallet_uuid,
            Decimal(operation.amount),
            operation.operation_type.value,
        )
        
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        return WalletOperationResponse(
            status="Successful",
            new_balance=wallet.balance,
        )
    
    except ValueError as e:
        if "Insufficient funds" in str(e):
            raise HTTPException(status_code=400, detail="Insufficient funds")
        
        raise HTTPException(status_code=400, detail=str(e))
