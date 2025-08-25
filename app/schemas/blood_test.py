from datetime import datetime
from pydantic import BaseModel
from app.models.blood_test import BloodTestType


class BloodTestBase(BaseModel):
    measured_at: datetime
    test_type: BloodTestType
    value: float
    unit: str


class BloodTestCreate(BloodTestBase):
    user_id: int


class BloodTestUpdate(BaseModel):
    measured_at: datetime | None = None
    test_type: BloodTestType | None = None
    value: float | None = None
    unit: str | None = None


class BloodTestOut(BloodTestBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
