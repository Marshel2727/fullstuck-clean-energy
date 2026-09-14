from typing import Literal
from pydantic import BaseModel, ConfigDict

PROPERTY = Literal["household", "business", "industry", "school", "other"]


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid")
