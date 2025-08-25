from datetime import datetime
from pydantic import BaseModel


class ActivityBase(BaseModel):
    start_time: datetime
    end_time: datetime
    steps: int | None = None
    distance_km: float | None = None
    calories: float | None = None


class ActivityCreate(ActivityBase):
    user_id: int


class ActivityUpdate(BaseModel):
    start_time: datetime | None = None
    end_time: datetime | None = None
    steps: int | None = None
    distance_km: float | None = None
    calories: float | None = None


class ActivityOut(ActivityBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
