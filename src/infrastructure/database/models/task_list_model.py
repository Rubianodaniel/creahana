from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from src.infrastructure.database.connection import Base


class TaskListModel(Base):
    __tablename__ = "task_lists"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    user_id = Column(Integer, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)