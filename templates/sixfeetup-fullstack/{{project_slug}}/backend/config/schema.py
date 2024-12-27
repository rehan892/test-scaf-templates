import strawberry
from strawberry_django.optimizer import DjangoOptimizerExtension

from {{ project_slug }}.users.queries import UserQuery
from {{ project_slug }}.users.mutations import UserMutation


schema = strawberry.Schema(query=UserQuery, mutation=UserMutation, extensions=[
    # other extensions...
    DjangoOptimizerExtension,
])
