from dataclasses import dataclass
from typing import List

from src.domain.entities.task import Task
from src.domain.entities.task_list import TaskList


@dataclass
class TaskListWithTasksDTO:
    task_list: TaskList
    tasks: List[Task]
    completion_percentage: float
    total_tasks: int
    completed_tasks: int
