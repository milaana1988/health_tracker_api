from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.api.deps import get_db
from app.models.blood_test import BloodTest
from app.models.user import User
from app.schemas.blood_test import BloodTestCreate, BloodTestUpdate, BloodTestOut

router = APIRouter()


@router.post("/", response_model=BloodTestOut)
def create_blood_test(payload: BloodTestCreate, db: Session = Depends(get_db)):
    if not db.get(User, payload.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    obj = BloodTest(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{bt_id}", response_model=BloodTestOut)
def get_blood_test(bt_id: int, db: Session = Depends(get_db)):
    obj = db.get(BloodTest, bt_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj


@router.get("/", response_model=list[BloodTestOut])
def list_blood_tests(user_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(BloodTest)
    if user_id is not None:
        stmt = stmt.where(BloodTest.user_id == user_id)
    return db.execute(stmt.order_by(BloodTest.measured_at.desc())).scalars().all()


@router.put("/{bt_id}", response_model=BloodTestOut)
def update_blood_test(bt_id: int, payload: BloodTestUpdate, db: Session = Depends(get_db)):
    obj = db.get(BloodTest, bt_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{bt_id}")
def delete_blood_test(bt_id: int, db: Session = Depends(get_db)):
    obj = db.get(BloodTest, bt_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
