class TaskException(Exception):
    """Base exception for task operations"""

    pass


class InvalidTaskListException(TaskException):
    """Exception raised when trying to create a task with non-existent task list"""

    def __init__(self, task_list_id: int):
        self.task_list_id = task_list_id
        super().__init__(f"Task list {task_list_id} does not exist")


class TaskNotFoundException(TaskException):
    """Exception raised when task is not found"""

    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task {task_id} not found")


class InvalidUserException(TaskException):
    """Exception raised when trying to assign a task to non-existent user"""

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User {user_id} does not exist")
