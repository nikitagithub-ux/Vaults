from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.schemas.vault import CreateVaultRequest, UpdateVaultRequest, VaultResponse
from backend.services.auth_service import get_current_user
from backend.services.vault_service import (
    get_user_vaults,
    get_vault_by_id,
    create_vault,
    update_vault,
    delete_vault
)
from typing import List

router = APIRouter(prefix="/vaults", tags=["Vaults"])

@router.get("", response_model=List[VaultResponse])
def get_vaults(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_vaults(db, current_user.id)

@router.post("", response_model=VaultResponse, status_code=201)
def create(
    request: CreateVaultRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vault, error = create_vault(
        db=db,
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        color=request.color,
        bank_account_id=str(request.bank_account_id)
    )
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    return vault

@router.get("/{vault_id}", response_model=VaultResponse)
def get_vault(
    vault_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vault = get_vault_by_id(db, vault_id, current_user.id)
    if not vault:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vault not found"
        )
    return vault

@router.put("/{vault_id}", response_model=VaultResponse)
def update(
    vault_id: str,
    request: UpdateVaultRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vault, error = update_vault(
        db=db,
        vault_id=vault_id,
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        color=request.color,
        is_locked=request.is_locked
    )
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )
    return vault

@router.delete("/{vault_id}", status_code=204)
def delete(
    vault_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success, error = delete_vault(db, vault_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )