from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.schemas.vault_rule import CreateVaultRuleRequest, VaultRuleResponse
from backend.services.auth_service import get_current_user
from backend.services.vault_rule_service import (
    create_rule,
    get_vault_rules,
    delete_rule
)
from typing import List

router = APIRouter(prefix="/vault-rules", tags=["Vault Rules"])

@router.post("", response_model=VaultRuleResponse, status_code=201)
def create_vault_rule(
    request: CreateVaultRuleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rule, error = create_rule(
        db=db,
        user_id=current_user.id,
        vault_id=str(request.vault_id),
        rule_type=request.rule_type,
        threshold_amount=request.threshold_amount,
        threshold_percentage=request.threshold_percentage
    )
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    return rule

@router.get("/{vault_id}", response_model=List[VaultRuleResponse])
def get_rules(
    vault_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rules, error = get_vault_rules(db, current_user.id, vault_id)
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )
    return rules

@router.delete("/{rule_id}", status_code=204)
def delete_vault_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success, error = delete_rule(db, current_user.id, rule_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )