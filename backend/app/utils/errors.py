"""HTTP exception handlers."""
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import request_validation_exception_handler


async def safe_validation_error(request, exc):
    if request.url.path.startswith("/api/v1/auth/"):
        # Validation errors must not echo credentials from rejected input.
        return JSONResponse({"detail": "Input autentikasi tidak valid"}, status_code=422,
                            headers={"Cache-Control": "no-store"})
    return await request_validation_exception_handler(request, exc)

async def database_conflict(request, exc):
    return JSONResponse({"detail": "Data conflicts with database constraints"}, status_code=409,
                        headers={"Cache-Control": "no-store"})
