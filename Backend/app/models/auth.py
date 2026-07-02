from pydantic import BaseModel, ConfigDict, Field, field_validator


class SignupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field(default=None, max_length=200)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized_value = value.strip()
        return normalized_value or None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized_value = value.strip().casefold()
        if "@" not in normalized_value or normalized_value.startswith("@") or normalized_value.endswith("@"):
            raise ValueError("A valid email address is required.")
        return normalized_value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        normalized_value = value.strip()
        if len(normalized_value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return normalized_value


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized_value = value.strip().casefold()
        if "@" not in normalized_value or normalized_value.startswith("@") or normalized_value.endswith("@"):
            raise ValueError("A valid email address is required.")
        return normalized_value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("Password cannot be empty.")
        return normalized_value


class UserResponse(BaseModel):
    id: int
    full_name: str = ""
    email: str
    created_at: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse