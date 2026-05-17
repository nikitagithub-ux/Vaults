from sqlalchemy import Column, String, DateTime, Numeric, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from backend.database import Base

class Vault(Base):
    __tablename__ = "vaults"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    color = Column(String, nullable=True)
    allocated_amount = Column(Numeric(12, 2), nullable=False, default=0)
    current_balance = Column(Numeric(12, 2), nullable=False, default=0)
    is_locked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_vault_name"),
    )

    # relationships
    user = relationship("User", back_populates="vaults")
    bank_account = relationship("BankAccount", back_populates="vaults")
    transactions = relationship("Transaction", back_populates="vault")
    rules = relationship("VaultRule", back_populates="vault")