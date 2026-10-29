import json
import logging

from django.contrib.gis.db.models.functions import Transform
from django.contrib.gis.db.models.functions import AsGeoJSON
from django.contrib.gis.geos import Polygon
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views import View
from django.views.generic import TemplateView

from .models import KDK

logger = logging.getLogger(__name__)

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

        return HttpResponse(status=204)
