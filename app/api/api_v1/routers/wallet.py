from fastapi import APIRouter

from app.core.config import settings


router = APIRouter(
    prefix=settings.api.prefix,
    tags=["Wallets"]
)


@router.get("/wallets/{wallet_uuid}")
async def get_balance(
    wallet_uuid: str
)