from .user import profile_id_resolver
from ariadne import ObjectType

user = ObjectType('User')
user.set_field('profile_id', profile_id_resolver)

accounts_reolvers = [user]