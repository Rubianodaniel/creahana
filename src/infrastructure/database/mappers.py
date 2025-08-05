from src.domain.entities.task import Task
from src.domain.entities.task_list import TaskList
from src.infrastructure.database.models.task_list_model import TaskListModel
from src.infrastructure.database.models.task_model import TaskModel


class TaskListMapper:
    @staticmethod
    def to_domain(model: TaskListModel) -> TaskList:
        return TaskList(
            id=model.id,
            title=model.title,
            description=model.description,
            user_id=model.user_id,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: TaskList) -> TaskListModel:
        model_data = {
            "id": entity.id,
            "title": entity.title,
            "description": entity.description,
            "user_id": entity.user_id,
            "is_active": entity.is_active,
        }

        # Only set timestamps if they exist
        if entity.created_at:
            model_data["created_at"] = entity.created_at
        if entity.updated_at:
            model_data["updated_at"] = entity.updated_at

        return TaskListModel(**model_data)


class TaskMapper:
    @staticmethod
    def to_domain(model: TaskModel) -> Task:
        return Task(
            id=model.id,
            title=model.title,
            description=model.description,
            task_list_id=model.task_list_id,
            status=model.status,
            priority=model.priority,
            assigned_user_id=model.assigned_user_id,
            due_date=model.due_date,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Task) -> TaskModel:
        return TaskModel(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            task_list_id=entity.task_list_id,
            status=entity.status,
            priority=entity.priority,
            assigned_user_id=entity.assigned_user_id,
            due_date=entity.due_date,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
