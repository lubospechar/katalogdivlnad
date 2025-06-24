import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from catalog.models import Measure


class Command(BaseCommand):
    help = "Update existing Measure records with data from an Excel file"

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
            "conditions_for_implementation_cs",
            "conditions_for_implementation_en",
            "abstract_cs",
            "abstract_en",
        ]

        # Check for missing fields in the Excel file
        missing_fields = [field for field in required_fields if field not in data.columns]
        if missing_fields:
            raise CommandError(f"Missing required columns in the Excel file: {missing_fields}")

        # Iterate over rows and update Measures
        for _, row in data.iterrows():
            try:
                # Fetch the Measure based on ID
                measure = Measure.objects.get(id=row["id"])

                # Update fields only if they are not empty
                if pd.notna(row["conditions_for_implementation_cs"]):
                    measure.conditions_for_implementation_cs = row["conditions_for_implementation_cs"]
                if pd.notna(row["conditions_for_implementation_en"]):
                    measure.conditions_for_implementation_en = row["conditions_for_implementation_en"]
                if pd.notna(row["abstract_cs"]):
                    measure.abstract_cs = row["abstract_cs"]
                if pd.notna(row["abstract_en"]):
                    measure.abstract_en = row["abstract_en"]

                # Save the updated Measure instance
                measure.save()

                self.stdout.write(self.style.SUCCESS(f"Updated Measure with ID {measure.id}"))

            except Measure.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Measure with ID {row['id']} does not exist. Skipping."))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing row with ID {row['id']}: {e}"))

        self.stdout.write(self.style.SUCCESS("Update completed!"))