import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from catalog.models import Measure, Option, ImpactDetail


class Command(BaseCommand):
    help = "Update ForeignKey fields in Measure model from an Excel file"

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path", type=str, help="Path to the Excel file containing the data"
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]

        # Load the Excel file
        try:
            self.stdout.write("Loading Excel file...")
            data = pd.read_excel(file_path)
        except Exception as e:
            raise CommandError(f"Error loading file: {e}")

        # Ensure the required columns are present
        required_columns = [
            "id",
            "env",
            "potential",
            "size",
            "difficulty_of_implementation",
            "quantification",
            "time_horizon",
            "impact_details",
            "unit",
        ]
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise CommandError(f"Missing required columns: {', '.join(missing_columns)}")

        # Iterate through the records in Excel
        for _, row in data.iterrows():
            try:
                # Retrieve Measure object by ID
                measure = Measure.objects.get(id=row["id"])

                # Update ForeignKey fields only if the cell is not empty
                if pd.notna(row["env"]):
                    measure.env_id = row["env"]
                if pd.notna(row["potential"]):
                    measure.potential_id = row["potential"]
                if pd.notna(row["size"]):
                    measure.size_id = row["size"]
                if pd.notna(row["difficulty_of_implementation"]):
                    measure.difficulty_of_implementation_id = row[
                        "difficulty_of_implementation"
                    ]
                if pd.notna(row["quantification"]):
                    measure.quantification_id = row["quantification"]
                if pd.notna(row["time_horizon"]):
                    measure.time_horizon_id = row["time_horizon"]
                if pd.notna(row["impact_details"]):
                    measure.impact_details_id = row["impact_details"]
                if pd.notna(row["unit"]):
                    measure.unit_id = row["unit"]

                # Save updated instance
                measure.save()

                self.stdout.write(self.style.SUCCESS(f"Updated Measure with ID {row['id']}"))

            except Measure.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Measure with ID {row['id']} not found. Skipping."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error updating ID {row['id']}: {e}"))

        self.stdout.write(self.style.SUCCESS("Update completed successfully!"))