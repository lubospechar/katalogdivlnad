from django.db import models
from django.utils.translation import gettext_lazy as _


class Localization(models.Model):
    localization_name = models.CharField(
        max_length=30, verbose_name="Pojmenování lokalizace"
    )

    def __str__(self):
        return self.localization_name

    class Meta:
        verbose_name = "Lokalizace"
        verbose_name_plural = "Lokalizace"


class Group(models.Model):
    localization = models.ForeignKey(
        Localization, on_delete=models.CASCADE, verbose_name="Lokalizace"
    )
    group_name = models.CharField(max_length=30, verbose_name="Pojmenování skupiny")

    def __str__(self):
        return f"{self.localization}: {self.group_name}"

    class Meta:
        unique_together = ("localization", "group_name")
        verbose_name = "Skupina"
        verbose_name_plural = "Skupiny"


class Advantage(models.Model):
    description = models.CharField(
        max_length=255,
        verbose_name="Výhoda",
    )

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = "Výhoda"
        verbose_name_plural = "Výhody"


class Disadvantage(models.Model):
    description = models.CharField(
        max_length=255,
        verbose_name="Nevýhoda",
    )

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = "Nevýhoda"
        verbose_name_plural = "Nevýhody"


class ChoiceName(models.Model):
    choice_name = models.CharField(max_length=255, verbose_name="Název volby")

    class Meta:
        verbose_name = "Název volby"
        verbose_name_plural = "Názvy voleb"

    def __str__(self):
        return self.choice_name


class Choice(models.Model):
    choice_name = models.ForeignKey(
        ChoiceName, on_delete=models.CASCADE, verbose_name="Název volby"
    )
    choice = models.CharField(max_length=255, verbose_name="Volba")
    order = models.PositiveSmallIntegerField(verbose_name="Pořadí", default=0)
    description = models.TextField(verbose_name="Popis", null=True, blank=True)

    class Meta:
        verbose_name = "Volba"
        verbose_name_plural = "Volby"
        ordering = ["choice_name", "order"]

    def __str__(self):
        return f"{self.choice}"


class Tag(models.Model):
    tag_name = models.CharField(verbose_name="Kategorie", max_length=50)

    class Meta:
        verbose_name = "Kategorie dopadu změny klimatu"
        verbose_name_plural = "Kategorie dopadu změny klimatu"

    def __str__(self):
        return self.tag_name


class TagDetail(models.Model):
    tag = models.ForeignKey(
        Tag, verbose_name="Kategorie dopadu změny klimatu", on_delete=models.CASCADE
    )
    tag_detail = models.CharField(verbose_name="Specifický dopad", max_length=100)

    class Meta:
        verbose_name = "Kategorie dopadu změny klimatu (Specifický dopad)"
        verbose_name_plural = "Kategorie dopadu změny klimatu (Specifické dopady)"

    def __str__(self):
        return f"{self.tag.tag_name} - {self.tag_detail}"


