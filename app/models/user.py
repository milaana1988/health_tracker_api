from datetime import date, datetime
from enum import Enum
from sqlalchemy import String, Date, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gender: Mapped[GenderEnum | None] = mapped_column(String(16), nullable=True)  # store as string
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    activities = relationship(
        "PhysicalActivity", back_populates="user", cascade="all, delete-orphan"
    )
    sleeps = relationship("SleepActivity", back_populates="user", cascade="all, delete-orphan")
    blood_tests = relationship("BloodTest", back_populates="user", cascade="all, delete-orphan")
