import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from catalog.models import Measure, Group


class Command(BaseCommand):
    help = "Import measures from an Excel file and preserve IDs"

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path", type=str, help="Path to the Excel file containing the data"
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]

        # Try loading the Excel file
        try:
            self.stdout.write(self.style.NOTICE("Loading Excel file..."))
            data = pd.read_excel(file_path)
        except Exception as e:
            raise CommandError(f"Could not read file: {e}")

        # Required fields from the Excel header
        required_fields = [
            "id",
            "group_id",
            "measure_name_cs",
            "measure_name_en",
            "code",
            "description_cs",
            "description_en",
            "price_czk",
            "rice_eu",
        ]

        # Check for missing fields
        missing_fields = [field for field in required_fields if field not in data.columns]
        if missing_fields:
            raise CommandError(f"Missing required columns in the Excel file: {missing_fields}")

        # Iterate over rows and create/update Measures
        for _, row in data.iterrows():
            try:
                # Fetch the related group (ForeignKey), or skip if not found
                try:
                    group = Group.objects.get(id=row["group_id"])
                except Group.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f"Skipping row with ID {row['id']} - Group not found.")
                    )
                    continue

                # Create or update the Measure
                measure, created = Measure.objects.update_or_create(
                    id=row["id"],  # Explicitly set the ID
                    defaults={
                        "group": group,
                        "measure_name_cs": row["measure_name_cs"],
                        "measure_name_en": row["measure_name_en"],
                        "code": row["code"],
                        "description_cs": row["description_cs"],
                        "description_en": row["description_en"],
                        "price_czk": row["price_czk"],
                        "price_eu": row["price_eu"],  # Assuming 'rice_eu' is a typo for 'price_eu'
                    },
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created Measure with ID {measure.id}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Updated Measure with ID {measure.id}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing row with ID {row['id']}: {e}"))

        self.stdout.write(self.style.SUCCESS("Import completed!"))