"""Installation submissions, status history and versioned updates."""
from datetime import datetime
from uuid import uuid4
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, or_
from app.model.installation import InstallationRequest, RequestStatusLog, RequestDocument
from app.model.file import StoredFile
from app.utils.uploads import store_attachment, private_file_path
from app.model.user import Customer
from app.model.package import SolarPackage
from app.model.schemas.installation import RequestInput, StatusInput
from app.service.package import package_data

REQUEST_FIELDS = {"fullName":"full_name", "phoneNumber":"phone_number", "email":"email",
    "address":"address", "city":"city", "postalCode":"postal_code", "propertyType":"property_type",
    "plnPowerVa":"pln_power_va", "monthlyBillIdr":"monthly_bill_idr", "roofAreaSqM":"roof_area_sqm", "notes":"notes"}

def request_data(db, row):
    result = {key: getattr(row, field) for key, field in REQUEST_FIELDS.items()}
    result.update(id=row.ticket_number, status=row.status, version=row.version,
                  createdAt=row.created_at.isoformat()+"Z", updatedAt=row.updated_at.isoformat()+"Z",
                  selectedPackageSlug=(row.package_snapshot_json or {}).get("slug"))
    result["timelineLogs"] = [dict(status=log.to_status, timestamp=log.created_at.isoformat()+"Z",
                                  note=log.note, updatedBy=log.actor_name_snapshot)
        for log in db.scalars(select(RequestStatusLog).where(RequestStatusLog.request_id == row.id)
                              .order_by(RequestStatusLog.created_at, RequestStatusLog.id))]
    result["documents"] = [dict(id=document.id, name=file.original_name, type=document.document_type,
                                 sizeBytes=file.size_bytes,
                                 downloadUrl=f"/api/v1/requests/{row.ticket_number}/documents/{document.id}")
        for document, file in db.execute(select(RequestDocument, StoredFile)
            .join(StoredFile, StoredFile.id == RequestDocument.file_id)
            .where(RequestDocument.request_id == row.id).order_by(RequestDocument.id))]
    return result


def requests(user, db):
    statement = select(InstallationRequest)
    if user.role != "admin":
        customer_ids = select(Customer.id).where(Customer.user_id == user.id, Customer.is_active.is_(True))
        statement = statement.where(or_(InstallationRequest.submitted_by_user_id == user.id,
                                        InstallationRequest.customer_id.in_(customer_ids)))
    return [request_data(db, row) for row in db.scalars(statement.order_by(InstallationRequest.created_at.desc()))]


def create_request(data: RequestInput, user, db, attachments=()):
    values = {field: getattr(data, key) for key, field in REQUEST_FIELDS.items()}
    values["email"] = values["email"] or None
    row = InstallationRequest(**values, ticket_number="REQ-"+uuid4().hex,
        submitted_by_user_id=user.id if user else None, consent_version="web-v1",
        consented_at=datetime.utcnow(), status="Diajukan")
    if data.selectedPackageSlug:
        package = db.scalar(select(SolarPackage).where(SolarPackage.slug == data.selectedPackageSlug,
                                                        SolarPackage.is_active.is_(True)))
        if not package:
            raise HTTPException(422, "Package no longer available")
        row.package_id = package.id
        row.package_snapshot_json = jsonable_encoder(package_data(db, package))
    # Never link a guest request to an account merely because its email matches.
    db.add(row)
    db.flush()
    db.add(RequestStatusLog(request_id=row.id, to_status="Diajukan", note="Pengajuan diterima",
                             actor_user_id=user.id if user else None,
                             actor_name_snapshot=user.name if user else "Pemohon"))
    saved_keys = []
    try:
        for attachment in attachments:
            key = store_attachment(attachment)
            saved_keys.append(key)
            stored = StoredFile(storage_key=key, original_name=attachment["name"],
                mime_type=attachment["mime"], size_bytes=len(attachment["content"]),
                visibility="private", uploaded_by_user_id=user.id if user else None)
            db.add(stored)
            db.flush()
            db.add(RequestDocument(request_id=row.id, file_id=stored.id,
                                   document_type=attachment["kind"], status="pending"))
        db.commit()
    except Exception:
        db.rollback()
        for key in saved_keys:
            private_file_path(key).unlink(missing_ok=True)
        raise
    return {"id": row.ticket_number}


def request_document(ticket, document_id, user, db):
    statement = select(StoredFile).join(RequestDocument, RequestDocument.file_id == StoredFile.id).join(
        InstallationRequest, InstallationRequest.id == RequestDocument.request_id).where(
        InstallationRequest.ticket_number == ticket, RequestDocument.id == document_id)
    if user.role != "admin":
        customer_ids = select(Customer.id).where(Customer.user_id == user.id, Customer.is_active.is_(True))
        statement = statement.where(or_(InstallationRequest.submitted_by_user_id == user.id,
                                        InstallationRequest.customer_id.in_(customer_ids)))
    stored = db.scalar(statement)
    if not stored:
        raise HTTPException(404, "Lampiran tidak ditemukan.")
    path = private_file_path(stored.storage_key)
    if not path.is_file():
        raise HTTPException(404, "Berkas lampiran tidak tersedia.")
    return path, stored.original_name, stored.mime_type


def request_status(ticket: str, data: StatusInput, user, db):
    row = db.scalar(select(InstallationRequest).where(InstallationRequest.ticket_number == ticket).with_for_update())
    if not row:
        raise HTTPException(404)
    if row.version != data.version:
        raise HTTPException(409, "Request changed. Refresh before saving.")
    db.add(RequestStatusLog(request_id=row.id, from_status=row.status, to_status=data.status,
        note=data.note, actor_user_id=user.id, actor_name_snapshot=user.name))
    row.status = data.status
    row.version += 1
    db.commit()
    return {"ok": True}
