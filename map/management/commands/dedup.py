
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from map.models import PovIVW


class Command(BaseCommand):
    """
    Find and remove duplicate PovIV_W polygons.

    Duplicates are identified by normalized geometry.

    By default, the command performs a dry run.
    """

    help = "Find and optionally remove duplicate PovIV_W polygons."

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete duplicate records.",
        )

        parser.add_argument(
            "--force-conflicts",
            action="store_true",
            help=(
                "Also delete geometrically identical records "
                "with conflicting attributes."
            ),
        )

        parser.add_argument(
            "--show",
            type=int,
            default=20,
            help="Number of duplicate groups to display.",
        )

    @staticmethod
    def normalize_value(value):
        """
        Treat NULL and empty strings as missing values.
        """
        if isinstance(value, str):
            value = value.strip()
            return value or None

        return value

    @classmethod
    def information_score(cls, record, fields):
        """
        Prefer records containing more useful information.

        Numeric zero is not treated as informative for scoring,
        but remains a valid attribute value.
        """
        score = 0

        for field in fields:
            value = cls.normalize_value(record[field])

            if value is None:
                continue

            if isinstance(value, (int, float)) and value == 0:
                continue

            score += 1

        return score

    @classmethod
    def get_conflicting_fields(cls, records, fields):
        """
        Return fields with differing attribute values.
        """
        conflicts = []

        for field in fields:
            values = {
                cls.normalize_value(record[field])
                for record in records
            }

            if len(values) > 1:
                conflicts.append(field)

        return conflicts

    def handle(self, *args, **options):
        delete = options["delete"]
        force_conflicts = options["force_conflicts"]
        show_limit = options["show"]

        if show_limit < 0:
            raise CommandError(
                "--show must be zero or greater."
            )

        table_name = connection.ops.quote_name(
            PovIVW._meta.db_table
        )

        pk_field = PovIVW._meta.pk.attname

        attribute_fields = [
            field.name
            for field in PovIVW._meta.concrete_fields
            if not field.primary_key and field.name != "geom"
        ]

        self.stdout.write(
            "Searching for duplicate PovIV_W geometries..."
        )

        # Find identical normalized geometries in PostGIS.
        sql = f"""
            SELECT
                MD5(
                    ST_AsEWKB(
                        ST_Normalize(geom)
                    )
                ) AS geometry_hash,
                ARRAY_AGG(
                    {connection.ops.quote_name(pk_field)}
                    ORDER BY {connection.ops.quote_name(pk_field)}
                ) AS record_ids
            FROM {table_name}
            WHERE geom IS NOT NULL
            GROUP BY 1
            HAVING COUNT(*) > 1
            ORDER BY MIN({connection.ops.quote_name(pk_field)})
        """

        with connection.cursor() as cursor:
            cursor.execute(sql)
            duplicate_groups = cursor.fetchall()

        if not duplicate_groups:
            self.stdout.write(
                self.style.SUCCESS(
                    "No duplicate geometries found."
                )
            )
            return

        # Collect IDs of all potentially duplicate records.
        duplicate_ids = [
            record_id
            for _, record_ids in duplicate_groups
            for record_id in record_ids
        ]

        # Read attributes without loading large geometries.
        records = {
            record[pk_field]: record
            for record in PovIVW.objects.filter(
                pk__in=duplicate_ids
            ).values(
                pk_field,
                *attribute_fields,
            )
        }

        to_delete = []

        duplicate_count = 0
        conflict_groups = 0
        skipped_groups = 0

        for group_number, (geometry_hash, record_ids) in enumerate(
            duplicate_groups,
            start=1,
        ):
            group_records = [
                records[record_id]
                for record_id in record_ids
            ]

            duplicate_count += len(group_records) - 1

            # Identify differing attributes.
            conflicting_fields = self.get_conflicting_fields(
                group_records,
                attribute_fields,
            )

            has_conflicts = bool(conflicting_fields)

            if has_conflicts:
                conflict_groups += 1

            # Choose the most informative record.
            # In case of a tie, keep the lowest ID.
            keep_record = max(
                group_records,
                key=lambda record: (
                    self.information_score(
                        record,
                        attribute_fields,
                    ),
                    -record[pk_field],
                ),
            )

            keep_id = keep_record[pk_field]

            remove_ids = [
                record_id
                for record_id in record_ids
                if record_id != keep_id
            ]

            # Do not remove conflicting records unless
            # explicitly requested.
            can_delete = (
                not has_conflicts or force_conflicts
            )

            if can_delete:
                to_delete.extend(remove_ids)
            else:
                skipped_groups += 1

            # Display selected duplicate groups.
            if group_number <= show_limit:
                self.stdout.write("")
                self.stdout.write(
                    f"Group {group_number}:"
                )
                self.stdout.write(
                    f"  Geometry: {geometry_hash}"
                )
                self.stdout.write(
                    f"  Records: {record_ids}"
                )
                self.stdout.write(
                    f"  Keep ID: {keep_id}"
                )
                self.stdout.write(
                    f"  Duplicate IDs: {remove_ids}"
                )

                if has_conflicts:
                    self.stdout.write(
                        self.style.WARNING(
                            "  Conflicting fields: "
                            + ", ".join(conflicting_fields)
                        )
                    )

                if not can_delete:
                    self.stdout.write(
                        "  Action: SKIP (attribute conflicts)"
                    )
                else:
                    self.stdout.write(
                        "  Action: DELETE"
                        if delete
                        else "  Action: WOULD DELETE"
                    )

        self.stdout.write("")
        self.stdout.write("Summary:")
        self.stdout.write(
            f"  Duplicate groups: {len(duplicate_groups)}"
        )
        self.stdout.write(
            f"  Excess records: {duplicate_count}"
        )
        self.stdout.write(
            f"  Groups with attribute conflicts: {conflict_groups}"
        )
        self.stdout.write(
            f"  Skipped groups: {skipped_groups}"
        )
        self.stdout.write(
            f"  Records selected for deletion: {len(to_delete)}"
        )

        if not delete:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "Dry run: no records were deleted."
                )
            )
            return

        if not to_delete:
            self.stdout.write(
                self.style.WARNING(
                    "No records eligible for deletion."
                )
            )
            return

        # Delete all selected records atomically.
        with transaction.atomic():
            deleted_count, _ = (
                PovIVW.objects.filter(
                    pk__in=to_delete
                ).delete()
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {deleted_count} records."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "PovIV_W deduplication completed."
            )
        )
