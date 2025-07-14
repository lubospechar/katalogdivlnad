import os
import openpyxl
from django.core.management.base import BaseCommand, CommandError
from catalog.models import OptionName


class Command(BaseCommand):
    help = "Load OptionName data from an Excel file, preserving original IDs"

    def add_arguments(self, parser):
        # Argument for specifying the file path
        parser.add_argument(
            "file_path", type=str, help="Path to the .xlsx file containing OptionName data"
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]

        # Validate the file path
        if not os.path.exists(file_path):
            raise CommandError(f"The file '{file_path}' does not exist.")

        try:
            # Open the Excel workbook
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active  # Use the active sheet

            # Iterate over rows, skipping the header
            for row_index, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                choice_name_id, choice_name_cs, choice_name_en = row

                # Skip rows with missing data
                if not choice_name_cs or not choice_name_en:
                    self.stdout.write(
                        f"Skipping row {row_index} due to missing values: {row}"
                    )
                    continue

                # Check if OptionName with the given ID exists
                option_name = OptionName.objects.filter(id=choice_name_id).first()

                try:
                    if option_name:  # Update existing record
                        option_name.option_name_cs = choice_name_cs.strip()
                        option_name.option_name_en = choice_name_en.strip()
                        option_name.save(force_update=True)
                        self.stdout.write(
                            f"Row {row_index}: Updated OptionName with ID {choice_name_id}"
                        )
                    else:  # Create new record with the given ID
                        option_name = OptionName(
                            id=choice_name_id,
                            option_name_cs=choice_name_cs.strip(),
                            option_name_en=choice_name_en.strip(),
                        )
                        option_name.save(force_insert=True)
                        self.stdout.write(
                            f"Row {row_index}: Created OptionName with ID {choice_name_id}"
                        )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Row {row_index}: Error processing row - {e}")
                    )

            self.stdout.write(self.style.SUCCESS("Successfully loaded OptionName data."))

        except Exception as e:
            raise CommandError(f"Error while processing the file: {e}")