from sqlalchemy.orm import Session
from backend.models.vault import Vault
from backend.models.bank_account import BankAccount
from decimal import Decimal

def get_user_vaults(db: Session, user_id: str):
    return db.query(Vault).filter(Vault.user_id == user_id).all()

def get_vault_by_id(db: Session, vault_id: str, user_id: str):
    return db.query(Vault).filter(
        Vault.id == vault_id,
        Vault.user_id == user_id
    ).first()

def create_vault(db: Session, user_id: str, name: str, description: str,
                 color: str, bank_account_id: str):

    # check bank account belongs to user
    bank_account = db.query(BankAccount).filter(
        BankAccount.id == bank_account_id,
        BankAccount.user_id == user_id
    ).first()
    if not bank_account:
        return None, "Bank account not found"

    # check duplicate vault name for this user
    existing = db.query(Vault).filter(
        Vault.user_id == user_id,
        Vault.name == name
    ).first()
    if existing:
        return None, f"You already have a vault named '{name}'"

    vault = Vault(
        user_id=user_id,
        bank_account_id=bank_account_id,
        name=name,
        description=description,
        color=color,
        allocated_amount=Decimal("0"),
        current_balance=Decimal("0"),
        is_locked=False
    )
    db.add(vault)
    db.commit()
    db.refresh(vault)
    return vault, None

def update_vault(db: Session, vault_id: str, user_id: str, **kwargs):
    vault = get_vault_by_id(db, vault_id, user_id)
    if not vault:
        return None, "Vault not found"

    for key, value in kwargs.items():
        if value is not None:
            setattr(vault, key, value)

    db.commit()
    db.refresh(vault)
    return vault, None

def delete_vault(db: Session, vault_id: str, user_id: str):
    vault = get_vault_by_id(db, vault_id, user_id)
    if not vault:
        return False, "Vault not found"

    if vault.current_balance > 0:
        return False, f"Vault still has ₹{vault.current_balance} remaining. Please reallocate before deleting."

    db.delete(vault)
    db.commit()
    return True, None