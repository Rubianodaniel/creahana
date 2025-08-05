from dataclasses import dataclass
from typing import List
from src.domain.entities.task_list import TaskList
from src.domain.entities.task import Task


@dataclass
class TaskListWithTasksDTO:
    task_list: TaskList
    tasks: List[Task]
    completion_percentage: float
    total_tasks: int
    completed_tasks: int