from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class TaskList:
    title: str
    user_id: int
    id: Optional[int] = None
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
