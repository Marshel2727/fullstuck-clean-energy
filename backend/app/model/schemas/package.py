from pydantic import Field
from app.model.schemas.common import PROPERTY, Payload

class Component(Payload):
    name: str = Field(min_length=1, max_length=255)
    specs: str
    qty: int = Field(gt=0)


class PackageInput(Payload):
    slug: str = Field(min_length=1, max_length=191, pattern=r"^[a-z0-9-]+$")
    name: str = Field(min_length=1, max_length=255)
    segment: PROPERTY
    capacityKwp: float = Field(gt=0, allow_inf_nan=False)
    tagline: str = Field(max_length=255)
    description: str
    priceFromIdr: float = Field(ge=0, allow_inf_nan=False)
    estimatedMonthlyProductionKwh: float = Field(ge=0, allow_inf_nan=False)
    estimatedMonthlySavingsIdr: float = Field(ge=0, allow_inf_nan=False)
    warrantyPanelsYears: int = Field(ge=0)
    warrantyInverterYears: int = Field(ge=0)
    warrantyWorkmanshipYears: int = Field(ge=0)
    recommendedRoofAreaSqM: float = Field(ge=0, allow_inf_nan=False)
    idealFor: str
    features: list[str] = Field(default_factory=list, max_length=100)
    components: list[Component] = Field(default_factory=list, max_length=100)
    includedServices: list[str] = Field(default_factory=list, max_length=100)
    exclusions: list[str] = Field(default_factory=list, max_length=100)
    isPopular: bool = False
