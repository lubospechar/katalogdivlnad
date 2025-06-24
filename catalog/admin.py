from django.contrib import admin
from .models import (
    Group,
    Advantage,
    Disadvantage,
    OptionName,
    Option,
    ImpactCategory,
    ImpactDetail,
    Measure,
    Example
)


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
    list_display = (
        "disadvantage_description_cs",
        "disadvantage_description_en",
        "__str__",
    )
    list_filter = ("disadvantage_description_cs", "disadvantage_description_en")
    search_fields = ("disadvantage_description_cs", "disadvantage_description_en")
    ordering = ("disadvantage_description_cs",)

    # Admin form configuration
    fields = ("disadvantage_description_cs", "disadvantage_description_en")


@admin.register(OptionName)
class OptionNameAdmin(BaseAdmin):
    """
    Admin configuration for the OptionName model.
    """

    list_display = ("id", "option_name_cs", "option_name_en", "__str__")
    list_filter = ("option_name_cs", "option_name_en")
    search_fields = ("option_name_cs", "option_name_en")
    ordering = ("option_name_cs",)


@admin.register(Option)
class OptionAdmin(BaseAdmin):
    """
    Admin configuration for the Option model.
    """

    # Admin list view configuration
    list_display = ("id", "option_name", "option_cs", "option_en", "order", "__str__")
    list_filter = ("option_name",)
    search_fields = ("option_cs", "option_en", "description_cs", "description_en")
    ordering = ("option_name", "order")

    # Admin form configuration
    fields = (
        "option_name",
        "option_cs",
        "option_en",
        "order",
        "description_cs",
        "description_en",
    )
    readonly_fields = ("id",)


@admin.register(ImpactCategory)
class ImpactCategoryAdmin(BaseAdmin):
    """
    Admin configuration for the ImpactCategory model.
    """

    # Admin list view configuration
    list_display = (
        "id",
        "impact_category_name_cs",
        "impact_category_name_en",
        "__str__",
    )
    list_filter = ("impact_category_name_cs", "impact_category_name_en")
    search_fields = ("impact_category_name_cs", "impact_category_name_en")
    ordering = ("impact_category_name_cs",)

    # Admin form configuration
    fields = ("impact_category_name_cs", "impact_category_name_en")
    readonly_fields = ("id",)


@admin.register(ImpactDetail)
class ImpactDetailAdmin(BaseAdmin):
    """
    Admin configuration for the ImpactDetail model.
    """

    # Admin list view configuration
    list_display = (
        "id",
        "impact_category",
        "impact_detail_cs",
        "impact_detail_en",
        "__str__",
    )
    list_filter = ("impact_category",)
    search_fields = ("impact_detail_cs", "impact_detail_en")
    ordering = ("impact_category", "impact_detail_cs")

    # Admin form configuration
    fields = (
        "impact_category",
        "impact_detail_cs",
        "impact_detail_en",
    )
    readonly_fields = ("id",)


@admin.register(Measure)
class MeasureAdmin(admin.ModelAdmin):
    list_display = (
        "measure_name_cs",
        "measure_name_en",
        "code",
        "group",
        "price_czk",
        "price_eu",
    )  # Fields shown in the list view
    list_filter = (
        "group",
        "advantages",
        "disadvantages",
        "env",
        "sdg",
    )  # Filters in the sidebar
    search_fields = (
        "measure_name_cs",
        "measure_name_en",
        "code",
    )  # Fields included in the search box
    autocomplete_fields = (
        "group",
        "advantages",
        "disadvantages",
        "env",
        "env_secondary",
        "potential",
        "size",
        "difficulty_of_implementation",
        "quantification",
        "time_horizon",
        "conflict",
        "impact_details",
        "other_impacts_details",
        "sdg",
        "unit",
    )  # Enable autocompletion for foreign key and many-to-many fields
    fieldsets = [
        (
            "General Information",
            {
                "fields": [
                    "group",
                    "measure_name_cs",
                    "measure_name_en",
                    "code",
                    "abstract_cs",
                    "abstract_en",
                    "description_cs",
                    "description_en",
                ]
            },
        ),
        (
            "Environmental Details",
            {
                "fields": [
                    "env",
                    "env_secondary",
                    "env_desc",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            "Implementation Details",
            {
                "fields": [
                    "potential",
                    "size",
                    "difficulty_of_implementation",
                    "conditions_for_implementation_cs",
                    "conditions_for_implementation_en",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            "Impact Details",
            {
                "fields": [
                    "impact_details",
                    "other_impacts_details",
                    "impact_desc_cs",
                    "impact_desc_en",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            "Miscellaneous",
            {
                "fields": [
                    "price_czk",
                    "price_eu",
                    "unit",
                    "comment_cs",
                    "comment_en",
                    "sdg",
                    "interconnection",
                    "conflict",
                    "other_conflict",
                ],
                "classes": ["collapse"],
            },
        ),
    ]  # Organize fields into collapsible sections
    filter_horizontal = (
        "advantages",
        "disadvantages",
        "sdg",
        "env_secondary",
        "other_impacts_details",
        "conflict",
        "interconnection",
    )  # Many-to-many fields displayed horizontally for better usability
    ordering = ("measure_name_cs", "code")  # Default ordering in the admin


@admin.register(Example)
class ExampleAdmin(admin.ModelAdmin):
    """Admin configuration for the Example model."""

    # Fields displayed in the list view
    list_display = (
        "example_name",
        "measure",
        "location",
        "web",
    )

    # Filters available in the sidebar
    list_filter = (
        "location",
        "measure",
    )

    # Fields to include in the search functionality
    search_fields = (
        "example_name",
        "description_cs",
        "description_en",
        "web",
    )

    # Organize fields into collapsible sections in the detail view
    fieldsets = (
        (
            "General Information",
            {
                "fields": (
                    "example_name",
                    "measure",
                    "location",
                )
            },
        ),
        (
            "Descriptions",
            {
                "fields": ("description_cs", "description_en"),
                "classes": ("collapse",),  # Make this section collapsible
            },
        ),
        (
            "Web Information",
            {
                "fields": ("web",),
            },
        ),
    )

    # Preload related foreign key data to optimize database queries
    def get_queryset(self, request):
        """
        Optimize the query to preload related Measure objects (foreign key).
        """
        queryset = super().get_queryset(request)
        return queryset.select_related("measure")

    # Default ordering of records in the list view
    ordering = ("example_name",)

    # Autocomplete support for ForeignKey fields in the admin
    autocomplete_fields = ["measure"]