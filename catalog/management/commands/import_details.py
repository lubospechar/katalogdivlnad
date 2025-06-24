import pandas as pd
from django.core.management.base import BaseCommand
from catalog.models import ImpactCategory, ImpactDetail


class Command(BaseCommand):
    help = "Import Impact Details into the database from an XLSX file."

    def add_arguments(self, parser):
        # Add argument for the file path
        parser.add_argument(
            "file_path",
            type=str,
            help="Path to the XLSX file containing the impact detail data.",
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]

        try:
            # Load the data from the XLSX file
            data = pd.read_excel(file_path, dtype={"id": int, "tag_id": int, "tag_trans": str, "tag_detail": str, "detail_trans": str})
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error reading the file: {e}"))
            return

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for _, row in data.iterrows():
            # Skip rows with missing or invalid required fields
            if pd.isna(row["id"]) or pd.isna(row["tag_id"]) or pd.isna(row["tag_trans"]) or pd.isna(row["tag_detail"]) or pd.isna(row["detail_trans"]):
                self.stderr.write(self.style.WARNING(f"Skipping row with missing data: {row}"))
                skipped_count += 1
                continue

            tag_id = int(row["tag_id"])  # ID of the related ImpactCategory
            impact_detail_id = int(row["id"])

            try:
                # Retrieve the related ImpactCategory object
                impact_category = ImpactCategory.objects.get(id=tag_id)

                # Update or create the ImpactDetail entry
                detail, created = ImpactDetail.objects.update_or_create(
                    id=impact_detail_id,  # Ensures preservation of specific IDs
                    defaults={
                        "impact_category": impact_category,
                        "impact_detail_cs": row["tag_detail"],
                        "impact_detail_en": row["detail_trans"],
                    },
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Created detail: {detail}"))
                else:
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated detail: {detail}"))
            except ImpactCategory.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"ImpactCategory with id {tag_id} does not exist. Skipping row: {row}"))
                skipped_count += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error processing row {row}: {e}"))
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Import completed: {created_count} created, {updated_count} updated, {skipped_count} skipped."
        ))