
from pathlib import Path

from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import (
    LineString,
    MultiLineString,
)
from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from django.db import transaction

from ...models import KDK


class Command(BaseCommand):
    help = "Import KDK shapefile into PostGIS."

    FIELD_MAPPING = {
        "FID_PovIV": "fid_poviv",
        "globalid": "globalid",
        "chp_4": "chp_4",
        "chp_u": "chp_u",
        "chp_d": "chp_d",
        "naz_tok": "naz_tok",
        "naz_tok_2": "naz_tok_2",
        "a_km2": "a_km2",
        "asum_km2": "asum_km2",
        "aa_km2": "aa_km2",
        "Area": "area",
        "FID_KDK": "fid_kdk",
        "arcid": "arcid",
        "grid_code": "grid_code",
        "from_node": "from_node",
        "to_node": "to_node",
        "F_KDK": "f_kdk",
        "Shape_Leng": "shape_leng",
    }

    REQUIRED_FILES = (
        "KDK.shp",
        "KDK.shx",
        "KDK.dbf",
        "KDK.prj",
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "directory",
            type=Path,
            help="Directory containing KDK shapefile files.",
        )

        parser.add_argument(
            "--batch-size",
            type=int,
            default=2000,
            help="Number of records per batch (default: 2000).",
        )

        parser.add_argument(
            "--replace",
            action="store_true",
            help="Replace all existing KDK records.",
        )

    def handle(self, *args, **options):
        directory = options["directory"].expanduser().resolve()
        batch_size = options["batch_size"]
        replace = options["replace"]

        if not directory.is_dir():
            raise CommandError(
                f"Directory does not exist: {directory}"
            )

        if batch_size < 1:
            raise CommandError(
                "Batch size must be greater than zero."
            )

        for filename in self.REQUIRED_FILES:
            filepath = directory / filename

            if not filepath.is_file():
                raise CommandError(
                    f"Required file not found: {filepath}"
                )

        shapefile_path = directory / "KDK.shp"

        self.stdout.write(
            f"Opening shapefile: {shapefile_path}"
        )

        try:
            datasource = DataSource(str(shapefile_path))
            layer = datasource[0]
        except Exception as exc:
            raise CommandError(
                f"Cannot open shapefile: {exc}"
            ) from exc

        # Validate source attributes
        available_fields = set(layer.fields)
        required_fields = set(self.FIELD_MAPPING)

        missing_fields = required_fields - available_fields

        if missing_fields:
            raise CommandError(
                "Missing shapefile fields: "
                + ", ".join(sorted(missing_fields))
            )

        # Check coordinate system
        if layer.srs is None:
            raise CommandError(
                "Shapefile has no coordinate system."
            )

        source_srid = layer.srs.srid

        if source_srid not in (5514, None):
            raise CommandError(
                f"Unexpected SRID: {source_srid}. "
                "Expected EPSG:5514."
            )

        if source_srid is None:
            self.stdout.write(
                self.style.WARNING(
                    "Source EPSG could not be identified. "
                    "Assuming EPSG:5514; verify KDK.prj."
                )
            )

        total = len(layer)

        self.stdout.write(
            f"Features in shapefile: {total:,}"
        )
        self.stdout.write(
            f"Attributes: {len(self.FIELD_MAPPING)}"
        )
        self.stdout.write(
            f"Batch size: {batch_size}"
        )

        existing_count = KDK.objects.count()

        if existing_count and not replace:
            raise CommandError(
                f"KDK table already contains "
                f"{existing_count:,} records. "
                "Use --replace to replace existing data."
            )

        imported = 0
        batch = []

        # Single transaction:
        # either the entire import succeeds,
        # or the database remains unchanged.
        with transaction.atomic():
            if replace and existing_count:
                self.stdout.write(
                    self.style.WARNING(
                        f"Deleting {existing_count:,} "
                        "existing records..."
                    )
                )

                KDK.objects.all().delete()

            for feature_number, feature in enumerate(
                layer, start=1
            ):
                try:
                    attributes = {
                        model_field: feature.get(source_field)
                        for source_field, model_field
                        in self.FIELD_MAPPING.items()
                    }

                    # Convert geometry to GEOS
                    ogr_geometry = feature.geom

                    if ogr_geometry is None:
                        raise ValueError(
                            "Feature has no geometry."
                        )

                    geometry = ogr_geometry.geos

                    if isinstance(geometry, LineString):
                        geometry = MultiLineString(geometry)

                    elif not isinstance(
                        geometry, MultiLineString
                    ):
                        raise ValueError(
                            "Unsupported geometry type: "
                            f"{geometry.geom_type}"
                        )

                    if geometry.empty:
                        raise ValueError(
                            "Feature has empty geometry."
                        )

                    geometry.srid = 5514

                    # Build Django model instance
                    obj = KDK(
                        **attributes,
                        geom=geometry,
                    )

                    batch.append(obj)

                except Exception as exc:
                    raise CommandError(
                        f"Error processing feature "
                        f"{feature_number}: {exc}"
                    ) from exc

                if len(batch) >= batch_size:
                    KDK.objects.bulk_create(
                        batch,
                        batch_size=batch_size,
                    )

                    imported += len(batch)
                    batch.clear()

                    percent = (
                        imported / total * 100
                        if total else 100
                    )

                    self.stdout.write(
                        f"Imported {imported:,}/{total:,} "
                        f"({percent:.1f}%)"
                    )

            # Insert remaining records
            if batch:
                KDK.objects.bulk_create(
                    batch,
                    batch_size=batch_size,
                )

                imported += len(batch)
                batch.clear()

        self.stdout.write(
            self.style.SUCCESS(
                f"Import completed: {imported:,} features."
            )
        )
