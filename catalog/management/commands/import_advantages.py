import pandas as pd
from django.core.management.base import BaseCommand
from catalog.models import Advantage
from django.db import IntegrityError


class Command(BaseCommand):
    help = "Import advantages from an Excel file into the database"

    def add_arguments(self, parser):
        # Argument for the path to the Excel file
        parser.add_argument(
            "file_path", type=str, help="Path to the Excel file (e.g., advantages.xlsx)"
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]

        # Attempt to load the Excel file
        try:
            self.stdout.write(self.style.SUCCESS(f"Loading file: {file_path}"))
            data = pd.read_excel(file_path, engine="openpyxl")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error loading file: {e}"))
            return

        # Ensure the DataFrame has the required columns
        required_columns = {"id", "description", "translate"}
        if not required_columns.issubset(data.columns):
            self.stderr.write(
                self.style.ERROR(
                    "The file must contain the following columns: id, description, translate"
                )
            )
            return

        imported = 0
        skipped = 0

        # Iterate through rows and import data into the database
        for _, row in data.iterrows():
            try:
                # Create or update each row in the Advantage model
                advantage, created = Advantage.objects.update_or_create(
                    id=row["id"],
                    defaults={
                        "advantage_description_cs": row["description"],
                        "advantage_description_en": row["translate"],
                    },
                )
                if created:
                    imported += 1
                else:
                    skipped += 1

            except IntegrityError as e:
                # Handle integrity errors gracefully
                self.stderr.write(
                    self.style.ERROR(
                        f"Skipping advantage with ID {row['id']} due to integrity error: {e}"
                    )
                )
                skipped += 1

        # Output summary of the import process
        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete: {imported} advantages imported, {skipped} skipped."
            )
        )