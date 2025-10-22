from decimal import Decimal

from datetime import datetime

from typing import List

from pydantic import (
    BaseModel, 
    Field,
)

from enum import Enum


class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class WalletOperationRequest(BaseModel):
    operation_type: OperationType
    amount: Decimal = Field(gt=0, description="Amount must be positive")


class WalletOperationResponse(BaseModel):
    status: str
    new_balance: Decimal


class WalletCreateResponse(BaseModel):
    wallet_id: str
    balance: Decimal
    created_at: datetime


class WalletResponse(BaseModel):
    wallet_id: str
    balance: Decimal
    created_at: datetime
    updated_at: datetime


class WalletsListResponse(BaseModel):
    wallets: List[WalletResponse]
    total: int
