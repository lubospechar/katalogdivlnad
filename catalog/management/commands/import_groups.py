import pandas as pd
from django.core.management.base import BaseCommand
from catalog.models import Group


class Command(BaseCommand):
    help = "Import groups into the database from an XLSX file."

    def add_arguments(self, parser):
        # Add an argument for the file path
        parser.add_argument(
            "file_path",
            type=str,
            help="Path to the XLSX file containing the groups data."
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]

        try:
            # Load the data from the XLSX file
            data = pd.read_excel(file_path)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error reading the file: {e}"))
            return

        created_count = 0
        updated_count = 0

        for _, row in data.iterrows():
            group, created = Group.objects.update_or_create(
                id=row["id"],  # Use 'id' column for update_or_create
                defaults={
                    "group_name_cs": row["cs"],
                    "group_name_en": row["en"]
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created new group: {group}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"Updated existing group: {group}"))

        self.stdout.write(self.style.SUCCESS(
            f"Import completed: {created_count} created, {updated_count} updated."
        ))