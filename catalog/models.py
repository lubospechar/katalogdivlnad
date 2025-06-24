from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language
from django.core.exceptions import ValidationError
from typing import Final


class Group(models.Model):
    # Maximum length for group name fields
    MAX_NAME_LENGTH: Final[int] = 60

    # Group name in the Czech language, used for localized representation
    group_name_cs: str = models.CharField(
        max_length=MAX_NAME_LENGTH, verbose_name=_("Group Name (Czech)"), unique=True
    )

    # Group name in the English language, used for internationalized representation
    group_name_en: str = models.CharField(
        max_length=MAX_NAME_LENGTH, verbose_name=_("Group Name (English)"), unique=True
    )

    # Returns the group name based on the active language (Czech or English)
    def __str__(self) -> str:
        lang: str = get_language()
        if lang == "cs":
            return self.group_name_cs
        return self.group_name_en

    # Ensures that Czech and English group names are not identical
    def clean(self) -> None:
        super().clean()
        if self.group_name_cs == self.group_name_en:
            raise ValidationError(
                _("The Czech and English group name must be different.")
            )

    class Meta:
        # Human-readable names for the admin interface
        verbose_name: str = _("Group")
        verbose_name_plural: str = _("Groups")

        # Ensures the combination of Czech and English group names is unique
        constraints = [
            models.UniqueConstraint(
                fields=["group_name_cs", "group_name_en"], name="unique_group_names"
            )
        ]


class Advantage(models.Model):
    # Description of the advantage in Czech language, used for localized representation
    advantage_description_cs: str = models.CharField(
        max_length=255, verbose_name=_("Advantage (Czech)"), unique=True
    )

    # Description of the advantage in English language, used for internationalized representation
    advantage_description_en: str = models.CharField(
        max_length=255, verbose_name=_("Advantage (English)"), unique=True
    )

    # Returns the description based on the active language (Czech or English)
    def __str__(self) -> str:
        lang: str = get_language()
        if lang == "cs":
            return self.advantage_description_cs
        return self.advantage_description_en

    # Ensures that Czech and English descriptions are not identical
    def clean(self) -> None:
        super().clean()
        if self.advantage_description_en == self.advantage_description_en:
            raise ValidationError(
                _("The names for the Czech and English advantages must be different.")
            )

    class Meta:
        # Human-readable names for the admin interface
        verbose_name: str = _("Advantage")
        verbose_name_plural: str = _("Advantages")

        # Ensures the combination of Czech and English descriptions is unique
        constraints = [
            models.UniqueConstraint(
                fields=["advantage_description_cs", "advantage_description_en"],
                name="unique_advantage_descriptions",
            )
        ]


class Disadvantage(models.Model):
    # Description of the disadvantage in Czech language, used for localized representation
    disadvantage_description_cs: str = models.CharField(
        max_length=255, verbose_name=_("Disadvantage (Czech)"), unique=True
    )

    # Description of the disadvantage in the English language, used for internationalized representation
    disadvantage_description_en: str = models.CharField(
        max_length=255, verbose_name=_("Disadvantage (English)"), unique=True
    )

    # Returns the description based on the active language (Czech or English)
    def __str__(self) -> str:
        lang: str = get_language()
        if lang == "cs":
            return self.disadvantage_description_cs
        return self.disadvantage_description_en

    # Ensures that Czech and English descriptions are not identical
    def clean(self) -> None:
        super().clean()
        if self.disadvantage_description_cs == self.disadvantage_description_en:
            raise ValidationError(
                _(
                    "The names for the Czech and English disadvantages must be different."
                )
            )

    class Meta:
        # Human-readable names for the admin interface
        verbose_name: str = _("Disadvantage")
        verbose_name_plural: str = _("Disadvantages")

        # Ensures the combination of Czech and English descriptions is unique
        constraints = [
            models.UniqueConstraint(
                fields=["disadvantage_description_cs", "disadvantage_description_en"],
                name="unique_disadvantage_descriptions",
            )
        ]


