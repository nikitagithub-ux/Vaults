from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.schemas.allocation import AllocateRequest, AllocateResponse
from backend.services.auth_service import get_current_user
from backend.services.allocation_service import allocate_funds

router = APIRouter(prefix="/allocate", tags=["Allocation"])

@router.post("", response_model=AllocateResponse)
def allocate(
    request: AllocateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result, error = allocate_funds(
        db=db,
        user_id=current_user.id,
        bank_account_id=str(request.bank_account_id),
        allocations=[
            {"vault_id": a.vault_id, "amount": a.amount}
            for a in request.allocations
        ]
    )
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    return result