from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.schemas.bank_account import (
    BankAccountResponse,
    AddBankAccountRequest,
    SeedMoneyRequest,
    PassbookEntry
)
from backend.services.auth_service import get_current_user
from backend.services.bank_service import (
    get_user_bank_accounts,
    add_bank_account,
    seed_money,
    get_passbook
)
from typing import List

router = APIRouter(prefix="/bank-accounts", tags=["Bank Accounts"])

@router.get("", response_model=List[BankAccountResponse])
def get_bank_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_bank_accounts(db, current_user.id)

@router.post("", response_model=BankAccountResponse, status_code=201)
def add_account(
    request: AddBankAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    account, error = add_bank_account(
        db=db,
        user_id=current_user.id,
        bank_name=request.bank_name,
        account_number=request.account_number,
        ifsc_code=request.ifsc_code,
        account_holder_name=request.account_holder_name,
        is_primary=request.is_primary
    )
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    return account

@router.post("/seed", response_model=BankAccountResponse)
def seed_bank_money(
    request: SeedMoneyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    account, error = seed_money(
        db=db,
        user_id=current_user.id,
        bank_account_id=str(request.bank_account_id),
        amount=request.amount
    )
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    return account

@router.get("/{bank_account_id}/passbook")
def passbook(
    bank_account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    account, transactions, error = get_passbook(
        db=db,
        user_id=current_user.id,
        bank_account_id=bank_account_id
    )
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )
    return {
        "account": BankAccountResponse.model_validate(account),
        "transactions": [
            {
                "id": t.id,
                "amount": t.amount,
                "type": t.type.value,
                "description": t.description,
                "created_at": t.created_at
            }
            for t in transactions
        ]
    }