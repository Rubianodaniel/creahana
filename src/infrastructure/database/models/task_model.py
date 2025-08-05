from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String

from src.domain.entities.task import TaskPriority, TaskStatus
from src.infrastructure.database.connection import Base
from src.infrastructure.utils.datetime_utils import utc_now


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    task_list_id = Column(Integer, ForeignKey("task_lists.id"), nullable=False, index=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    assigned_user_id = Column(Integer, nullable=True, index=True)
    due_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
