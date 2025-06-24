from django.contrib import admin
from .models import Group, Advantage, Disadvantage


class BaseAdmin(admin.ModelAdmin):
    """
    A base admin class that includes common functionality.
    """

    # Ensure model validation is applied before saving
    def save_model(self, request, obj, form, change):
        obj.clean()
        super().save_model(request, obj, form, change)


@admin.register(Group)
class GroupAdmin(BaseAdmin):
    """
    Admin configuration for the Group model.
    """
    # Admin list view configuration
    list_display = ("group_name_cs", "group_name_en", "__str__")
    list_filter = ("group_name_cs", "group_name_en")
    search_fields = ("group_name_cs", "group_name_en")
    ordering = ("group_name_cs",)

    # Admin form configuration
    fields = ("group_name_cs", "group_name_en")


@admin.register(Advantage)
class AdvantageAdmin(BaseAdmin):
    """
    Admin configuration for the Advantage model.
    """
    # Admin list view configuration
    list_display = ("advantage_description_cs", "advantage_description_en", "__str__")
    list_filter = ("advantage_description_cs", "advantage_description_en")
    search_fields = ("advantage_description_cs", "advantage_description_en")
    ordering = ("advantage_description_cs",)

    # Admin form configuration
    fields = ("advantage_description_cs", "advantage_description_en")


@admin.register(Disadvantage)
class DisadvantageAdmin(BaseAdmin):
    """
    Admin configuration for the Disadvantage model.
    """
    # Admin list view configuration
    list_display = ("disadvantage_description_cs", "disadvantage_description_en", "__str__")
    list_filter = ("disadvantage_description_cs", "disadvantage_description_en")
    search_fields = ("disadvantage_description_cs", "disadvantage_description_en")
    ordering = ("disadvantage_description_cs",)

    # Admin form configuration
    fields = ("disadvantage_description_cs", "disadvantage_description_en")