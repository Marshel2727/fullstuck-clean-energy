"""Dashboard aggregation and cache policy."""
from datetime import datetime
from sqlalchemy import select, func
from app.model.system import SolarSystem, Site
from app.model.energy import EnergyDailySummary
from app.model.device import Device, DeviceTelemetry
from app.service.system import system_for_user
from app.utils.serialization import row_data
from app.utils.cache import read_cached

def dashboard(system_id: int, user, db):
    system_for_user(db, user, system_id)  # Never bypass ownership on a Redis hit.
    def load():
        from zoneinfo import ZoneInfo
        system = db.get(SolarSystem, system_id)
        site = db.get(Site, system.site_id)
        today = datetime.now(ZoneInfo(site.timezone)).date()
        summary = db.scalar(select(EnergyDailySummary).where(
            EnergyDailySummary.system_id == system_id, EnergyDailySummary.local_date == today))
        devices = list(db.scalars(select(Device).where(Device.system_id == system_id, Device.is_active.is_(True))))
        samples = dict(db.execute(select(DeviceTelemetry.device_id, func.max(DeviceTelemetry.recorded_at))
            .join(Device, Device.id == DeviceTelemetry.device_id)
            .where(Device.system_id == system_id, DeviceTelemetry.quality_status != "invalid")
            .group_by(DeviceTelemetry.device_id)).all())
        return dict(systemId=str(system_id), localDate=today, timezone=site.timezone,
                    summary=row_data(summary) if summary else None,
                    devices=[dict(id=str(d.id), name=d.model, status=d.status,
                        lastSampleAt=samples[d.id].isoformat()+"Z" if samples.get(d.id) else None,
                        expectedIntervalSeconds=d.expected_interval_seconds) for d in devices])
    return read_cached(db, f"system-{system_id}", f"dashboard:user-{user.id}", 15, load)