class OptionName(models.Model):
    # Option name in the Czech language, used for localized representation
    option_name_cs = models.CharField(
        max_length=255, verbose_name="Option name (Czech)"
    )

    # Option name in the English language, used for internationalized representation
    option_name_en = models.CharField(
        max_length=255, verbose_name="Option name (English)"
    )

    # Returns the option name based on the active language (Czech or English)
    def __str__(self) -> str:
        lang: str = get_language()
        if lang == "cs":
            return self.option_name_cs
        return self.option_name_en

    # Ensures that Czech and English option names are not identical
    def clean(self) -> None:
        super().clean()
        if self.option_name_cs == self.option_name_en:
            raise ValidationError(
                _("The option names for Czech and English must be different.")
            )

    class Meta:
        # Human-readable names for the admin interface
        verbose_name = "Option name"
        verbose_name_plural = "Option names"

        # Ensures the combination of Czech and English option names is unique
        constraints = [
            models.UniqueConstraint(
                fields=["option_name_cs", "option_name_en"],
                name="unique_option_names",
            )
        ]


class Option(models.Model):
    # Reference to the OptionName model, defining the category of the option
    option_name = models.ForeignKey(
        OptionName, on_delete=models.CASCADE, verbose_name=_("Option Name")
    )

    # Option name in the Czech language, used for localized representation
    option_cs = models.CharField(max_length=255, verbose_name=_("Option (Czech)"))

    # Option name in the English language, used for internationalized representation
    option_en = models.CharField(max_length=255, verbose_name=_("Option (English)"))

    # Position of the option within the list, used for ordering options
    order = models.PositiveSmallIntegerField(verbose_name=_("Order"), default=0)

    # Description of the option in Czech, optional field
    description_cs = models.TextField(
        verbose_name=_("Description (Czech)"), null=True, blank=True
    )

    # Description of the option in English, optional field
    description_en = models.TextField(
        verbose_name=_("Description (English)"), null=True, blank=True
    )

    # Ensures that Czech and English option names and descriptions are not identical
    def clean(self) -> None:
        super().clean()
        # Validate that Czech and English option names are different
        if self.option_cs == self.option_en:
            raise ValidationError(
                _("The Czech and English option names must be different.")
            )
        # Validate that Czech and English descriptions are different if both are defined
        if (
            self.description_cs
            and self.description_en
            and self.description_cs == self.description_en
        ):
            raise ValidationError(
                _("The Czech and English descriptions must be different.")
            )

    # Returns the option name based on the active language (Czech or English)
    def __str__(self) -> str:
        lang: str = get_language()
        if lang == "cs":
            return self.option_cs
        return self.option_en

    class Meta:
        # Human-readable names for the admin interface
        verbose_name = _("Option")
        verbose_name_plural = _("Options")

        # Default sorting of options by category (OptionName) and order
        ordering = ["option_name", "order"]

        # Ensure the combination of Czech and English option names is unique
        constraints = [
            models.UniqueConstraint(
                fields=["option_name", "option_cs", "option_en"], name="unique_options"
            ),
            # Ensure the combination of Czech and English descriptions is unique
            models.UniqueConstraint(
                fields=["option_name", "description_cs", "description_en"],
                name="unique_descriptions",
            ),
        ]


class ImpactCategory(models.Model):
    impact_category_name_cs = models.CharField(
        verbose_name=_("Impact Category (Czech)"), max_length=100
    )
    impact_category_name_en = models.CharField(
        verbose_name=_("Impact Category (English)"), max_length=100
    )

    def __str__(self) -> str:
        lang: str = get_language()
        if lang == "cs":
            return self.impact_category_name_cs
        return self.impact_category_name_en

    class Meta:
        verbose_name = "Impact category"
        verbose_name_plural = "Impact categories"
        constraints = [
            models.UniqueConstraint(
                fields=["impact_category_name_cs", "impact_category_name_en"],
                name="impact_category_name_unique",
            ),
        ]


