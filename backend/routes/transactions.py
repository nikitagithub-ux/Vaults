from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.schemas.transaction import CreateTransactionRequest, TransactionResponse
from backend.services.auth_service import get_current_user
from backend.services.transaction_service import (
    make_payment,
    get_vault_transactions,
    get_all_transactions
)
from typing import List
from decimal import Decimal

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("", response_model=TransactionResponse)
def create_transaction(
    request: CreateTransactionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result, error = make_payment(
        db=db,
        user_id=current_user.id,
        vault_id=str(request.vault_id),
        amount=request.amount,
        description=request.description,
        merchant_name=request.merchant_name,
        upi_id=request.upi_id,
        category=request.category,
        override_reason=request.override_reason
    )
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    return result["transaction"]

@router.get("", response_model=List[TransactionResponse])
def all_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_all_transactions(db, current_user.id)

@router.get("/vault/{vault_id}", response_model=List[TransactionResponse])
def vault_transactions(
    vault_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transactions, error = get_vault_transactions(db, current_user.id, vault_id)
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )
    return transactions