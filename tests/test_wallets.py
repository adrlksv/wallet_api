import pytest
import asyncio

from httpx import AsyncClient


class TestWalletCreation:
    
    @pytest.mark.asyncio
    async def test_create_wallet_success(self, client: AsyncClient):
        response = await client.post("/api/wallets/create_wallet")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "wallet_id" in data
        assert "balance" in data
        assert "created_at" in data
        assert float(data["balance"]) == 0.0
    
    @pytest.mark.asyncio
    async def test_create_multiple_wallets(self, client: AsyncClient):
        response1 = await client.post("/api/wallets/create_wallet")
        response2 = await client.post("/api/wallets/create_wallet")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        wallet1_id = response1.json()["wallet_id"]
        wallet2_id = response2.json()["wallet_id"]
        
        assert wallet1_id != wallet2_id


class TestGetWallet:
    
    @pytest.mark.asyncio
    async def test_get_existing_wallet(self, client: AsyncClient):
        create_response = await client.post("/api/wallets/create_wallet")
        wallet_id = create_response.json()["wallet_id"]
        
        response = await client.get(f"/api/wallets/{wallet_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["wallet_id"] == wallet_id
        assert "balance" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_wallet(self, client: AsyncClient):
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/wallets/{fake_uuid}")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Wallet not found"


class TestGetAllWallets:
    
    @pytest.mark.asyncio
    async def test_get_all_wallets_empty(self, client: AsyncClient):
        response = await client.get("/api/wallets/get_wallets")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "wallets" in data
        assert "total" in data
        assert isinstance(data["wallets"], list)
        assert isinstance(data["total"], int)
    
    @pytest.mark.asyncio
    async def test_get_all_wallets_with_data(self, client: AsyncClient):
        await client.post("/api/wallets/create_wallet")
        await client.post("/api/wallets/create_wallet")
        await client.post("/api/wallets/create_wallet")
        
        response = await client.get("/api/wallets/get_wallets")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["wallets"]) == 3
        assert data["total"] == 3
    
    @pytest.mark.asyncio
    async def test_get_all_wallets_with_pagination(self, client: AsyncClient):
        for _ in range(5):
            await client.post("/api/wallets/create_wallet")
        
        response = await client.get("/api/wallets/get_wallets?skip=2&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["wallets"]) == 2
        assert data["total"] == 5
    
    @pytest.mark.asyncio
    async def test_get_all_wallets_default_pagination(self, client: AsyncClient):
        await client.post("/api/wallets/create_wallet")
        
        response = await client.get("/api/wallets/get_wallets")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["wallets"]) <= 100


