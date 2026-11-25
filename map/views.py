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

from django.db.models import F, Value, FloatField
from django.db.models.functions import Abs

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
    """
    Return KDK line geometries within the map bounds.

    Coordinate reference system:
    Input: EPSG:4326
    Database: EPSG:5514
    Output: EPSG:4326

    The feature limit is provided by the frontend.
    """

    DEFAULT_FEATURE_LIMIT = 20000

    def get(self, request, *args, **kwargs):
        # Parse bounding box
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

        if (
            not all(math.isfinite(v) for v in (west, south, east, north))
            or west >= east
            or south >= north
        ):
            return JsonResponse(
                {"error": "Invalid bbox"},
                status=400,
            )

        # Parse frontend feature limit
        try:
            line_limit = int(
                request.GET.get(
                    "line_limit",
                    self.DEFAULT_FEATURE_LIMIT,
                )
            )
        except (ValueError, TypeError):
            return JsonResponse(
                {"error": "Invalid line_limit"},
                status=400,
            )

        if line_limit < 1:
            return JsonResponse(
                {"error": "line_limit must be greater than zero"},
                status=400,
            )

        # Transform map bounds to database CRS
        bbox = Polygon.from_bbox(
            (west, south, east, north)
        )
        bbox.srid = 4326
        bbox.transform(5514)

        # Find intersecting lines
        queryset = KDK.objects.filter(
            geom__intersects=bbox
        )

        count = queryset.count()

        # Respect the frontend limit
        if count > line_limit:
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
                "geometry": json.loads(
                    record["geometry_json"]
                ),
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

    The feature limit is provided by the frontend.
    """

    DEFAULT_FEATURE_LIMIT = 5000

    def get(self, request, *args, **kwargs):
        # Parse bounding box
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

        if (
            not all(math.isfinite(v) for v in (west, south, east, north))
            or west >= east
            or south >= north
        ):
            return JsonResponse(
                {"error": "Invalid bbox"},
                status=400,
            )

        # Parse frontend feature limit
        try:
            polygon_limit = int(
                request.GET.get(
                    "polygon_limit",
                    self.DEFAULT_FEATURE_LIMIT,
                )
            )
        except (ValueError, TypeError):
            return JsonResponse(
                {"error": "Invalid polygon_limit"},
                status=400,
            )

        if polygon_limit < 1:
            return JsonResponse(
                {"error": "polygon_limit must be greater than zero"},
                status=400,
            )

        # Transform map bounds to database CRS
        bbox = Polygon.from_bbox(
            (west, south, east, north)
        )
        bbox.srid = 4326
        bbox.transform(5514)

        # Find intersecting polygons
        queryset = PovIVW.objects.filter(
            geom__intersects=bbox
        )

        count = queryset.count()

        # Respect the frontend limit
        if count > polygon_limit:
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
                "geometry": json.loads(
                    record["geometry_json"]
                ),
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
    Return the 10 highest-scoring measures for a selected
    PovIVW polygon.

    KDK features return an empty measure list.

    Scores are retrieved from previously calculated
    PovIVWMeasureScore records.
    """

    MEASURE_LIMIT = 10

    def get(self, request, feature_type, feature_id):

        if feature_type == "kdk":

            if not KDK.objects.filter(pk=feature_id).exists():
                return JsonResponse(
                    {"error": "KDK feature not found."},
                    status=404,
                )

            layer_name = "KDK"
            measures = []

        elif feature_type == "poviv_w":

            try:
                polygon = PovIVW.objects.get(pk=feature_id)
            except PovIVW.DoesNotExist:
                return JsonResponse(
                    {"error": "PovIV_W feature not found."},
                    status=404,
                )

            layer_name = "PovIV_W"

            scores = (
                polygon.get_measures_by_score()
                .filter(score__isnull=False)
                [:self.MEASURE_LIMIT]
            )

            measures = [
                {
                    "id": result.measure_id,
                    "name": result.measure.measure_name,
                    "url": reverse(
                        "measure-detail",
                        kwargs={"pk": result.measure_id},
                    ),
                    "score": round(result.score, 2),
                    "score_100": round(result.score_100),
                    "f": round(polygon.mean_f, 2),
                }
                for result in scores
            ]

        else:
            return JsonResponse(
                {"error": "Unsupported feature type."},
                status=400,
            )

        response = JsonResponse({
            "feature_type": feature_type,
            "feature_id": feature_id,
            "layer": layer_name,
            "feature_score": None,
            "measures": measures,
        })

        response["Cache-Control"] = "no-store"

        return response

