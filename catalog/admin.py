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
    Example,
    MeasureImage,
    ContactPerson,
    Reference
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


@admin.register(ContactPerson)
class ContactPersonAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ContactPerson model.
    """

    # Fields displayed in the list view
    list_display = (
        "first_name",
        "last_name",
        "expertise",
        "email",
        "phone",
    )

    # Fields to include in the search functionality
    search_fields = (
        "first_name",
        "last_name",
        "expertise",
        "email",
        "phone",
    )

    # Organize fields into sections for better usability
    fieldsets = [
        (
            "Personal Information",
            {
                "fields": [
                    "first_name",
                    "last_name",
                ]
            },
        ),
        (
            "Contact Details",
            {
                "fields": [
                    "email",
                    "phone",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            "Professional Information",
            {
                "fields": [
                    "expertise",
                ],
                "classes": ["collapse"],
            },
        ),
    ]

    # Default ordering of records in the admin
    ordering = ("last_name", "first_name")

@admin.register(Measure)
class MeasureAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Measure model.
    """

    # Fields displayed in the list view
    list_display = (
        "measure_name_cs",
        "measure_name_en",
        "group",
        "code",
        "price_czk_min",
        "price_czk_max",
        "price_eu_min",
        "price_eu_max",
    )

    # Filters available in the sidebar
    list_filter = (
        "group",
        "advantages",
        "disadvantages",
        "env",
        "potential",
        "size",
        "difficulty_of_implementation",
        "quantification",
        "time_horizon",
    )

    # Fields to include in the search functionality
    search_fields = (
        "measure_name_cs",
        "measure_name_en",
        "code",
    )

    # Fields with autocomplete enabled for related models
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
        "contact_persons",
    )

    # Organize fields into sections for better usability
    fieldsets = [
        (
            "Basic Information",
            {
                "fields": [
                    "group",
                    "measure_name_cs",
                    "measure_name_en",
                    "code",
                ]
            },
        ),
        (
            "Price Details",
            {
                "fields": [
                    "price_czk_min",
                    "price_czk_max",
                    "price_eu_min",
                    "price_eu_max",
                    "unit",
                ],
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
            "Implementation and Complexity",
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
            "Impact and Categories",
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
            "Additional Information",
            {
                "fields": [
                    "sdg",
                    "interconnection",
                    "conflict",
                    "other_conflict",
                    "references",
                    "contact_persons",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            "Images and History",
            {
                "fields": [
                    "title_image",
                    "history_cs",
                    "history_en",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            "Abstracts and Descriptions",
            {
                "fields": [
                    "abstract_cs",
                    "abstract_en",
                    "description_cs",
                    "description_en",
                ],
                "classes": ["collapse"],
            },
        ),
    ]

    # Display many-to-many fields horizontally for better usability
    filter_horizontal = (
        "advantages",
        "disadvantages",
        "env_secondary",
        "other_impacts_details",
        "sdg",
        "conflict",
        "interconnection",
        "references",
    )

    # Default ordering of records in the admin
    ordering = ("measure_name_cs", "code")


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


@admin.register(MeasureImage)
class MeasureImageAdmin(admin.ModelAdmin):
    """
    Admin configuration for the MeasureImage model.
    """

    # Admin list view configuration
    list_display = (
        "measure",
        "caption_cs",
        "caption_en",
        "author",
        "license",
    )
    list_filter = ("measure", "author", "license")
    search_fields = ("caption_cs", "caption_en", "author", "license")
    ordering = ("measure", "caption_cs")

    # Admin form configuration
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "measure",
                    "original_image",
                ),
            },
        ),
        (
            "Captions",
            {
                "fields": ("caption_cs", "caption_en"),
                "classes": ("collapse",),
            },
        ),
        (
            "Author and License",
            {
                "fields": ("author", "license", "license_url"),
                "classes": ("collapse",),
            },
        ),
    )

@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Reference model.
    """

    # Admin list view configuration
    list_display = ("reference", "url")
    search_fields = ("reference", "url")
    ordering = ("reference",)

    # Admin form configuration
    fields = ("reference", "url")
