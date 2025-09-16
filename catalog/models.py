from django.db import models
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from typing import Final
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from markdownx.models import MarkdownxField

from django.conf import settings
from django.utils.translation import get_language
from markdownx.utils import markdownify


class TranslateMixin:
    def translate(self, base: str):
        lang = (get_language() or settings.LANGUAGE_CODE or "en").lower()
        candidates = [lang, lang.split("-")[0], getattr(settings, "LANGUAGE_CODE", "en"), "en", "cs"]
        for code in candidates:
            field = f"{base}_{code}"
            if hasattr(self, field):
                val = getattr(self, field)
                if val:
                    return val
        return ""

class Page(models.Model):
    title_cs = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content_cs = MarkdownxField()
    content_en = MarkdownxField()
    is_home = models.BooleanField(default=False, help_text="Tahle stránka je titulka")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["is_home"],
                condition=Q(is_home=True),
                name="only_one_homepage",
            )
        ]

        verbose_name = _("Page")
        verbose_name_plural = _("Pages")

    def __str__(self) -> str:
        lang: str = get_language()
        if lang == "cs":
            return self.title_cs
        return self.title_en

    # def get_absolute_url(self):
    #     return reverse("page_detail", args=[self.slug])


class Group(models.Model, TranslateMixin):
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

    @property
    def group_name(self):
        return self.translate('group_name')

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


class Advantage(models.Model, TranslateMixin):
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
        return self.translate('advantage_description')

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


