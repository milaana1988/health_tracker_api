from datetime import datetime
from enum import Enum
from sqlalchemy import ForeignKey, Float, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class BloodTestType(str, Enum):
    glucose = "glucose"
    cholesterol = "cholesterol"


class BloodTest(Base):
    __tablename__ = "blood_tests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    measured_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    test_type: Mapped[BloodTestType] = mapped_column(String(32))
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(32))  # e.g. mg/dL for glucose

    user = relationship("User", back_populates="blood_tests")
