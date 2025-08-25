from datetime import datetime
from sqlalchemy import ForeignKey, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class PhysicalActivity(Base):
    __tablename__ = "physical_activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    steps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    calories: Mapped[float | None] = mapped_column(Float, nullable=True)

    user = relationship("User", back_populates="activities")
