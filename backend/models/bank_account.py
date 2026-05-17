from sqlalchemy import Column, String, DateTime, Numeric, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from backend.database import Base

class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    bank_name = Column(String, nullable=False)
    account_number = Column(String, unique=True, nullable=False)
    ifsc_code = Column(String, nullable=False)
    account_holder_name = Column(String, nullable=False)
    balance = Column(Numeric(12, 2), nullable=False, default=0)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("user_id", "bank_name", name="uq_user_bank"),
    )

    # relationships
    user = relationship("User", back_populates="bank_accounts")
    vaults = relationship("Vault", back_populates="bank_account")