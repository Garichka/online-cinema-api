import re
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, AliasPath
from app.auth.models import UserGroupEnum, GenderEnum


class UserProfileResponse(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    avatar: str | None = None
    gender: GenderEnum | None = None
    date_of_birth: datetime | None = None
    info: str | None = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="Unique user email")
    password: str = Field(
        ..., min_length=8, description="Password (minimum 8 characters)"
    )

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, value: str) -> str:
        if not re.search(r"[A-Z]", value):
            raise ValueError(
                "Password must contain at least one uppercase letter (A-Z)."
            )
        if not re.search(r"[a-z]", value):
            raise ValueError(
                "Password must contain at least one lowercase letter (a-z)."
            )
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one digit (0-9).")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_]", value):
            raise ValueError("Password must contain at least one special character.")
        return value


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime
    role: UserGroupEnum = Field(validation_alias=AliasPath("group", "name"))
    profile: UserProfileResponse | None = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    refresh_token: str
