from sqlalchemy import Column, String, DateTime, Numeric, Boolean, ForeignKey, Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import enum
from backend.database import Base

class RuleType(enum.Enum):
    MIN_BALANCE = "min_balance"         # vault cannot go below X amount
    ALERT_PERCENTAGE = "alert_percentage" # alert when balance drops below X%
    REQUIRE_REASON = "require_reason"           # require reason if overspending

class VaultRule(Base):
    __tablename__ = "vault_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vault_id = Column(UUID(as_uuid=True), ForeignKey("vaults.id"), nullable=False)
    rule_type = Column(SqlEnum(RuleType), nullable=False)
    threshold_amount = Column(Numeric(12, 2), nullable=True)
    threshold_percentage = Column(Numeric(5, 2), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # relationships
    vault = relationship("Vault", back_populates="rules")