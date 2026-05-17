from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import enum
from backend.database import Base

class TransactionType(enum.Enum):
    DEBIT = "debit"
    CREDIT = "credit"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    vault_id = Column(UUID(as_uuid=True), ForeignKey("vaults.id"), nullable=True)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    type = Column(SqlEnum(TransactionType), nullable=False)
    category = Column(String, nullable=True)
    description = Column(String, nullable=True)
    merchant_name = Column(String, nullable=True)
    upi_id = Column(String, nullable=True)
    is_vault_violation = Column(String, nullable=True)
    penalty_amount = Column(Numeric(12, 2), nullable=True, default=0)
    external_reference_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # relationships
    user = relationship("User", back_populates="transactions")
    vault = relationship("Vault", back_populates="transactions")
    bank_account = relationship("BankAccount")