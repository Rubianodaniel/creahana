class TaskListException(Exception):
    """Base exception for task list operations"""
    pass


class TaskListHasTasksException(TaskListException):
    """Exception raised when trying to delete a task list that has associated tasks"""
    
    def __init__(self, task_list_id: int):
        self.task_list_id = task_list_id
        super().__init__(f"Cannot delete task list {task_list_id} because it contains tasks")


class TaskListNotFoundException(TaskListException):
    """Exception raised when task list is not found"""
    
    def __init__(self, task_list_id: int):
        self.task_list_id = task_list_id
        super().__init__(f"Task list {task_list_id} not found")