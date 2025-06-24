from django.contrib import admin
from .models import Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    # Admin list view configuration
    list_display = ("group_name_cs", "group_name_eng", "__str__")
    list_filter = ("group_name_cs", "group_name_eng")
    search_fields = ("group_name_cs", "group_name_eng")
    ordering = ("group_name_cs",)

    # Admin form configuration
    fields = ("group_name_cs", "group_name_eng")

    # Ensure model validation is applied
    def save_model(self, request, obj, form, change):
        obj.clean()
        super().save_model(request, obj, form, change)