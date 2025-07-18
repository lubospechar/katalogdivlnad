# Generated by Django 5.2.3 on 2025-06-24 18:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0012_alter_measure_measure_name_cs_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Example",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "example_name",
                    models.CharField(max_length=100, verbose_name="Example name"),
                ),
                (
                    "description_cs",
                    models.TextField(verbose_name="Description (Czech)"),
                ),
                (
                    "description_en",
                    models.TextField(verbose_name="Description (English)"),
                ),
                ("web", models.URLField(verbose_name="URL")),
                (
                    "location",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "in the Czech Republic"),
                            (2, "abroad"),
                            (3, "within DIVILAND"),
                        ],
                        verbose_name="Location",
                    ),
                ),
                (
                    "measure",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="catalog.measure",
                        verbose_name="Measure",
                    ),
                ),
            ],
            options={
                "verbose_name": "Implemented (example)",
                "verbose_name_plural": "Implemented (examples)",
            },
        ),
    ]
