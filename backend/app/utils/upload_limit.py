"""Bound multipart bodies before parsing, including chunked requests."""
from starlette.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from fastapi import HTTPException
from app.utils.uploads import MAX_REQUEST_BYTES
from app.utils.rate_limit import check_upload_rate


class UploadLimitMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope.get("method") != "POST" or scope.get("path") != "/api/v1/requests/with-documents":
            return await self.app(scope, receive, send)
        try:
            await run_in_threadpool(check_upload_rate)
        except HTTPException as exc:
            return await JSONResponse({"detail": exc.detail}, status_code=exc.status_code,
                                      headers={"Cache-Control": "no-store", **(exc.headers or {})})(scope, receive, send)
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > MAX_REQUEST_BYTES:
                return await JSONResponse({"detail": "Lampiran terlalu besar. Maksimal dua file, masing-masing 5 MB."},
                                          status_code=413, headers={"Cache-Control": "no-store"})(scope, receive, send)
            body.extend(chunk)
            if not message.get("more_body", False):
                break
        delivered = False

        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, replay, send)
