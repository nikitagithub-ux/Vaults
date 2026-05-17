from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.models.bank_account import BankAccount
from backend.models.transaction import Transaction, TransactionType
from backend.models.user import User
from decimal import Decimal
import uuid

def get_user_bank_accounts(db: Session, user_id: str):
    return db.query(BankAccount).filter(BankAccount.user_id == user_id).all()

def add_bank_account(db: Session, user_id: str, bank_name: str, 
                     account_number: str, ifsc_code: str, 
                     account_holder_name: str, is_primary: bool):
    
    # check duplicate bank for this user
    existing = db.query(BankAccount).filter(
        BankAccount.user_id == user_id,
        BankAccount.bank_name == bank_name
    ).first()
    if existing:
        return None, f"You already have a {bank_name} account"

    # if this is set as primary, unset others
    if is_primary:
        db.query(BankAccount).filter(
            BankAccount.user_id == user_id
        ).update({"is_primary": False})

    bank_account = BankAccount(
        user_id=user_id,
        bank_name=bank_name,
        account_number=account_number,
        ifsc_code=ifsc_code,
        account_holder_name=account_holder_name,
        balance=Decimal("0"),
        is_primary=is_primary
    )
    db.add(bank_account)
    db.commit()
    db.refresh(bank_account)
    return bank_account, None

def seed_money(db: Session, user_id: str, bank_account_id: str, amount: Decimal):
    bank_account = db.query(BankAccount).filter(
        BankAccount.id == bank_account_id,
        BankAccount.user_id == user_id
    ).first()

    if not bank_account:
        return None, "Bank account not found"

    if amount <= 0:
        return None, "Amount must be positive"

    # add money to balance
    bank_account.balance += amount

    # record in transactions as a credit
    transaction = Transaction(
        user_id=user_id,
        vault_id=None,
        bank_account_id=bank_account_id,
        amount=amount,
        type=TransactionType.CREDIT,
        description=f"Money seeded into {bank_account.bank_name} account"
    )
    db.add(transaction)
    db.commit()
    db.refresh(bank_account)
    return bank_account, None

def get_passbook(db: Session, user_id: str, bank_account_id: str):
    bank_account = db.query(BankAccount).filter(
        BankAccount.id == bank_account_id,
        BankAccount.user_id == user_id
    ).first()

    if not bank_account:
        return None, None, "Bank account not found"

    transactions = db.query(Transaction).filter(
        Transaction.bank_account_id == bank_account_id,
        Transaction.user_id == user_id
    ).order_by(desc(Transaction.created_at)).all()

    return bank_account, transactions, None