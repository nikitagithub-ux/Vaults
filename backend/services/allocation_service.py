from sqlalchemy.orm import Session
from backend.models.vault import Vault
from backend.models.bank_account import BankAccount
from backend.models.transaction import Transaction, TransactionType
from decimal import Decimal
from typing import List, Dict

def allocate_funds(db: Session, user_id: str, bank_account_id: str, 
                   allocations: List[Dict]):

    # get bank account
    bank_account = db.query(BankAccount).filter(
        BankAccount.id == bank_account_id,
        BankAccount.user_id == user_id
    ).first()
    if not bank_account:
        return None, "Bank account not found"

    # calculate total being allocated
    total = sum(Decimal(str(a["amount"])) for a in allocations)

    if total <= 0:
        return None, "Total allocation must be positive"

    if total > bank_account.balance:
        return None, f"Insufficient bank balance. You have ₹{bank_account.balance} but tried to allocate ₹{total}"

    balance_before = bank_account.balance
    results = []

    for allocation in allocations:
        vault_id = str(allocation["vault_id"])
        amount = Decimal(str(allocation["amount"]))

        if amount <= 0:
            return None, f"Allocation amount must be positive for each vault"

        # get vault and verify it belongs to this user
        vault = db.query(Vault).filter(
            Vault.id == vault_id,
            Vault.user_id == user_id
        ).first()
        if not vault:
            return None, f"Vault {vault_id} not found"

        if vault.is_locked:
            return None, f"Vault '{vault.name}' is locked and cannot receive funds"

        # move money
        vault.current_balance += amount
        vault.allocated_amount += amount
        bank_account.balance -= amount

        # record transaction
        transaction = Transaction(
            user_id=user_id,
            vault_id=vault.id,
            bank_account_id=bank_account_id,
            amount=amount,
            type=TransactionType.CREDIT,
            description=f"Allocation to {vault.name} vault",
            category="allocation"
        )
        db.add(transaction)

        results.append({
            "vault_id": vault.id,
            "vault_name": vault.name,
            "allocated_amount": amount,
            "new_balance": vault.current_balance
        })

    db.commit()

    return {
        "message": "Funds allocated successfully",
        "bank_balance_before": balance_before,
        "bank_balance_after": bank_account.balance,
        "allocations": results
    }, None