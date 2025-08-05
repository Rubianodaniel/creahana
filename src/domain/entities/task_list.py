from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TaskList:
    title: str
    id: Optional[int] = None
    description: Optional[str] = None
    user_id: Optional[int] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
