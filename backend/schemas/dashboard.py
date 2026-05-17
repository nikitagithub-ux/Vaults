from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from backend.schemas.vault import VaultResponse
from backend.schemas.transaction import TransactionResponse

class Alert(BaseModel):
    vault_id: str
    vault_name: str
    message: str
    severity: str

class DashboardResponse(BaseModel):
    total_bank_balance: float
    total_vault_balance: float
    total_allocated: float
    total_spent_this_month: float
    penalty_pool_balance: float
    vaults: List[VaultResponse]
    recent_transactions: List[TransactionResponse]
    alerts: List[Alert]