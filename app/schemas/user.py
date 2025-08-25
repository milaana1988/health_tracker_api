from datetime import date, datetime
from pydantic import BaseModel, EmailStr
from app.models.user import GenderEnum


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    gender: GenderEnum | None = None
    date_of_birth: date | None = None
    height_cm: float | None = None
    weight_kg: float | None = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    full_name: str | None = None
    gender: GenderEnum | None = None
    date_of_birth: date | None = None
    height_cm: float | None = None
    weight_kg: float | None = None


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