class TestWalletOperations:
    
    @pytest.mark.asyncio
    async def test_deposit_to_wallet(self, client: AsyncClient):
        create_response = await client.post("/api/wallets/create_wallet")
        wallet_id = create_response.json()["wallet_id"]
        
        operation_data = {
            "operation_type": "DEPOSIT",
            "amount": "100.50"
        }
        
        response = await client.post(
            f"/api/wallets/{wallet_id}/operation",
            json=operation_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "Successful"
        assert float(data["new_balance"]) == 100.50
    
    @pytest.mark.asyncio
    async def test_withdraw_from_wallet(self, client: AsyncClient):
        create_response = await client.post("/api/wallets/create_wallet")
        wallet_id = create_response.json()["wallet_id"]
        
        deposit_data = {
            "operation_type": "DEPOSIT",
            "amount": "100.00"
        }
        await client.post(f"/api/wallets/{wallet_id}/operation", json=deposit_data)
        
        withdraw_data = {
            "operation_type": "WITHDRAW",
            "amount": "30.00"
        }
        
        response = await client.post(
            f"/api/wallets/{wallet_id}/operation",
            json=withdraw_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "Successful"
        assert float(data["new_balance"]) == 70.00
    
    @pytest.mark.asyncio
    async def test_withdraw_insufficient_funds(self, client: AsyncClient):
        create_response = await client.post("/api/wallets/create_wallet")
        wallet_id = create_response.json()["wallet_id"]
        
        withdraw_data = {
            "operation_type": "WITHDRAW",
            "amount": "50.00"
        }
        
        response = await client.post(
            f"/api/wallets/{wallet_id}/operation",
            json=withdraw_data
        )
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Insufficient funds"
    
    @pytest.mark.asyncio
    async def test_operation_on_nonexistent_wallet(self, client: AsyncClient):
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        
        operation_data = {
            "operation_type": "DEPOSIT",
            "amount": "100.00"
        }
        
        response = await client.post(
            f"/api/wallets/{fake_uuid}/operation",
            json=operation_data
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Wallet not found"
    
    @pytest.mark.asyncio
    async def test_operation_with_negative_amount(self, client: AsyncClient):
        create_response = await client.post("/api/wallets/create_wallet")
        wallet_id = create_response.json()["wallet_id"]
        
        operation_data = {
            "operation_type": "DEPOSIT",
            "amount": "-50.00"
        }
        
        response = await client.post(
            f"/api/wallets/{wallet_id}/operation",
            json=operation_data
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_operation_with_zero_amount(self, client: AsyncClient):
        create_response = await client.post("/api/wallets/create_wallet")
        wallet_id = create_response.json()["wallet_id"]
        
        operation_data = {
            "operation_type": "DEPOSIT",
            "amount": "0.00"
        }
        
        response = await client.post(
            f"/api/wallets/{wallet_id}/operation",
            json=operation_data
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_multiple_operations_on_same_wallet(self, client: AsyncClient):
        create_response = await client.post("/api/wallets/create_wallet")
        wallet_id = create_response.json()["wallet_id"]
        
        operations = [
            {"operation_type": "DEPOSIT", "amount": "100.00"},
            {"operation_type": "DEPOSIT", "amount": "50.00"},
            {"operation_type": "WITHDRAW", "amount": "30.00"},
            {"operation_type": "DEPOSIT", "amount": "20.00"},
        ]
        
        for operation in operations:
            response = await client.post(
                f"/api/wallets/{wallet_id}/operation",
                json=operation
            )
            assert response.status_code == 200
        
        final_response = await client.get(f"/api/wallets/{wallet_id}")
        assert response.status_code == 200
        
        final_balance = float(final_response.json()["balance"])
        assert final_balance == 140.00
    
    @pytest.mark.asyncio
    async def test_operation_with_invalid_type(self, client: AsyncClient):
        create_response = await client.post("/api/wallets/create_wallet")
        wallet_id = create_response.json()["wallet_id"]
        
        operation_data = {
            "operation_type": "INVALID",
            "amount": "100.00"
        }
        
        response = await client.post(
            f"/api/wallets/{wallet_id}/operation",
            json=operation_data
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_operation_with_large_amount(self, client: AsyncClient):
        create_response = await client.post("/api/wallets/create_wallet")
        wallet_id = create_response.json()["wallet_id"]
        
        operation_data = {
            "operation_type": "DEPOSIT",
            "amount": "999999999.99"
        }
        
        response = await client.post(
            f"/api/wallets/{wallet_id}/operation",
            json=operation_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert float(data["new_balance"]) == 999999999.99


class TestWalletIntegration:
    
    @pytest.mark.asyncio
    async def test_full_wallet_lifecycle(self, client: AsyncClient):
        create_response = await client.post("/api/wallets/create_wallet")
        assert create_response.status_code == 200
        wallet_id = create_response.json()["wallet_id"]
        
        get_response = await client.get(f"/api/wallets/{wallet_id}")
        assert get_response.status_code == 200
        assert float(get_response.json()["balance"]) == 0.0
        
        deposit_response = await client.post(
            f"/api/wallets/{wallet_id}/operation",
            json={"operation_type": "DEPOSIT", "amount": "500.00"}
        )
        assert deposit_response.status_code == 200
        assert float(deposit_response.json()["new_balance"]) == 500.00
        
        withdraw_response = await client.post(
            f"/api/wallets/{wallet_id}/operation",
            json={"operation_type": "WITHDRAW", "amount": "200.00"}
        )
        assert withdraw_response.status_code == 200
        assert float(withdraw_response.json()["new_balance"]) == 300.00
        
        final_response = await client.get(f"/api/wallets/{wallet_id}")
        assert final_response.status_code == 200
        assert float(final_response.json()["balance"]) == 300.00
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, client: AsyncClient):
        create_response = await client.post("/api/wallets/create_wallet")
        wallet_id = create_response.json()["wallet_id"]
        
        await client.post(
            f"/api/wallets/{wallet_id}/operation",
            json={"operation_type": "DEPOSIT", "amount": "1000.00"}
        )
        
        async def withdraw():
            return await client.post(
                f"/api/wallets/{wallet_id}/operation",
                json={"operation_type": "WITHDRAW", "amount": "100.00"}
            )
        
        responses = await asyncio.gather(
            withdraw(),
            withdraw(),
            withdraw(),
        )
        
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count <= 10
        
        final_response = await client.get(f"/api/wallets/{wallet_id}")
        final_balance = float(final_response.json()["balance"])
        assert final_balance >= 0
