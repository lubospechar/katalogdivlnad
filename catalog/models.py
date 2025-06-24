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
