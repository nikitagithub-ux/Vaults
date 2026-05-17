from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models.vault import Vault
from backend.models.bank_account import BankAccount
from backend.models.transaction import Transaction, TransactionType
from datetime import datetime, timezone

def get_dashboard(db: Session, user_id: str):
    # get all bank accounts
    bank_accounts = db.query(BankAccount).filter(
        BankAccount.user_id == user_id
    ).all()
    total_bank_balance = sum(b.balance for b in bank_accounts)

    # get all vaults
    all_vaults = db.query(Vault).filter(
        Vault.user_id == user_id
    ).all()

    # separate penalty pool from regular vaults
    penalty_vault = next((v for v in all_vaults if v.name == "Penalty Pool"), None)
    regular_vaults = [v for v in all_vaults if v.name != "Penalty Pool"]

    total_vault_balance = sum(v.current_balance for v in regular_vaults)
    total_allocated = sum(v.allocated_amount for v in regular_vaults)
    penalty_pool_balance = penalty_vault.current_balance if penalty_vault else 0

    # calculate total spent this month
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    monthly_spent = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == TransactionType.DEBIT,
        Transaction.created_at >= month_start,
        Transaction.vault_id != None,
        Transaction.category != "penalty"
    ).scalar() or 0

    # get recent 10 transactions
    recent_transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).order_by(Transaction.created_at.desc()).limit(10).all()

    # generate alerts
    alerts = []
    for vault in regular_vaults:
        if vault.allocated_amount > 0:
            percentage_left = (vault.current_balance / vault.allocated_amount) * 100
            if percentage_left <= 20:
                alerts.append({
                    "vault_id": str(vault.id),
                    "vault_name": vault.name,
                    "message": f"Only {percentage_left:.0f}% left in {vault.name} vault",
                    "severity": "high" if percentage_left <= 10 else "medium"
                })

    return {
        "total_bank_balance": float(total_bank_balance),
        "total_vault_balance": float(total_vault_balance),
        "total_allocated": float(total_allocated),
        "total_spent_this_month": float(monthly_spent),
        "penalty_pool_balance": float(penalty_pool_balance),
        "vaults": regular_vaults,
        "recent_transactions": recent_transactions,
        "alerts": alerts
    }