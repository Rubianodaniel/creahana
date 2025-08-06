from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    email: str
    username: str
    id: Optional[int] = None
    hashed_password: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if not self.email:
            raise ValueError("Email is required")
        if not self.username:
            raise ValueError("Username is required")
