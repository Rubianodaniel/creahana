from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from src.infrastructure.database.connection import Base
from src.infrastructure.utils.datetime_utils import utc_now


class TaskListModel(Base):
    __tablename__ = "task_lists"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
