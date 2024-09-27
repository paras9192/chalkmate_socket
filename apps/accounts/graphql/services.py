from ..models import User
from ..serializer import UserSerailizerViewset

def get_user_by_id(id, many=False):
    if many: 
        user_obj = User.objects.filter(id__in=id)
    else:
        user_obj = User.objects.get(id=id)
    serializer = UserSerailizerViewset(user_obj, many=many)
    return serializer.data