class SubGroup(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="Skupina")
    subgroup_name = models.CharField(
        max_length=100, verbose_name="Pojmenování podskupiny"
    )
    code = models.CharField(max_length=10, verbose_name="Kód opatření", unique=True)
    abstract = models.CharField(max_length=255, verbose_name="Shrnutí opatření")
    description = models.TextField(
        verbose_name="Podrobný popis opatření",
        blank=False,
        null=False,
    )
    advantages = models.ManyToManyField(Advantage, verbose_name="Výhody")
    disadvantages = models.ManyToManyField(Disadvantage, verbose_name="Nevýhody")

    mix_localization = models.BooleanField(
        default=False, verbose_name="Přesah lokalizace extravilán - intravilán"
    )
    env = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        verbose_name="Složka ŽP",
        limit_choices_to={"choice_name_id": 1},
        related_name="envs",
    )
    env_secondary = models.ManyToManyField(
        Choice,
        verbose_name="Složka ŽP (přesah)",
        limit_choices_to={"choice_name_id": 1},
        related_name="envs_sec",
        blank=True,
    )

    env_desc = models.TextField(
        verbose_name="Složka ŽP (přesah) - poznánka", blank=True, null=True
    )

    potential = models.ForeignKey(
        Choice,
        verbose_name="Potenciál aplikace",
        limit_choices_to={"choice_name_id": 2},
        related_name="potentials",
        on_delete=models.CASCADE,
        null=True,
    )
    size = models.ForeignKey(
        Choice,
        verbose_name="Rozsah / velikost",
        limit_choices_to={"choice_name_id": 3},
        related_name="sizes",
        on_delete=models.CASCADE,
        null=True,
    )
    difficulty_of_implementation = models.ForeignKey(
        Choice,
        verbose_name="Náročnost realizace",
        limit_choices_to={"choice_name_id": 4},
        related_name="difficulty_of_implementations",
        on_delete=models.CASCADE,
        null=True,
    )
    conditions_for_implementation = models.TextField(
        verbose_name="Podmínky implementace", null=True, blank=False
    )

    quantification = models.ForeignKey(
        Choice,
        verbose_name="Kvantifikace dopadu",
        limit_choices_to={"choice_name_id": 5},
        related_name="quantifications",
        on_delete=models.CASCADE,
        null=True,
    )

    time_horizon = models.ForeignKey(
        Choice,
        verbose_name="Časový horizont dopadu",
        limit_choices_to={"choice_name_id": 6},
        related_name="time_horizons",
        on_delete=models.CASCADE,
        null=True,
    )

    related = models.ManyToManyField("self", blank=True, verbose_name="Návaznost")

    conflict = models.ManyToManyField(
        Choice,
        verbose_name="Střet",
        limit_choices_to={"choice_name_id": 7},
        related_name="conflicts",
        blank=True,
    )

    other_conflict = models.CharField(
        max_length=255, verbose_name="Jiné střety", null=True, blank=True
    )

    tag = models.ForeignKey(
        TagDetail,
        verbose_name="Kategorie dopadu změny klimatu",
        on_delete=models.CASCADE,
        null=True,
        related_name="tags",
    )

    other_tags = models.ManyToManyField(
        TagDetail,
        verbose_name="Vedlejší kategorie dopadu změny klimatu",
        related_name="other_tags",
        blank=True,
    )

    tag_desc = models.TextField(
        verbose_name="Kategorie dopadu změny klimatu - poznánka", blank=True, null=True
    )

    sdg = models.ManyToManyField(
        Choice,
        verbose_name="Cíle udržitelného rozvoje (SDG)",
        limit_choices_to={"choice_name_id": 10},
        related_name="sdgs",
        blank=True,
    )

    price = models.PositiveIntegerField(verbose_name="Hodnota", default=0)
    unit = models.ForeignKey(
        Choice,
        verbose_name="Jednotka",
        limit_choices_to={"choice_name_id": 11},
        related_name="units",
        on_delete=models.CASCADE,
        null=True,
    )

    comment = models.CharField(
        max_length=255, verbose_name="Komentář", null=True, blank=True
    )

    def __str__(self):
        return f"{self.group}: {self.subgroup_name, self.code}"

    class Meta:
        unique_together = ("group", "subgroup_name")
        verbose_name = "Podskupina"
        verbose_name_plural = "Podskupiny"


class Example(models.Model):

    LOCATION_CHOICES = (
        (1, "v ČR"),
        (2, "v zahraničí"),
        (3, "v rámci DIVILAND"),
    )

    subgroup = models.ForeignKey(
        SubGroup, verbose_name="Podskupina", on_delete=models.CASCADE
    )
    example_name = models.CharField(verbose_name="Název", max_length=100)
    description = models.TextField(verbose_name="Popis")
    web = models.URLField(verbose_name="Odkaz na www")
    location = models.PositiveSmallIntegerField(
        choices=LOCATION_CHOICES, verbose_name="Lokace"
    )

    class Meta:
        verbose_name = "Realizováno (příklad)"
        verbose_name_plural = "Realizováno (příklady)"

    def __str__(self):
        return f"{self.subgroup} - {self.example_name}"
