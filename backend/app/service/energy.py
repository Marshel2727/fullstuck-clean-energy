"""Energy history and aggregate imports."""
from datetime import date, datetime
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from app.model.energy import EnergyDailySummary
from app.model.schemas.energy import DailyInput
from app.service.system import system_for_user
from app.utils.serialization import row_data
from app.utils.cache import bump_epoch, read_cached

def energy(system_id: int, start: date, end: date, user, db):
    system_for_user(db, user, system_id)
    if end < start or (end-start).days > 366:
        raise HTTPException(422, "Date range must be 0–366 days")
    return read_cached(db, f"system-{system_id}", f"energy:user-{user.id}:{start}:{end}", 60,
        lambda: [row_data(row) for row in db.scalars(select(EnergyDailySummary).where(
            EnergyDailySummary.system_id == system_id,
            EnergyDailySummary.local_date.between(start, end)).order_by(EnergyDailySummary.local_date))])


def save_daily(system_id: int, local_date: date, data: DailyInput,
               user, db):
    # Import of an already-computed aggregate, not a telemetry aggregation algorithm.
    system_for_user(db, user, system_id)
    values = data.model_dump()
    statement = insert(EnergyDailySummary).values(system_id=system_id, local_date=local_date, **values)
    db.execute(statement.on_duplicate_key_update(**values, peak_at=None, updated_at=datetime.utcnow()))
    bump_epoch(db, f"system-{system_id}")
    db.commit()
    return {"ok": True}
