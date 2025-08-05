import strawberry
from src.presentation.graphql.resolvers.task_list_resolvers import TaskListQuery, TaskListMutation
from src.presentation.graphql.resolvers.task_resolvers import TaskQuery, TaskMutation


@strawberry.type
class Query(TaskListQuery, TaskQuery):
    pass


@strawberry.type
class Mutation(TaskListMutation, TaskMutation):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)