class ImpactDetail(models.Model):
    impact_category = models.ForeignKey(
        ImpactCategory, on_delete=models.CASCADE, verbose_name=_("Impact Category")
    )
    impact_detail_cs = models.CharField(
        verbose_name=_("Impact detail (Czech)"), max_length=100
    )
    impact_detail_en = models.CharField(
        verbose_name=_("Impact detail (English)"), max_length=100
    )

    def __str__(self) -> str:
        lang: str = get_language()
        if lang == "cs":
            return self.impact_detail_cs
        return self.impact_detail_en

    class Meta:
        verbose_name = _("Impact detail")
        verbose_name_plural = _("Impact details")
        constraints = [
            models.UniqueConstraint(
                fields=["impact_category", "impact_detail_cs", "impact_detail_en"],
                name="impact_detail_unique",
            ),
        ]

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language
from django.core.exceptions import ValidationError


class Measure(models.Model):
    group = models.ForeignKey(
        "Group",
        on_delete=models.CASCADE,
        verbose_name=_("Group"),
    )
    measure_name_cs = models.CharField(
        max_length=100, verbose_name=_("Measure name (Czech)")
    )
    measure_name_en = models.CharField(
        max_length=100, verbose_name=_("Measure name (English)")
    )
    code = models.CharField(max_length=10, verbose_name=_("Code"), unique=True)

    abstract_cs = models.CharField(
        max_length=255, verbose_name=_("Abstract (Czech)"), blank=True, null=True
    )
    abstract_en = models.CharField(
        max_length=255, verbose_name=_("Abstract (English)"), blank=True, null=True
    )

    description_cs = models.TextField(
        verbose_name=_("Description (Czech)"),
    )
    description_en = models.TextField(
        verbose_name=_("Description (English)"),
    )

    advantages = models.ManyToManyField(
        "Advantage", verbose_name=_("Advantages"), blank=True
    )
    disadvantages = models.ManyToManyField(
        "Disadvantage", verbose_name=_("Disadvantages"), blank=True
    )

    env = models.ForeignKey(
        "Option",
        on_delete=models.CASCADE,
        verbose_name=_("Environmental compartment"),
        limit_choices_to={"option_name__id": 1},
        related_name="envs",
        null=True,
        blank=True,
    )
    env_secondary = models.ManyToManyField(
        "Option",
        verbose_name=_("Environmental compartment (overlap)"),
        limit_choices_to={"option_name__id": 1},
        related_name="envs_sec",
        blank=True,
    )

    env_desc = models.TextField(
        verbose_name=_("Environmental compartment (overlap) - note"),
        blank=True,
        null=True,
    )

    potential = models.ForeignKey(
        "Option",
        verbose_name=_("Application potential"),
        limit_choices_to={"option_name__id": 2},
        related_name="potentials",
        on_delete=models.CASCADE,
        null=True,
    )
    size = models.ForeignKey(
        "Option",
        verbose_name=_("Scale / extent"),
        limit_choices_to={"option_name__id": 3},
        related_name="sizes",
        on_delete=models.CASCADE,
        null=True,
    )
    difficulty_of_implementation = models.ForeignKey(
        "Option",
        verbose_name=_("Implementation complexity"),
        limit_choices_to={"option_name__id": 4},
        related_name="difficulty_of_implementations",
        on_delete=models.CASCADE,
        null=True,
    )
    conditions_for_implementation_cs = models.TextField(
        verbose_name=_("Conditions of implementation (Czech)"), blank=True, null=True
    )
    conditions_for_implementation_en = models.TextField(
        verbose_name=_("Conditions of implementation (English)"), blank=True, null=True
    )

    quantification = models.ForeignKey(
        "Option",
        verbose_name=_("Impact quantification"),
        limit_choices_to={"option_name__id": 5},
        related_name="rel_quantification",
        on_delete=models.CASCADE,
        null=True,
    )
    time_horizon = models.ForeignKey(
        "Option",
        verbose_name=_("Impact time horizon"),
        limit_choices_to={"option_name__id": 6},
        related_name="time_horizons",
        on_delete=models.CASCADE,
        null=True,
    )

    interconnection = models.ManyToManyField(
        "self", blank=True, verbose_name=_("Interconnection")
    )

    conflict = models.ManyToManyField(
        "Option",
        verbose_name=_("Conflicts"),
        limit_choices_to={"option_name__id": 7},
        related_name="conflicts",
        blank=True,
    )

    other_conflict = models.CharField(
        max_length=255, verbose_name=_("Other conflicts"), blank=True, null=True
    )

    impact_details = models.ForeignKey(
        "ImpactDetail",
        verbose_name=_("Impact categories of climate change"),
        on_delete=models.CASCADE,
        null=True,
        related_name="impacts",
        blank=True,
    )
    other_impacts_details = models.ManyToManyField(
        "ImpactDetail",
        verbose_name=_("Secondary impact categories of climate change"),
        related_name="other_impacts",
        blank=True,
    )
    impact_desc_cs = models.TextField(
        verbose_name=_("Impact categories of climate change - note (Czech)"),
        blank=True,
        null=True,
    )
    impact_desc_en = models.TextField(
        verbose_name=_("Impact categories of climate change - note (English)"),
        blank=True,
        null=True,
    )

    sdg = models.ManyToManyField(
        "Option",
        verbose_name=_("Sustainable Development Goals (SDG)"),
        limit_choices_to={"option_name__id": 10},
        related_name="rel_sdg",
        blank=True,
    )

    price_czk = models.PositiveIntegerField(verbose_name=_("Price (CZK)"), default=0)
    price_eu = models.PositiveIntegerField(verbose_name=_("Price (Euro)"), default=0)

    unit = models.ForeignKey(
        "Option",
        verbose_name=_("Unit"),
        limit_choices_to={"option_name__id": 11},
        related_name="units",
        on_delete=models.CASCADE,
        null=True,
    )

    comment_cs = models.CharField(
        max_length=255, verbose_name=_("Comment (cs)"), blank=True, null=True
    )
    comment_en = models.CharField(
        max_length=255, verbose_name=_("Comment (en)"), blank=True, null=True
    )

    def clean(self):
        # Example: Validate that descriptions in Czech and English are different
        super().clean()
        if self.description_cs and self.description_cs == self.description_en:
            raise ValidationError(
                _("The Czech and English descriptions must be different.")
            )

    def __str__(self):
        lang = get_language()
        if lang == "cs":
            return self.measure_name_cs
        return self.measure_name_en

    class Meta:
        verbose_name = _("Measure")
        verbose_name_plural = _("Measures")
        constraints = [
            models.UniqueConstraint(
                fields=["group", "measure_name_cs", "measure_name_en", "code"],
                name="unique_measure_names_and_code",
            )
        ]

class Example(models.Model):

    LOCATION_CHOICES = (
        (1, _("in the Czech Republic")),
        (2, _("abroad")),
        (3, _("within DIVILAND")),  # No translation provided for DIVILAND, as it seems like a name
    )

    measure = models.ForeignKey(
        Measure, verbose_name=_("Measure"), on_delete=models.CASCADE
    )
    example_name = models.CharField(verbose_name=_("Example name"), max_length=100)
    description_cs = models.TextField(verbose_name=_("Description (Czech)"))
    description_en = models.TextField(verbose_name=_("Description (English)"))
    web = models.URLField(verbose_name=_("URL"))
    location = models.PositiveSmallIntegerField(
        choices=LOCATION_CHOICES, verbose_name=_("Location")
    )

    class Meta:
        verbose_name = _("Implemented (example)")
        verbose_name_plural = _("Implemented (examples)")

    def __str__(self):
        return f"{self.subgroup} - {self.example_name}"
