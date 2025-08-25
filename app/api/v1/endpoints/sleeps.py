from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.api.deps import get_db
from app.models.sleep import SleepActivity
from app.models.user import User
from app.schemas.sleep import SleepCreate, SleepUpdate, SleepOut

router = APIRouter()


@router.post("/", response_model=SleepOut)
def create_sleep(payload: SleepCreate, db: Session = Depends(get_db)):
    if not db.get(User, payload.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    obj = SleepActivity(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{sleep_id}", response_model=SleepOut)
def get_sleep(sleep_id: int, db: Session = Depends(get_db)):
    obj = db.get(SleepActivity, sleep_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj


@router.get("/", response_model=list[SleepOut])
def list_sleeps(user_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(SleepActivity)
    if user_id is not None:
        stmt = stmt.where(SleepActivity.user_id == user_id)
    return db.execute(stmt.order_by(SleepActivity.start_time.desc())).scalars().all()


@router.put("/{sleep_id}", response_model=SleepOut)
def update_sleep(sleep_id: int, payload: SleepUpdate, db: Session = Depends(get_db)):
    obj = db.get(SleepActivity, sleep_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{sleep_id}")
def delete_sleep(sleep_id: int, db: Session = Depends(get_db)):
    obj = db.get(SleepActivity, sleep_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
