import json
import logging

from django.contrib.gis.db.models.functions import Transform
from django.contrib.gis.db.models.functions import AsGeoJSON
from django.contrib.gis.geos import Polygon
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views import View
from django.views.generic import TemplateView

from .models import KDK

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

