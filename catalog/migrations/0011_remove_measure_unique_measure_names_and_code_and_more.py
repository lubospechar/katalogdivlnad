# Generated by Django 5.2.3 on 2025-06-24 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0010_alter_measure_options_alter_measure_advantages_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="measure",
            name="unique_measure_names_and_code",
        ),
        migrations.AddConstraint(
            model_name="measure",
            constraint=models.UniqueConstraint(
                fields=("group", "measure_name_cs", "measure_name_en", "code"),
                name="unique_measure_names_and_code",
            ),
        ),
    ]
