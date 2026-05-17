from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional
from decimal import Decimal

class CreateVaultRequest(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    bank_account_id: UUID

    class Config:
        str_strip_whitespace = True

class UpdateVaultRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    is_locked: Optional[bool] = None

class VaultResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    color: Optional[str]
    allocated_amount: Decimal
    current_balance: Decimal
    is_locked: bool
    bank_account_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True