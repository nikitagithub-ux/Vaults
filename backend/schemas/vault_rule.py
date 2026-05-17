from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Optional

class CreateVaultRuleRequest(BaseModel):
    vault_id: UUID
    rule_type: str
    threshold_amount: Optional[Decimal] = None
    threshold_percentage: Optional[Decimal] = None

class VaultRuleResponse(BaseModel):
    id: UUID
    vault_id: UUID
    rule_type: str
    threshold_amount: Optional[Decimal]
    threshold_percentage: Optional[Decimal]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True