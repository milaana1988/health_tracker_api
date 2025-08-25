from datetime import datetime
from sqlalchemy import ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class SleepActivity(Base):
    __tablename__ = "sleep_activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    sleep_quality: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0..100

    user = relationship("User", back_populates="sleeps")
