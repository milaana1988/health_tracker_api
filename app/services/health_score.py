"""Health score aggregation and normalization.

Formula (composite, 0..100):
- Activity (50%): average steps per day over window, min-max normalized across users
- Sleep (30%): mix of duration score (target 7.5h) and quality score, then min-max across users
- Glucose (20%): average glucose; lower is better; reversed min-max across users

Returned components are also 0..100.
"""

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, select

from app.models.activity import PhysicalActivity
from app.models.sleep import SleepActivity
from app.models.blood_test import BloodTest, BloodTestType


def _normalize_minmax(value: float, vmin: float, vmax: float, reverse: bool = False) -> float:
    if vmin is None or vmax is None or vmax <= vmin:
        return 50.0
    norm = (value - vmin) / (vmax - vmin) if (vmax - vmin) else 0.5
    if reverse:
        norm = 1.0 - norm
    return max(0.0, min(1.0, norm)) * 100.0


def _target_duration_score(minutes: float, target_min: float = 450.0) -> float:
    """Score is highest near target (default 7.5h). Penalize deviation symmetrically."""
    if minutes <= 0:
        return 0.0
    deviation = abs(minutes - target_min)
    # 0 penalty up to 30 min, then linear drop. Clamp at 0.
    if deviation <= 30:
        base = 1.0
    else:
        base = max(0.0, 1.0 - (deviation - 30) / 360)  # lose all by ~6.5h off
    return base * 100.0


def compute_health_score(db: Session, user_id: int, days: int = 30) -> Dict[str, Any]:
    now = datetime.utcnow()
    since = now - timedelta(days=days)

    # --- User aggregates ---
    # Activity: average steps per day (sum steps / distinct days)
    user_steps_sum, user_days = db.execute(
        select(
            func.coalesce(func.sum(PhysicalActivity.steps), 0),
            func.count(func.distinct(func.date(PhysicalActivity.start_time))),
        ).where(PhysicalActivity.user_id == user_id, PhysicalActivity.start_time >= since)
    ).one()
    user_steps_avg = (user_steps_sum / max(user_days, 1)) if user_steps_sum is not None else 0.0

    # Sleep: average duration and quality
    sleep_rows = db.execute(
        select(
            func.coalesce(func.avg(SleepActivity.duration_minutes), 0),
            func.coalesce(func.avg(SleepActivity.sleep_quality), 0),
        ).where(SleepActivity.user_id == user_id, SleepActivity.start_time >= since)
    ).one()
    user_sleep_avg_minutes = float(sleep_rows[0] or 0)
    user_sleep_avg_quality = float(sleep_rows[1] or 0)
    user_sleep_duration_score = _target_duration_score(user_sleep_avg_minutes)
    user_sleep_mix = 0.7 * user_sleep_duration_score + 0.3 * (user_sleep_avg_quality)

    # Glucose: average value for glucose tests
    glucose_row = db.execute(
        select(func.coalesce(func.avg(BloodTest.value), 0)).where(
            BloodTest.user_id == user_id,
            BloodTest.measured_at >= since,
            BloodTest.test_type == BloodTestType.glucose,
        )
    ).one()
    user_glucose_avg = float(glucose_row[0] or 0)

    # --- Population aggregates per user ---
    # Steps per-user averages
    steps_per_user = db.execute(
        select(
            PhysicalActivity.user_id,
            func.coalesce(func.sum(PhysicalActivity.steps), 0).label("sum_steps"),
            func.count(func.distinct(func.date(PhysicalActivity.start_time))).label("days"),
        )
        .where(PhysicalActivity.start_time >= since)
        .group_by(PhysicalActivity.user_id)
    ).all()
    steps_avgs = [
        (s.sum_steps / max(s.days, 1)) if s.sum_steps is not None else 0.0 for s in steps_per_user
    ]
    steps_min = min(steps_avgs) if steps_avgs else 0.0
    steps_max = max(steps_avgs) if steps_avgs else 0.0

    # Sleep mix per-user
    sleep_avgs = []
    sleep_rows = db.execute(
        select(
            SleepActivity.user_id,
            func.coalesce(func.avg(SleepActivity.duration_minutes), 0).label("avg_minutes"),
            func.coalesce(func.avg(SleepActivity.sleep_quality), 0).label("avg_quality"),
        )
        .where(SleepActivity.start_time >= since)
        .group_by(SleepActivity.user_id)
    ).all()
    for r in sleep_rows:
        d_score = _target_duration_score(float(r.avg_minutes or 0))
        mix = 0.7 * d_score + 0.3 * float(r.avg_quality or 0)
        sleep_avgs.append(mix)
    sleep_min = min(sleep_avgs) if sleep_avgs else 0.0
    sleep_max = max(sleep_avgs) if sleep_avgs else 0.0

    # Glucose per-user averages (lower is better, reverse scale)
    glu_rows = db.execute(
        select(BloodTest.user_id, func.coalesce(func.avg(BloodTest.value), 0).label("avg_val"))
        .where(BloodTest.measured_at >= since, BloodTest.test_type == BloodTestType.glucose)
        .group_by(BloodTest.user_id)
    ).all()
    glu_avgs = [float(r.avg_val or 0) for r in glu_rows]
    glu_min = min(glu_avgs) if glu_avgs else user_glucose_avg
    glu_max = max(glu_avgs) if glu_avgs else user_glucose_avg

    # --- Normalize ---
    steps_score = _normalize_minmax(user_steps_avg, steps_min, steps_max)
    sleep_score = _normalize_minmax(user_sleep_mix, sleep_min, sleep_max)
    glucose_score = (
        _normalize_minmax(user_glucose_avg, glu_min, glu_max, reverse=True)
        if user_glucose_avg > 0
        else 50.0
    )

    # Composite
    total = 0.5 * steps_score + 0.3 * sleep_score + 0.2 * glucose_score

    return {
        "since": since.isoformat(),
        "components": {
            "steps_avg_per_day": user_steps_avg,
            "steps_score": steps_score,
            "sleep_avg_minutes": user_sleep_avg_minutes,
            "sleep_avg_quality": user_sleep_avg_quality,
            "sleep_score": sleep_score,
            "glucose_avg": user_glucose_avg,
            "glucose_score": glucose_score,
        },
        "score": round(total, 2),
    }
