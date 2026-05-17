from sqlalchemy.orm import Session
from backend.models.vault_rule import VaultRule, RuleType
from backend.models.vault import Vault
from decimal import Decimal

def create_rule(db: Session, user_id: str, vault_id: str,
                rule_type: str, threshold_amount: Decimal = None,
                threshold_percentage: Decimal = None):

    # verify vault belongs to user
    vault = db.query(Vault).filter(
        Vault.id == vault_id,
        Vault.user_id == user_id
    ).first()
    if not vault:
        return None, "Vault not found"

    # validate rule type
    try:
        rule_type_enum = RuleType(rule_type)
    except ValueError:
        return None, f"Invalid rule type. Must be one of: {[r.value for r in RuleType]}"

    # validate thresholds
    if rule_type_enum == RuleType.MIN_BALANCE and not threshold_amount:
        return None, "MIN_BALANCE rule requires threshold_amount"
    if rule_type_enum == RuleType.ALERT_PERCENTAGE and not threshold_percentage:
        return None, "ALERT_PERCENTAGE rule requires threshold_percentage"
    if rule_type_enum == RuleType.ALERT_PERCENTAGE:
        if threshold_percentage < 0 or threshold_percentage > 100:
            return None, "threshold_percentage must be between 0 and 100"

    rule = VaultRule(
        vault_id=vault_id,
        rule_type=rule_type_enum,
        threshold_amount=threshold_amount,
        threshold_percentage=threshold_percentage,
        is_active=True
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule, None

def get_vault_rules(db: Session, user_id: str, vault_id: str):
    vault = db.query(Vault).filter(
        Vault.id == vault_id,
        Vault.user_id == user_id
    ).first()
    if not vault:
        return None, "Vault not found"

    rules = db.query(VaultRule).filter(
        VaultRule.vault_id == vault_id
    ).all()
    return rules, None

def delete_rule(db: Session, user_id: str, rule_id: str):
    rule = db.query(VaultRule).filter(
        VaultRule.id == rule_id
    ).first()
    if not rule:
        return False, "Rule not found"

    # verify vault belongs to user
    vault = db.query(Vault).filter(
        Vault.id == rule.vault_id,
        Vault.user_id == user_id
    ).first()
    if not vault:
        return False, "Not authorized"

    db.delete(rule)
    db.commit()
    return True, None

def check_rules(db: Session, vault: Vault) -> list:
    alerts = []
    rules = db.query(VaultRule).filter(
        VaultRule.vault_id == vault.id,
        VaultRule.is_active == True
    ).all()

    for rule in rules:
        if rule.rule_type == RuleType.MIN_BALANCE:
            if vault.current_balance < rule.threshold_amount:
                alerts.append({
                    "rule_type": "min_balance",
                    "vault_name": vault.name,
                    "message": f"'{vault.name}' balance ₹{vault.current_balance} is below minimum ₹{rule.threshold_amount}"
                })

        elif rule.rule_type == RuleType.ALERT_PERCENTAGE:
            if vault.allocated_amount > 0:
                percentage_left = (vault.current_balance / vault.allocated_amount) * 100
                if percentage_left <= rule.threshold_percentage:
                    alerts.append({
                        "rule_type": "alert_percentage",
                        "vault_name": vault.name,
                        "message": f"'{vault.name}' is at {percentage_left:.0f}% — below your {rule.threshold_percentage}% alert"
                    })

        elif rule.rule_type == RuleType.REQUIRE_REASON:
            alerts.append({
                "rule_type": "require_reason",
                "vault_name": vault.name,
                "message": f"'{vault.name}' requires a reason for any overspending"
            })

    return alerts