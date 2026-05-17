from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from typing import List

class VaultAllocation(BaseModel):
    vault_id: UUID
    amount: Decimal

class AllocateRequest(BaseModel):
    bank_account_id: UUID
    allocations: List[VaultAllocation]

class AllocationResult(BaseModel):
    vault_id: UUID
    vault_name: str
    allocated_amount: Decimal
    new_balance: Decimal

class AllocateResponse(BaseModel):
    message: str
    bank_balance_before: Decimal
    bank_balance_after: Decimal
    allocations: List[AllocationResult]