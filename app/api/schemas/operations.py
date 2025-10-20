from pydantic import BaseModel


class OperationType(BaseModel):
    deposit: str = "DEPOSIT"
    withdraw: str = "WITHDRAW"
