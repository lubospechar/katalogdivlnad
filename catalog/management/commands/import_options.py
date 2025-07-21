import os
import openpyxl
from django.core.management.base import BaseCommand, CommandError
from catalog.models import Option, OptionName


class Command(BaseCommand):
    help = "Import options into the database from an Excel file, preserving IDs"

    def add_arguments(self, parser):
        # Add argument for the file path
        parser.add_argument(
            "file_path",
            type=str,
            help="The file path to the Excel file to import options from",
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]

        # Check if file exists
        if not os.path.exists(file_path):
            raise CommandError(f"The file '{file_path}' does not exist.")

        # Load the Excel workbook
        try:
            workbook = openpyxl.load_workbook(file_path)
            sheet = workbook.active
        except Exception as e:
            raise CommandError(f"Error loading the Excel file: {e}")

        # Iterate over rows in the Excel file
        for row_index, row in enumerate(sheet.iter_rows(min_row=2), start=2):  # Skip header
            try:
                # Parse row data
                id = row[0].value  # `id`
                choice_name_id = row[1].value  # `choice_name_id`
                choice = row[2].value  # `choice`
                choice_trans = row[3].value  # `choice_trans`
                order = row[4].value or 0  # `order`, default to 0 if not provided
                description = row[5].value  # `description`
                description_trans = row[6].value  # `description_trans`

                # Fetch the associated OptionName instance
                try:
                    option_name = OptionName.objects.get(id=choice_name_id)
                except OptionName.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Row {row_index}: Skipping because OptionName with ID {choice_name_id} does not exist."
                        )
                    )
                    continue

                # Check if Option with the given ID exists
                option = Option.objects.filter(id=id).first()

                if option:  # Update existing record
                    option.option_name = option_name
                    option.option_cs = choice
                    option.option_en = choice_trans
                    option.order = order
                    option.description_cs = description
                    option.description_en = description_trans
                    option.save(force_update=True)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Row {row_index}: Updated option with ID {id}"
                        )
                    )
                else:  # Create new record with specified ID
                    option = Option(
                        id=id,
                        option_name=option_name,
                        option_cs=choice,
                        option_en=choice_trans,
                        order=order,
                        description_cs=description,
                        description_en=description_trans,
                    )
                    option.save(force_insert=True)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Row {row_index}: Created option with ID {id}"
                        )
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Row {row_index}: Error processing row - {e}")
                )

        self.stdout.write(self.style.SUCCESS("Import completed successfully."))