import json
import logging
import math

from django.contrib.gis.db.models.functions import Transform
from django.contrib.gis.db.models.functions import AsGeoJSON
from django.contrib.gis.geos import Polygon
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from catalog.models import Measure
from .models import KDK, PovIVW

logger = logging.getLogger("map.bounds")

class MapView(TemplateView):
    template_name = "map/map.html"


class MapBoundsView(View):

    def get(self, request, *args, **kwargs):
        try:
            west, south, east, north = map(
                float,
                request.GET["bbox"].split(",")
            )
        except (KeyError, ValueError):
            return HttpResponseBadRequest("Invalid bbox")

        bbox = Polygon.from_bbox((west, south, east, north))
        bbox.srid = 4326
        bbox.transform(5514)

        count = KDK.objects.filter(
            geom__intersects=bbox
        ).count()

        logger.info("KDK: %s features", count)

        return JsonResponse({"count": count})



class KDKLinesView(View):
    MAX_FEATURES = 15000

    def get(self, request, *args, **kwargs):
        try:
            west, south, east, north = map(
                float,
                request.GET["bbox"].split(",")
            )
        except (KeyError, ValueError):
            return JsonResponse(
                {"error": "Invalid bbox"},
                status=400,
            )

        bbox = Polygon.from_bbox((west, south, east, north))
        bbox.srid = 4326
        bbox.transform(5514)

        queryset = KDK.objects.filter(
            geom__intersects=bbox
        )

        count = queryset.count()

        if count > self.MAX_FEATURES:
            return JsonResponse({
                "type": "FeatureCollection",
                "features": [],
                "count": count,
                "too_many": True,
            })

        queryset = queryset.annotate(
            geometry_json=AsGeoJSON(
                Transform("geom", 4326),
                precision=6,
            )
        ).values(
            "id",
            "naz_tok",
            "arcid",
            "geometry_json",
        )

        features = []

        for record in queryset.iterator(chunk_size=500):
            features.append({
                "type": "Feature",
                "id": record["id"],
                "geometry": json.loads(record["geometry_json"]),
                "properties": {
                    "naz_tok": record["naz_tok"],
                    "arcid": record["arcid"],
                },
            })

        return JsonResponse({
            "type": "FeatureCollection",
            "features": features,
            "count": count,
            "too_many": False,
        })


class PovIVWPolygonsView(View):
    """
    Return PovIV_W polygon geometries within the map bounds.

    Coordinate reference system:
    Input: EPSG:4326
    Database: EPSG:5514
    Output: EPSG:4326
    """

    MAX_FEATURES = 5000

    def get(self, request, *args, **kwargs):
        try:
            west, south, east, north = map(
                float, request.GET["bbox"].split(",")
            )
        except (KeyError, ValueError):
            return JsonResponse(
                {"error": "Invalid bbox"},
                status=400,
            )

        if (
            not all(math.isfinite(v) for v in (west, south, east, north))
            or west >= east
            or south >= north
        ):
            return JsonResponse(
                {"error": "Invalid bbox"},
                status=400,
            )

        # Transform map bounds to database CRS
        bbox = Polygon.from_bbox((west, south, east, north))
        bbox.srid = 4326
        bbox.transform(5514)

        # Find intersecting polygons
        queryset = PovIVW.objects.filter(
            geom__intersects=bbox
        )

        count = queryset.count()

        # Do not return geometries above the limit
        if count > self.MAX_FEATURES:
            return JsonResponse({
                "type": "FeatureCollection",
                "features": [],
                "count": count,
                "too_many": True,
            })

        # Transform geometries to GeoJSON coordinates
        queryset = queryset.annotate(
            geometry_json=AsGeoJSON(
                Transform("geom", 4326),
                precision=9,
            )
        ).values(
            "id",
            "geometry_json",
        )

        features = []

        for record in queryset.iterator(chunk_size=100):
            features.append({
                "type": "Feature",
                "id": record["id"],
                "geometry": json.loads(record["geometry_json"]),
                "properties": {},
            })

        return JsonResponse({
            "type": "FeatureCollection",
            "features": features,
            "count": count,
            "too_many": False,
        })


class MapFeatureMeasuresView(View):
    """
    Return mock measures for a selected map feature.

    Supported feature types:
    - kdk
    - poviv_w

    The relationship between features and measures
    is currently simulated using random measures.
    """

    FEATURE_TYPES = {
        "kdk": "KDK",
        "poviv_w": "PovIV_W",
    }

    MEASURE_LIMIT = 10

    def get(self, request, feature_type, feature_id):
        layer_name = self.FEATURE_TYPES.get(feature_type)

        if layer_name is None:
            return JsonResponse(
                {"error": "Unsupported feature type."},
                status=400,
            )

        # Mock: select up to 10 random measures
        measures = Measure.objects.order_by("?")[
            :self.MEASURE_LIMIT
        ]

        result = [
            {
                "id": measure.pk,
                "name": measure.measure_name,
                "url": reverse(
                    "measure-detail",
                    kwargs={"pk": measure.pk},
                ),
            }
            for measure in measures
        ]

        response = JsonResponse({
            "feature_type": feature_type,
            "feature_id": feature_id,
            "layer": layer_name,
            "measures": result,
        })

        # Prevent caching of random mock results
        response["Cache-Control"] = "no-store"

        return response
