from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.api.deps import get_db
from app.models.activity import PhysicalActivity
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityOut

router = APIRouter()


@router.post("/", response_model=ActivityOut)
def create_activity(payload: ActivityCreate, db: Session = Depends(get_db)):
    if not db.get(User, payload.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    obj = PhysicalActivity(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{activity_id}", response_model=ActivityOut)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    obj = db.get(PhysicalActivity, activity_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj


@router.get("/", response_model=list[ActivityOut])
def list_activities(user_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(PhysicalActivity)
    if user_id is not None:
        stmt = stmt.where(PhysicalActivity.user_id == user_id)
    return db.execute(stmt.order_by(PhysicalActivity.start_time.desc())).scalars().all()


@router.put("/{activity_id}", response_model=ActivityOut)
def update_activity(activity_id: int, payload: ActivityUpdate, db: Session = Depends(get_db)):
    obj = db.get(PhysicalActivity, activity_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{activity_id}")
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    obj = db.get(PhysicalActivity, activity_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
