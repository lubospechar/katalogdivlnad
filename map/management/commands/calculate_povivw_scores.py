
from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Measure
from map.models import PovIVW, PovIVWMeasureScore


class Command(BaseCommand):
    help = "Calculate suitability scores for all PovIVW polygons and measures."

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=2000,
            help="Number of results saved in one database batch.",
        )

    def handle(self, *args, **options):
        batch_size = options["batch_size"]

        if batch_size < 1:
            raise ValueError("Batch size must be greater than zero.")

        measures = list(
            Measure.objects.values_list(
                "id",
                "p_sklon",
                "p_landuse",
                "p_cn",
                "p_conn",
                "f_score",
            ).order_by("id")
        )

        if not measures:
            self.stdout.write(
                self.style.WARNING("No measures found.")
            )
            return

        polygon_count = PovIVW.objects.count()
        measure_count = len(measures)

        self.stdout.write(
            f"Polygons: {polygon_count}\n"
            f"Measures: {measure_count}\n"
            f"Expected results: {polygon_count * measure_count}"
        )

        batch = []
        processed_polygons = 0
        saved_results = 0
        missing_results = 0

        polygons = (
            PovIVW.objects.order_by("id")
            .values_list(
                "id",
                "mean_w_skl",
                "mean_w_lan",
                "mean_w_cn",
                "w_conn",
            )
            .iterator(chunk_size=500)
        )

        for (
            polygon_id,
            w_sklon,
            w_landuse,
            w_cn,
            w_conn,
        ) in polygons:

            polygon_weights = (
                w_sklon,
                w_landuse,
                w_cn,
                w_conn,
            )

            calculated_scores = []

            for (
                measure_id,
                p_sklon,
                p_landuse,
                p_cn,
                p_conn,
                f_score,
            ) in measures:

                measure_values = (
                    p_sklon,
                    p_landuse,
                    p_cn,
                    p_conn,
                    f_score,
                )

                if (
                    any(value is None for value in polygon_weights)
                    or any(value is None for value in measure_values)
                ):
                    score = None
                    missing_results += 1

                else:
                    score = (
                        w_sklon * float(p_sklon)
                        + w_landuse * float(p_landuse)
                        + w_cn * float(p_cn)
                        + w_conn * float(p_conn)
                    ) * f_score

                calculated_scores.append(
                    (measure_id, score)
                )

            # Normalize scores independently for each polygon.
            valid_scores = [
                score
                for _, score in calculated_scores
                if score is not None
            ]

            if valid_scores:
                min_score = min(valid_scores)
                max_score = max(valid_scores)
            else:
                min_score = None
                max_score = None

            for measure_id, score in calculated_scores:

                if score is None:
                    score_100 = None

                elif max_score == min_score:
                    score_100 = 0.0

                else:
                    score_100 = (
                        (score - min_score)
                        / (max_score - min_score)
                        * 100.0
                    )

                batch.append(
                    PovIVWMeasureScore(
                        polygon_id=polygon_id,
                        measure_id=measure_id,
                        score=score,
                        score_100=score_100,
                    )
                )

                if len(batch) >= batch_size:
                    self._save_batch(batch)
                    saved_results += len(batch)
                    batch.clear()

            processed_polygons += 1

            if processed_polygons % 1000 == 0:
                self.stdout.write(
                    f"Processed {processed_polygons}/{polygon_count} "
                    f"polygons, saved {saved_results} results."
                )

        if batch:
            self._save_batch(batch)
            saved_results += len(batch)
            batch.clear()

        self.stdout.write(
            self.style.SUCCESS(
                f"Completed.\n"
                f"Processed polygons: {processed_polygons}\n"
                f"Saved results: {saved_results}\n"
                f"Results with missing input: {missing_results}"
            )
        )

    @staticmethod
    def _save_batch(batch):
        with transaction.atomic():
            PovIVWMeasureScore.objects.bulk_create(
                batch,
                batch_size=len(batch),
                update_conflicts=True,
                update_fields=[
                    "score",
                    "score_100",
                    "calculated_at",
                ],
                unique_fields=[
                    "polygon",
                    "measure",
                ],
            )
