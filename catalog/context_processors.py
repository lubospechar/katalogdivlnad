from django.utils import translation
from catalog.models import Group

def groups_nav(request):
    lang = translation.get_language()
    field_name = f"group_name_{lang}"

    qs = Group.objects.all()
    qs = qs.order_by(field_name)
    return {"groups": qs}

