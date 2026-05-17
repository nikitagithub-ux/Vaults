from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional
from decimal import Decimal

class BankAccountResponse(BaseModel):
    id: UUID
    bank_name: str
    account_number: str
    ifsc_code: str
    account_holder_name: str
    balance: Decimal
    is_primary: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AddBankAccountRequest(BaseModel):
    bank_name: str
    account_number: str
    ifsc_code: str
    account_holder_name: str
    is_primary: bool = False

class SeedMoneyRequest(BaseModel):
    amount: Decimal
    bank_account_id: UUID

class PassbookEntry(BaseModel):
    id: UUID
    amount: Decimal
    type: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True