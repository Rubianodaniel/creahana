from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class UserCreateSchema(BaseModel):
    email: EmailStr
    username: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long")
        return v.strip()


class UserResponseSchema(BaseModel):
    id: Optional[int] = None
    email: str
    username: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True