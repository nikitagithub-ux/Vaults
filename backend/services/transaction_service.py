from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.models.vault import Vault
from backend.models.bank_account import BankAccount
from backend.models.transaction import Transaction, TransactionType
from decimal import Decimal
from backend.services.vault_rule_service import check_rules

PENALTY_RATE = Decimal("0.015")  # 1.5%

def get_penalty_vault(db: Session, user_id: str):
    return db.query(Vault).filter(
        Vault.user_id == user_id,
        Vault.name == "Penalty Pool"
    ).first()

def make_payment(db: Session, user_id: str, vault_id: str, amount: Decimal,
                 description: str, merchant_name: str, upi_id: str,
                 category: str, override_reason: str = None):

    # get vault
    vault = db.query(Vault).filter(
        Vault.id == vault_id,
        Vault.user_id == user_id
    ).first()
    if not vault:
        return None, "Vault not found"

    if vault.name == "Penalty Pool":
        return None, "Cannot make payments from Penalty Pool"

    if amount <= 0:
        return None, "Amount must be positive"

    # get bank account
    bank_account = db.query(BankAccount).filter(
        BankAccount.id == vault.bank_account_id
    ).first()

    # check vault has enough balance
    if vault.current_balance < amount:
        return None, f"Insufficient vault balance. '{vault.name}' has ₹{vault.current_balance} but payment is ₹{amount}"


    # detect vault violation
    is_violation = False
    violation_reason = None

    if category and vault.name:
        category_lower = category.lower()
        vault_name_lower = vault.name.lower()
        vault_desc_lower = vault.description.lower() if vault.description else ""
        
        # check if category matches vault name OR description
        if category_lower not in vault_name_lower and category_lower not in vault_desc_lower:
            is_violation = True
            violation_reason = override_reason or f"Payment category '{category}' doesn't match vault purpose"

    # calculate penalty
    penalty_amount = Decimal("0")
    if is_violation:
        penalty_amount = (amount * PENALTY_RATE).quantize(Decimal("0.01"))

    # deduct from vault and bank
    vault.current_balance -= amount

    # record main transaction
    transaction = Transaction(
        user_id=user_id,
        vault_id=vault.id,
        bank_account_id=bank_account.id,
        amount=amount,
        type=TransactionType.DEBIT,
        category=category,
        description=description,
        merchant_name=merchant_name,
        upi_id=upi_id,
        is_vault_violation=violation_reason,
        penalty_amount=penalty_amount
    )
    db.add(transaction)

    # apply penalty if violation
    if penalty_amount > 0:
        penalty_vault = get_penalty_vault(db, user_id)
        if penalty_vault:
            penalty_vault.current_balance += penalty_amount

            # record penalty transaction
            penalty_transaction = Transaction(
                user_id=user_id,
                vault_id=penalty_vault.id,
                bank_account_id=bank_account.id,
                amount=penalty_amount,
                type=TransactionType.DEBIT,
                category="penalty",
                description=f"Penalty for vault violation: {violation_reason}",
            )
            db.add(penalty_transaction)

    db.commit()
    db.refresh(transaction)
    rule_alerts = check_rules(db, vault)
    return {"transaction": transaction, "alerts": rule_alerts}, None

def get_vault_transactions(db: Session, user_id: str, vault_id: str):
    vault = db.query(Vault).filter(
        Vault.id == vault_id,
        Vault.user_id == user_id
    ).first()
    if not vault:
        return None, "Vault not found"
    
    if vault.is_locked:
        return None, f"Vault '{vault.name}' is locked. Payments cannot be made from it."

    transactions = db.query(Transaction).filter(
        Transaction.vault_id == vault_id,
        Transaction.user_id == user_id
    ).order_by(desc(Transaction.created_at)).all()

    return transactions, None

def get_all_transactions(db: Session, user_id: str):
    return db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).order_by(desc(Transaction.created_at)).all()