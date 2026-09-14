from pydantic import BaseModel, ConfigDict, Field

class DailyInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    production_kwh: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    consumption_kwh: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    grid_export_kwh: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    grid_import_kwh: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    solar_self_consumed_kwh: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    savings_idr: float | None = Field(default=None, allow_inf_nan=False)
    co2_avoided_kg: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    peak_power_kw: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    coverage_percent: float | None = Field(default=None, ge=0, le=100, allow_inf_nan=False)
    calculation_basis_json: dict
