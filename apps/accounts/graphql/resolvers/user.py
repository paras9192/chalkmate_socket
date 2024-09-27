# from apps.userProfile.graphql.services import get_profile_data_by_id
from ...serializer import UserSerailizerViewset
from ...models import User

def profile_id_resolver(obj, info):
    request = info.context['request']
    id = obj['profile_id']
    return get_profile_data_by_id(request, id)

def user_resolver(obj,info):
    user_obj = User.objects.filter(profile_id__id = obj['id']).last()
    serializer = UserSerailizerViewset(user_obj,many = False)
    return serializer.data
