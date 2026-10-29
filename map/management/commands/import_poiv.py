
from pathlib import Path

from django.contrib.gis.gdal import DataSource
from django.contrib.gis.gdal.error import GDALException
from django.contrib.gis.geos import MultiPolygon, Polygon
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ...models import PovIVW


FIELD_MAPPING = {
    "globalid": "globalid",
    "chp_4": "chp_4",
    "chp_u": "chp_u",
    "chp_d": "chp_d",
    "naz_tok": "naz_tok",
    "naz_tok_2": "naz_tok_2",
    "a_km2": "a_km2",
    "asum_km2": "asum_km2",
    "aa_km2": "aa_km2",
    "area": "Area",
    "frequency": "FREQUENCY",
    "mean_f": "MEAN_F",
    "mean_w_skl": "MEAN_W_skl",
    "mean_w_lan": "MEAN_W_lan",
    "mean_w_cn": "MEAN_W_CN",
    "w_conn": "W_conn",
    "shape_leng": "Shape_Leng",
    "shape_area": "Shape_Area",
}


class Command(BaseCommand):
    help = "Import PovIV_W shapefile into PostGIS."

    def add_arguments(self, parser):
        parser.add_argument(
            "source",
            type=Path,
            help="Path to PovIV_W shapefile or its basename.",
        )

        parser.add_argument(
            "--batch-size",
            type=int,
            default=200,
            help="Number of features per database batch.",
        )

        parser.add_argument(
            "--replace",
            action="store_true",
            help="Delete existing PovIVW records before importing.",
        )

    def handle(self, *args, **options):
        source = options["source"]
        batch_size = options["batch_size"]
        replace = options["replace"]

        if batch_size < 1:
            raise CommandError(
                "Batch size must be greater than zero."
            )

        if source.suffix.lower() == ".shp":
            shp_path = source
        else:
            shp_path = source.with_suffix(".shp")

        # Validate required shapefile components
        required_extensions = [
            ".shp",
            ".shx",
            ".dbf",
            ".prj",
        ]

        for extension in required_extensions:
            file_path = shp_path.with_suffix(extension)

            if not file_path.is_file():
                raise CommandError(
                    f"Required file not found: {file_path}"
                )

        # Open shapefile
        try:
            data_source = DataSource(str(shp_path))
        except (GDALException, OSError) as error:
            raise CommandError(
                f"Cannot open shapefile: {error}"
            ) from error

        layer = data_source[0]

        # Validate coordinate reference system
        if layer.srs is None or layer.srs.srid != 5514:
            raise CommandError(
                "Shapefile must use EPSG:5514 (S-JTSK)."
            )

        # Validate attribute fields
        missing_fields = (
            set(FIELD_MAPPING.values()) - set(layer.fields)
        )

        if missing_fields:
            raise CommandError(
                "Missing shapefile fields: "
                + ", ".join(sorted(missing_fields))
            )

        # Prevent accidental duplicate imports
        if PovIVW.objects.exists() and not replace:
            raise CommandError(
                "PovIVW table already contains data. "
                "Use --replace to overwrite existing records."
            )

        total = len(layer)
        imported = 0
        last_reported = 0
        batch = []

        self.stdout.write(
            f"Importing {total:,} features from {shp_path}"
        )

        with transaction.atomic():
            if replace:
                deleted, _ = PovIVW.objects.all().delete()

                self.stdout.write(
                    f"Deleted {deleted:,} existing records."
                )

            for index, feature in enumerate(layer, start=1):
                # Read geometry
                geometry = feature.geom.geos

                if isinstance(geometry, Polygon):
                    geometry = MultiPolygon(geometry)

                if not isinstance(geometry, MultiPolygon):
                    raise CommandError(
                        f"Unsupported geometry at feature {index}: "
                        f"{geometry.geom_type}"
                    )

                if geometry.empty:
                    raise CommandError(
                        f"Empty geometry at feature {index}."
                    )

                geometry.srid = 5514

                # Read all original attributes
                attributes = {
                    model_field: feature.get(source_field)
                    for model_field, source_field
                    in FIELD_MAPPING.items()
                }

                batch.append(
                    PovIVW(
                        **attributes,
                        geom=geometry,
                    )
                )

                if len(batch) >= batch_size:
                    PovIVW.objects.bulk_create(
                        batch,
                        batch_size=batch_size,
                    )

                    imported += len(batch)
                    batch.clear()

                    if imported - last_reported >= 1000:
                        self.stdout.write(
                            f"Imported {imported:,} / {total:,}"
                        )
                        last_reported = imported

            # Insert remaining features
            if batch:
                PovIVW.objects.bulk_create(
                    batch,
                    batch_size=batch_size,
                )

                imported += len(batch)
                batch.clear()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {imported:,} features."
            )
        )
