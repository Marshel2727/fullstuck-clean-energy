from pathlib import Path
from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


def health() -> dict[str, str]:
    return {"status": "ok"}


def readiness(db: Session) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
        revision = db.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
        if revision != ScriptDirectory.from_config(config).get_current_head():
            raise HTTPException(status_code=503, detail="Database schema is not ready")
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database is not ready") from None
    return {"status": "ready", "schema": revision}
