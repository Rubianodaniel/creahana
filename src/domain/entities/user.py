from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class User:
    id: Optional[int] = None
    email: str = ""
    username: str = ""
    hashed_password: str = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
