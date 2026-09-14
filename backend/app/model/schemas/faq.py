from typing import Literal
from pydantic import Field
from app.model.schemas.common import Payload

class FAQInput(Payload):
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)
    category: Literal["Umum", "Kalkulator & Biaya", "Teknis & Atap", "Proses Instalasi", "Garansi & Pemeliharaan"]
