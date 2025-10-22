from decimal import Decimal

import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repository.wallet_repository import (
    create_wallet,
    get_wallet_by_uuid,
    get_all_wallets,
    get_wallets_count,
    update_wallet_balance,
)


class TestWalletRepository:
    
    @pytest.mark.asyncio
    async def test_create_wallet(self, test_session: AsyncSession):
        wallet = await create_wallet(test_session)
        
        assert wallet.id is not None
        assert wallet.balance == Decimal("0.0")
        assert wallet.created_at is not None
        assert wallet.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_get_wallet_by_uuid(self, test_session: AsyncSession):
        created_wallet = await create_wallet(test_session)
        
        fetched_wallet = await get_wallet_by_uuid(
            test_session,
            str(created_wallet.id)
        )
        
        assert fetched_wallet is not None
        assert fetched_wallet.id == created_wallet.id
        assert fetched_wallet.balance == created_wallet.balance
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_wallet(self, test_session: AsyncSession):
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        wallet = await get_wallet_by_uuid(test_session, fake_uuid)
        
        assert wallet is None
    
    @pytest.mark.asyncio
    async def test_get_all_wallets(self, test_session: AsyncSession):
        await create_wallet(test_session)
        await create_wallet(test_session)
        await create_wallet(test_session)
        
        wallets = await get_all_wallets(test_session)
        
        assert len(wallets) == 3
    
    @pytest.mark.asyncio
    async def test_get_all_wallets_with_pagination(self, test_session: AsyncSession):
        for _ in range(5):
            await create_wallet(test_session)
        
        wallets = await get_all_wallets(test_session, skip=2, limit=2)
        
        assert len(wallets) == 2
    
    @pytest.mark.asyncio
    async def test_get_wallets_count(self, test_session: AsyncSession):
        await create_wallet(test_session)
        await create_wallet(test_session)
        
        count = await get_wallets_count(test_session)
        
        assert count == 2
    
    @pytest.mark.asyncio
    async def test_update_wallet_balance_deposit(self, test_session: AsyncSession):
        wallet = await create_wallet(test_session)
        
        updated_wallet = await update_wallet_balance(
            test_session,
            str(wallet.id),
            Decimal("100.50"),
            "DEPOSIT"
        )
        
        assert updated_wallet is not None
        assert updated_wallet.balance == Decimal("100.50")
    
    @pytest.mark.asyncio
    async def test_update_wallet_balance_withdraw(self, test_session: AsyncSession):
        wallet = await create_wallet(test_session)
        
        await update_wallet_balance(
            test_session,
            str(wallet.id),
            Decimal("200.00"),
            "DEPOSIT"
        )
        
        updated_wallet = await update_wallet_balance(
            test_session,
            str(wallet.id),
            Decimal("50.00"),
            "WITHDRAW"
        )
        
        assert updated_wallet is not None
        assert updated_wallet.balance == Decimal("150.00")
    
    @pytest.mark.asyncio
    async def test_update_wallet_balance_insufficient_funds(
        self,
        test_session: AsyncSession
    ):
        wallet = await create_wallet(test_session)
        
        with pytest.raises(ValueError, match="Insufficient funds"):
            await update_wallet_balance(
                test_session,
                str(wallet.id),
                Decimal("100.00"),
                "WITHDRAW"
            )
    
    @pytest.mark.asyncio
    async def test_update_nonexistent_wallet(self, test_session: AsyncSession):
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        
        result = await update_wallet_balance(
            test_session,
            fake_uuid,
            Decimal("100.00"),
            "DEPOSIT"
        )
        
        assert result is None


class TestWalletRepositoryEdgeCases:
    
    @pytest.mark.asyncio
    async def test_multiple_deposits(self, test_session: AsyncSession):
        wallet = await create_wallet(test_session)
        
        await update_wallet_balance(
            test_session,
            str(wallet.id),
            Decimal("50.00"),
            "DEPOSIT"
        )
        
        await update_wallet_balance(
            test_session,
            str(wallet.id),
            Decimal("30.00"),
            "DEPOSIT"
        )
        
        updated_wallet = await get_wallet_by_uuid(
            test_session,
            str(wallet.id)
        )
        
        assert updated_wallet.balance == Decimal("80.00")
    
    @pytest.mark.asyncio
    async def test_decimal_precision(self, test_session: AsyncSession):
        wallet = await create_wallet(test_session)
        
        updated_wallet = await update_wallet_balance(
            test_session,
            str(wallet.id),
            Decimal("0.01"),
            "DEPOSIT"
        )
        
        assert updated_wallet.balance == Decimal("0.01")
    
    @pytest.mark.asyncio
    async def test_large_amount_operations(self, test_session: AsyncSession):
        wallet = await create_wallet(test_session)
        
        large_amount = Decimal("9999999999.99")
        
        updated_wallet = await update_wallet_balance(
            test_session,
            str(wallet.id),
            large_amount,
            "DEPOSIT"
        )
        
        assert updated_wallet.balance == large_amount
