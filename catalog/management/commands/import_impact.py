import pandas as pd
from django.core.management.base import BaseCommand
from catalog.models import ImpactCategory


class Command(BaseCommand):
    help = "Import Impact Categories into the database from an XLSX file."

    def add_arguments(self, parser):
        # Add argument for the file path
        parser.add_argument(
            "file_path",
            type=str,
            help="Path to the XLSX file containing the impact category data.",
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]

        try:
            # Load the data from the XLSX file
            data = pd.read_excel(file_path, dtype={"tag_id": int, "tag_name": str, "tag_trans": str})
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error reading the file: {e}"))
            return

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for _, row in data.iterrows():
            # Skip rows with missing required fields
            if pd.isna(row["tag_id"]) or pd.isna(row["tag_name"]) or pd.isna(row["tag_trans"]):
                self.stderr.write(self.style.WARNING(f"Skipping row with missing data: {row}"))
                skipped_count += 1
                continue

            # Update or create the ImpactCategory entry
            tag_id = int(row["tag_id"])
            try:
                category, created = ImpactCategory.objects.update_or_create(
                    id=tag_id,  # Use tag_id to preserve custom IDs
                    defaults={
                        "impact_category_name_cs": row["tag_name"],
                        "impact_category_name_en": row["tag_trans"],
                    },
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Created category: {category}"))
                else:
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated category: {category}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error processing row {row}: {e}"))
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Import completed: {created_count} created, {updated_count} updated, {skipped_count} skipped."
        ))