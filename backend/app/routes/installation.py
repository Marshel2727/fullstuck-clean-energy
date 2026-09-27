"""HTTP endpoints for installation."""
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import FileResponse
from pydantic import ValidationError
from starlette.datastructures import UploadFile
from starlette.concurrency import run_in_threadpool
import logging
from app.utils.uploads import MAX_FILE_BYTES, validate_attachment
from app.model.schemas.installation import RequestInput, StatusInput
from app.routes.dependencies import current_user, admin_user, optional_user
from app.utils.database import get_db
from app.service import installation as service

router = APIRouter(prefix="/api/v1", tags=["operations"])

@router.get("/requests")
def requests(user=Depends(current_user), db=Depends(get_db)):
    return service.requests(user, db)


@router.post("/requests")
def create_request(data: RequestInput, user=Depends(optional_user), db=Depends(get_db)):
    return service.create_request(data, user, db)


@router.post("/requests/with-documents")
async def create_with_documents(request: Request, user=Depends(optional_user), db=Depends(get_db)):
    if not request.headers.get("content-type", "").startswith("multipart/form-data"):
        raise HTTPException(415, "Gunakan formulir unggah lampiran.")
    async with request.form(max_files=2, max_fields=1) as form:
        allowed = {"data", "roof_photo", "electricity_bill"}
        if any(key not in allowed or len(form.getlist(key)) != 1 for key in form):
            raise HTTPException(422, "Field lampiran tidak valid atau berulang.")
        raw = form.get("data")
        if not isinstance(raw, str) or len(raw.encode("utf-8")) > 65536:
            raise HTTPException(422, "Data pengajuan tidak valid.")
        try:
            data = RequestInput.model_validate_json(raw)
        except ValidationError:
            raise HTTPException(422, "Data pengajuan tidak valid. Periksa isian dan persetujuan Anda.") from None
        attachments = []
        for kind in ("roof_photo", "electricity_bill"):
            upload = form.get(kind)
            if upload is None:
                continue
            if not isinstance(upload, UploadFile):
                raise HTTPException(422, "Lampiran harus berupa file.")
            content = await upload.read(MAX_FILE_BYTES + 1)
            attachments.append(validate_attachment(kind, upload.filename, content))
        try:
            return await run_in_threadpool(service.create_request, data, user, db, attachments)
        except HTTPException:
            raise
        except Exception:
            logging.getLogger(__name__).error("request_attachment_save_failed")
            raise HTTPException(503, "Pengajuan belum dapat disimpan. Periksa koneksi atau hubungi admin sebelum mengirim ulang.") from None


@router.get("/requests/{ticket}/documents/{document_id}")
def download_document(ticket: str, document_id: int, user=Depends(current_user), db=Depends(get_db)):
    path, name, mime = service.request_document(ticket, document_id, user, db)
    return FileResponse(path, filename=name, media_type=mime, content_disposition_type="attachment",
                        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
                                 "Content-Security-Policy": "sandbox"})


@router.patch("/admin/requests/{ticket}/status")
def request_status(ticket: str, data: StatusInput, user=Depends(admin_user), db=Depends(get_db)):
    return service.request_status(ticket, data, user, db)
