
from django.contrib.gis import admin

from .models import KDK, PovIVW


@admin.register(KDK)
class KDKAdmin(admin.GISModelAdmin):
    """
    Administration of KDK hydrological line segments.
    """

    list_display = (
        "id",
        "naz_tok",
        "chp_4",
        "arcid",
        "fid_kdk",
        "fid_poviv",
        "f_kdk",
    )

    list_display_links = (
        "id",
        "naz_tok",
    )

    search_fields = (
        "=chp_4",
        "=naz_tok",
    )

    ordering = ("id",)
    list_per_page = 50
    show_full_result_count = False
    save_on_top = True

    fieldsets = (
        (
            "Identification",
            {
                "fields": (
                    "globalid",
                    "fid_kdk",
                    "fid_poviv",
                    "arcid",
                    "grid_code",
                )
            },
        ),
        (
            "Hydrological identifiers",
            {
                "fields": (
                    "chp_4",
                    "chp_u",
                    "chp_d",
                )
            },
        ),
        (
            "Watercourses",
            {
                "fields": (
                    "naz_tok",
                    "naz_tok_2",
                )
            },
        ),
        (
            "Network topology",
            {
                "fields": (
                    "from_node",
                    "to_node",
                )
            },
        ),
        (
            "Hydrological parameters",
            {
                "fields": (
                    "f_kdk",
                    "a_km2",
                    "asum_km2",
                    "aa_km2",
                    "area",
                    "shape_leng",
                )
            },
        ),
        (
            "Geometry",
            {
                "fields": (
                    "geom",
                )
            },
        ),
    )

    def get_queryset(self, request):
        """
        Avoid loading large geometries in the changelist.
        Geometry is loaded separately when editing a record.
        """
        queryset = super().get_queryset(request)
        return queryset.defer("geom")


@admin.register(PovIVW)
class PovIVWAdmin(admin.GISModelAdmin):
    """
    Administration of PovIV_W hydrological polygons.
    """

    list_display = (
        "id",
        "chp_4",
        "naz_tok",
        "a_km2",
        "w_conn",
        "mean_f",
        "frequency",
    )

    list_display_links = (
        "id",
        "chp_4",
    )

    search_fields = (
        "=chp_4",
        "=globalid",
    )

    ordering = ("id",)
    list_per_page = 50
    show_full_result_count = False
    save_on_top = True

    fieldsets = (
        (
            "Identification",
            {
                "fields": (
                    "globalid",
                    "chp_4",
                    "chp_u",
                    "chp_d",
                )
            },
        ),
        (
            "Watercourses",
            {
                "fields": (
                    "naz_tok",
                    "naz_tok_2",
                )
            },
        ),
        (
            "Area parameters",
            {
                "fields": (
                    "a_km2",
                    "asum_km2",
                    "aa_km2",
                    "area",
                    "shape_area",
                    "shape_leng",
                )
            },
        ),
        (
            "Hydrological parameters",
            {
                "fields": (
                    "frequency",
                    "mean_f",
                    "mean_w_skl",
                    "mean_w_lan",
                    "mean_w_cn",
                    "w_conn",
                )
            },
        ),
        (
            "Geometry",
            {
                "fields": (
                    "geom",
                )
            },
        ),
    )

    def get_queryset(self, request):
        """
        Avoid loading polygon geometries in the changelist.
        """
        queryset = super().get_queryset(request)
        return queryset.defer("geom")
