import json
import logging
import math

from django.contrib.gis.db.models.functions import Transform
from django.contrib.gis.db.models.functions import AsGeoJSON
from django.contrib.gis.geos import Polygon
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views import View
from django.views.generic import TemplateView

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
