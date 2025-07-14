import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from catalog.models import Measure, Advantage, Disadvantage, Option, ImpactDetail


class Command(BaseCommand):
    help = "Import ManyToManyField data for Measure model from an Excel file"

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
            "advantages",
            "disadvantages",
            "env_secondary",
            "interconnection",
            "conflict",
            "other_impacts_details",
            "sdg",
        ]
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise CommandError(f"Missing required columns: {', '.join(missing_columns)}")

        # Iterate through the records in Excel
        for _, row in data.iterrows():
            try:
                # Retrieve Measure object by ID
                measure = Measure.objects.get(id=row["id"])

                # Update ManyToMany fields based on comma-separated IDs
                if pd.notna(row["advantages"]):
                    advantage_ids = [int(a) for a in row["advantages"].split(",") if a.strip()]
                    advantages = Advantage.objects.filter(id__in=advantage_ids)
                    measure.advantages.set(advantages)

                if pd.notna(row["disadvantages"]):
                    disadvantage_ids = [int(a) for a in row["disadvantages"].split(",") if a.strip()]
                    disadvantages = Disadvantage.objects.filter(id__in=disadvantage_ids)
                    measure.disadvantages.set(disadvantages)

                if pd.notna(row["env_secondary"]):
                    env_secondary_ids = [int(a) for a in row["env_secondary"].split(",") if a.strip()]
                    env_secondary = Option.objects.filter(id__in=env_secondary_ids)
                    measure.env_secondary.set(env_secondary)

                if pd.notna(row["interconnection"]):
                    interconnection_ids = [int(a) for a in row["interconnection"].split(",") if a.strip()]
                    interconnections = Measure.objects.filter(id__in=interconnection_ids)
                    measure.interconnection.set(interconnections)

                if pd.notna(row["conflict"]):
                    conflict_ids = [int(a) for a in row["conflict"].split(",") if a.strip()]
                    conflicts = Option.objects.filter(id__in=conflict_ids)
                    measure.conflict.set(conflicts)

                if pd.notna(row["other_impacts_details"]):
                    other_impacts_ids = [int(a) for a in row["other_impacts_details"].split(",") if a.strip()]
                    other_impacts = ImpactDetail.objects.filter(id__in=other_impacts_ids)
                    measure.other_impacts_details.set(other_impacts)

                if pd.notna(row["sdg"]):
                    sdg_ids = [int(a) for a in row["sdg"].split(",") if a.strip()]
                    sdgs = Option.objects.filter(id__in=sdg_ids)
                    measure.sdg.set(sdgs)

                # Save updated instance
                measure.save()

                self.stdout.write(self.style.SUCCESS(f"Updated Measure with ID {row['id']}"))

            except Measure.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Measure with ID {row['id']} not found. Skipping."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error updating ID {row['id']}: {e}"))

        self.stdout.write(self.style.SUCCESS("Import completed successfully!"))