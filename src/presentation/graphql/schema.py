import strawberry

from src.presentation.graphql.resolvers.task_list_resolvers import (
    TaskListMutation,
    TaskListQuery,
)
from src.presentation.graphql.resolvers.task_resolvers import TaskMutation, TaskQuery


@strawberry.type
class Query(TaskListQuery, TaskQuery):
    pass


@strawberry.type
class Mutation(TaskListMutation, TaskMutation):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
