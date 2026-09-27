from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

from app.routes import routers
from app.utils.config import get_settings
from app.utils.errors import database_conflict, safe_validation_error
from app.utils.middleware import api_cache_policy
from app.utils.upload_limit import UploadLimitMiddleware

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")
for router in routers:
    app.include_router(router)

app.add_exception_handler(IntegrityError, database_conflict)
app.add_exception_handler(RequestValidationError, safe_validation_error)
app.add_middleware(UploadLimitMiddleware)
app.middleware("http")(api_cache_policy)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
