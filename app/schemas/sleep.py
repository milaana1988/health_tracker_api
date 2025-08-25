from datetime import datetime
from pydantic import BaseModel


class SleepBase(BaseModel):
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    sleep_quality: int | None = None


class SleepCreate(SleepBase):
    user_id: int


class SleepUpdate(BaseModel):
    start_time: datetime | None = None
    end_time: datetime | None = None
    duration_minutes: int | None = None
    sleep_quality: int | None = None


class SleepOut(SleepBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
