from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from app.model.schemas.common import PROPERTY

STATUS = Literal["Diajukan", "Diverifikasi", "Menunggu Survei", "Penawaran", "Disetujui",
                 "Dijadwalkan", "Instalasi", "Selesai", "Dibatalkan"]

class RequestInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fullName: str = Field(min_length=1, max_length=255)
    phoneNumber: str = Field(min_length=1, max_length=32)
    email: str = Field(default="", max_length=254)
    address: str = Field(min_length=1)
    city: str = Field(min_length=1, max_length=100)
    postalCode: str | None = Field(default=None, max_length=12)
    propertyType: PROPERTY
    plnPowerVa: int = Field(gt=0)
    monthlyBillIdr: float = Field(ge=0, allow_inf_nan=False)
    roofAreaSqM: float = Field(gt=0, allow_inf_nan=False)
    selectedPackageSlug: str | None = None
    notes: str | None = None
    consent: Literal[True]


class StatusInput(BaseModel):
    status: STATUS
    note: str = Field(min_length=1)
    version: int = Field(gt=0)
