import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from catalog.models import Example, Measure

class Command(BaseCommand):
    """
    Management command to import data from an XLSX file into
    the Example model.
    """
    help = "Import Example data from an XLSX file."

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path", type=str, help="Path to the Excel file containing the data"
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]

        # Try to load the XLSX file
        try:
            self.stdout.write("Loading Excel file...")
            data = pd.read_excel(file_path)
        except Exception as e:
            raise CommandError(f"Error loading file: {e}")

        # Check if the required columns exist in the file
        required_columns = [
            "id",
            "measure",
            "example_name",
            "description",
            "trans",
            "web",
            "location",
        ]
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise CommandError(f"Missing required columns: {', '.join(missing_columns)}")

        # Iterate through each row and create/update Example objects
        for _, row in data.iterrows():
            try:
                # Find the related Measure object
                measure_id = row["measure"]
                try:
                    measure = Measure.objects.get(id=measure_id)
                except Measure.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f"Measure with ID {measure_id} not found. Skipping row.")
                    )
                    continue

                # Update or create the Example object
                example, created = Example.objects.update_or_create(
                    id=row["id"],
                    defaults={
                        "measure": measure,
                        "example_name": row["example_name"],
                        "description_cs": row["description"],  # Assuming `description` column contains the Czech version
                        "description_en": row["trans"],  # Assuming `trans` column contains the English translation
                        "web": row["web"],
                        "location": row["location"],
                    },
                )

                # Output success message
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"Created Example with ID {example.id}.")
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"Updated Example with ID {example.id}.")
                    )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing row: {e}"))

        self.stdout.write(self.style.SUCCESS("Data import completed successfully!"))