class Disadvantage(models.Model, TranslateMixin):
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
        return self.translate('disadvantage_description')

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
        max_length=255, verbose_name=_("Option name (Czech)")
    )

    # Option name in the English language, used for internationalized representation
    option_name_en = models.CharField(
        max_length=255, verbose_name=_("Option name (English)")
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
        verbose_name = _("Option name")
        verbose_name_plural = _("Option names")

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
        verbose_name = _("Impact category")
        verbose_name_plural = _("Impact categories")
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


class Reference(models.Model):
    reference = models.CharField(
        verbose_name=_("Reference"),
        max_length=255,
    )
    url = models.URLField(
        verbose_name=_("URL"),
    )

    def __str__(self):
        return self.reference

    class Meta:
        verbose_name = _("Reference")
        verbose_name_plural = _("References")


class ContactPerson(models.Model):
    # First name of the contact person
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    # Last name of the contact person
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    # Expertise of the contact person
    expertise = models.CharField(max_length=255, verbose_name=_("Expertise"))
    # Email of the contact person (optional)
    email = models.EmailField(verbose_name=_("Email"), blank=True, null=True)
    # Phone number of the contact person (optional)
    phone = models.CharField(
        max_length=20, verbose_name=_("Phone"), blank=True, null=True
    )

    def __str__(self):
        # Returns a combination of first name, last name, and expertise
        return f"{self.first_name} {self.last_name} ({self.expertise})"

    class Meta:
        # Human-readable names for the Django admin interface
        verbose_name = _("Contact Person")
        verbose_name_plural = _("Contact Persons")


class Measure(models.Model, TranslateMixin):
    class Size(models.TextChoices):
        SMALL = "S", _("Small")
        MEDIUM = "M", _("Medium")
        LARGE = "L", _("Large")

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

    description_cs = MarkdownxField(
        verbose_name=_("Description (Czech)"),
    )
    description_en = MarkdownxField(
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

    potential_scale=models.CharField(
        max_length=1,
        choices=Size.choices,
        default=Size.MEDIUM,
        verbose_name=_("Application potential scale"),
    )

    size = models.ForeignKey(
        "Option",
        verbose_name=_("Scale / extent"),
        limit_choices_to={"option_name__id": 3},
        related_name="sizes",
        on_delete=models.CASCADE,
        null=True,
    )

    size_scale=models.CharField(
        max_length=1,
        choices=Size.choices,
        default=Size.MEDIUM,
        verbose_name=_("Scale / extent - scale"),
    )

    difficulty_of_implementation = models.ForeignKey(
        "Option",
        verbose_name=_("Implementation complexity"),
        limit_choices_to={"option_name__id": 4},
        related_name="difficulty_of_implementations",
        on_delete=models.CASCADE,
        null=True,
    )

    difficulty_of_implementation_scale=models.CharField(
        max_length=1,
        choices=Size.choices,
        default=Size.MEDIUM,
        verbose_name=_("Implementation complexity - scale"),
    )

    conditions_for_implementation_cs = MarkdownxField(
        verbose_name=_("Conditions of implementation (Czech)"), blank=True, null=True
    )
    conditions_for_implementation_en = MarkdownxField(
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

    quantification_scale=models.CharField(
        max_length=1,
        choices=Size.choices,
        default=Size.MEDIUM,
        verbose_name=_("Impact quantification - scale"),
    )

    time_horizon = models.ForeignKey(
        "Option",
        verbose_name=_("Impact time horizon"),
        limit_choices_to={"option_name__id": 6},
        related_name="time_horizons",
        on_delete=models.CASCADE,
        null=True,
    )

    time_horizon_scale=models.CharField(
        max_length=1,
        choices=Size.choices,
        default=Size.MEDIUM,
        verbose_name=_("Impact time horizon - scale"),
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

    other_conflict_cs = models.CharField(
        max_length=255, verbose_name=_("Other conflicts (Czech)"), blank=True, null=True
    )

    other_conflict_en = models.CharField(
        max_length=255, verbose_name=_("Other conflicts (English)"), blank=True, null=True
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

    pre_project_preparation = models.ManyToManyField(
        "Option",
        verbose_name=_("Pre-project preparation"),
        limit_choices_to={"option_name__id": 13},
        related_name="rel_ppp",
        blank=True,
    )

    price_czk_min = models.PositiveIntegerField(
        verbose_name=_("Price (CZK) - From"), default=0
    )
    price_czk_max = models.PositiveIntegerField(
        verbose_name=_("Price (CZK) - To"), default=0
    )
    price_eu_min = models.PositiveIntegerField(
        verbose_name=_("Price (Euro) - From"), default=0
    )
    price_eu_max = models.PositiveIntegerField(
        verbose_name=_("Price (Euro) - To"), default=0
    )

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

    references = models.ManyToManyField(
        "Reference",
        verbose_name=_("References"),
        related_name="measure_references",
        blank=True,
    )

    contact_person = models.ForeignKey(
        "ContactPerson",
        verbose_name=_("Contact person"),
        on_delete=models.CASCADE,
        null=True,
        related_name="contact_persons",
    )

    # title image field for Measure
    title_image = models.ImageField(
        verbose_name=_("Original Image"),
        upload_to="measure_images/originals/",  # Directory for original images
        blank=True,
        null=True,
    )

    # Processed title image field for Measure (resized)
    processed_title_image = ImageSpecField(
        source="title_image",
        processors=[ResizeToFill(800, 600)],
        format="JPEG",
        options={"quality": 90},
    )

    image_1280 = ImageSpecField(source='title_image',
        processors=[ResizeToFill(1280, 305)],
        format='JPEG', options={'quality': 85})

    image_1440 = ImageSpecField(source='title_image',
        processors=[ResizeToFill(1440, 343)],
        format='JPEG', options={'quality': 85})

    image_1920 = ImageSpecField(source='title_image',
        processors=[ResizeToFill(1920, 457)],
        format='JPEG', options={'quality': 82})

    image_2560 = ImageSpecField(source='title_image',
        processors=[ResizeToFill(2560, 610)],
        format='JPEG', options={'quality': 82})

    image_3200 = ImageSpecField(source='title_image',
        processors=[ResizeToFill(3200, 762)],
        format='JPEG', options={'quality': 80})

    image_3840 = ImageSpecField(source='title_image',
        processors=[ResizeToFill(3840, 915)],
        format='JPEG', options={'quality': 78})

    image_5000 = ImageSpecField(source='title_image',
        processors=[ResizeToFill(5000, 1191)],
        format='JPEG', options={'quality': 76})

    history_cs = MarkdownxField(
        verbose_name=_("History (Czech)"),
        blank=True,
        null=True,
    )

    history_en = MarkdownxField(
        verbose_name=_("History (English)"),
        blank=True,
        null=True,
    )

    dzes = models.ManyToManyField(
        "Dzes",
        verbose_name=_("Dzes"),
    )

    pph = models.ManyToManyField(
        "Pph",
        verbose_name=_("PPh"),
    )

    nature_restoration_law = models.ManyToManyField(
        "NatureRestorationLaw",
        verbose_name=_("Nature restoration law"),
    )

    invasion_cs = MarkdownxField(
        verbose_name=_("Invasive species issue (cs)"),
        blank=True,
        null=True,
    )

    invasion_en = MarkdownxField(
        verbose_name=_("Invasive species issue (en)"),
        blank=True,
        null=True,
    )

    def clean(self):
        # Example: Validate that descriptions in Czech and English are different
        super().clean()
        if self.description_cs and self.description_cs == self.description_en:
            raise ValidationError(
                _("The Czech and English descriptions must be different.")
            )

    def __str__(self):
        return self.measure_name

    @property
    def measure_name(self):
        return self.translate("measure_name")

    @property
    def abstract(self):
        return self.translate("abstract")

    @property
    def description(self):
        return mark_safe(markdownify(self.translate("description")))

    @property
    def conditions_for_implementation(self):
        return mark_safe(markdownify(self.translate("conditions_for_implementation")))

    @property
    def invasion(self):
        return mark_safe(markdownify(self.translate("invasion")))

    @property
    def other_conflict(self):
        return self.translate("other_conflict")

    @property
    def impact_desc(self):
        return self.translate("impact_desc")

    @property
    def history(self):
        return mark_safe(markdownify(self.translate("history")))

    @property
    def cost(self):
        lang: str = get_language()
        if lang == "cs":
            return f'{ self.price_czk_min } - {self.price_czk_max} {self.unit.option_cs}'
        return f'{ self.price_eu_min } - {self.price_eu_max} {self.unit.option_en}'

    class Meta:
        verbose_name = _("Measure")
        verbose_name_plural = _("Measures")
        constraints = [
            models.UniqueConstraint(
                fields=["group", "measure_name_cs", "measure_name_en", "code"],
                name="unique_measure_names_and_code",
            )
        ]


class MeasureImage(models.Model):
    """
    Gallery images connected to a specific Measure.
    """

    measure = models.ForeignKey(
        Measure,
        on_delete=models.CASCADE,
        related_name="gallery",
        verbose_name=_("Related Measure"),
    )
    # Original image stored by date (year/month/day)
    original_image = models.ImageField(
        verbose_name=_("Original Image"),
        upload_to="photos/%Y/%m/%d/",
        blank=False,
        null=False,
    )
    # Resized version of the image
    processed_image = ImageSpecField(
        source="original_image",
        processors=[ResizeToFill(1024, 768)],  # Resize to 1024x768
        format="JPEG",
        options={"quality": 85},  # 85% quality compression
    )
    # Optional captions
    caption_cs = models.CharField(
        max_length=255,
        verbose_name=_("Caption (Czech)"),
    )
    caption_en = models.CharField(
        max_length=255,
        verbose_name=_("Caption (English)"),
    )

    # Author of the image
    author = models.CharField(
        max_length=255,
        verbose_name=_("Author"),
    )
    # License details
    license = models.CharField(
        max_length=255,
        verbose_name=_("License"),
    )
    # Optional URL to the license information
    license_url = models.URLField(
        verbose_name=_("License URL"),
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"Image for {self.measure} - {self.caption_cs}"

    class Meta:
        verbose_name = _("Measure Image")
        verbose_name_plural = _("Measure Images")


class Example(models.Model, TranslateMixin):

    LOCATION_CHOICES = (
        (1, _("in the Czech Republic")),
        (2, _("abroad")),
        (
            3,
            _("within DIVILAND"),
        ),  # No translation provided for DIVILAND, as it seems like a name
    )

    measure = models.ForeignKey(
        Measure, verbose_name=_("Measure"), on_delete=models.CASCADE, related_name="examples"
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
        return f"{self.measure} - {self.example_name}"

    def description(self):
        return mark_safe(markdownify(self.translate("description")))

class Dzes(models.Model, TranslateMixin):
    code = models.CharField(max_length=10, verbose_name=_("Code DZES"))
    name_cs = models.CharField(verbose_name=_("Name (Czech)"), max_length=100)
    name_en = models.CharField(verbose_name=_("Name (English)"), max_length=100)
    url_cs = models.URLField(verbose_name=_("URL (Czech)"), blank=True, null=True)
    url_en = models.URLField(verbose_name=_("URL (English)"), blank=True, null=True)

    def __str__(self):
        name = self.translate("name")
        return f'{self.code} - {name}'

    def url(self):
        return self.translate('url')

    class Meta:
        verbose_name = "Dzes"  # Singular form in the admin
        verbose_name_plural = "Dzes"  # Plural form in the admin


class Pph(models.Model, TranslateMixin):
    code = models.CharField(max_length=10, verbose_name=_("Code PPH"))
    name_cs = models.CharField(verbose_name=_("Name (Czech)"), max_length=100)
    name_en = models.CharField(verbose_name=_("Name (English)"), max_length=100)
    url_cs = models.URLField(verbose_name=_("URL (Czech)"), blank=True, null=True)
    url_en = models.URLField(verbose_name=_("URL (English)"), blank=True, null=True)

    def __str__(self):
        name = self.translate("name")
        return f'{self.code} - {name}'

    def url(self):
        return self.translate('url')

    class Meta:
        verbose_name = "PPH"
        verbose_name_plural = "PPH"


class NatureRestorationLaw(models.Model, TranslateMixin):
    code = models.CharField(max_length=10, verbose_name=_("Code NPOP"))
    name_cs = models.CharField(verbose_name=_("Name (Czech)"), max_length=100)
    name_en = models.CharField(verbose_name=_("Name (English)"), max_length=100)
    url_cs = models.URLField(verbose_name=_("URL (Czech)"), blank=True, null=True)
    url_en = models.URLField(verbose_name=_("URL (English)"), blank=True, null=True)

    def __str__(self):
        name = self.translate("name")
        return f'{self.code} - {name}'

    def url(self):
        return self.translate('url')

    class Meta:
        verbose_name = _("Nature Restoration Law")
        verbose_name_plural = _("Nature Restoration Laws")
