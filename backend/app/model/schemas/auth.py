from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator


class LoginInput(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    identifier: str = Field(min_length=1, max_length=254)
    password: SecretStr = Field(min_length=1, max_length=1024)

    @field_validator("identifier")
    @classmethod
    def clean_identifier(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Identifier is required")
        return value
