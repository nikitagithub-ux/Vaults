from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Optional

class CreateTransactionRequest(BaseModel):
    vault_id: UUID
    amount: Decimal
    description: Optional[str] = None
    merchant_name: Optional[str] = None
    upi_id: Optional[str] = None
    category: Optional[str] = None
    override_reason: Optional[str] = None

class TransactionResponse(BaseModel):
    id: UUID
    vault_id: Optional[UUID]
    bank_account_id: UUID
    amount: Decimal
    type: str
    category: Optional[str]
    description: Optional[str]
    merchant_name: Optional[str]
    upi_id: Optional[str]
    is_vault_violation: Optional[str]
    penalty_amount: Optional[Decimal]
    created_at: datetime

    class Config:
        from_attributes = True
