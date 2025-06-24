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
        max_length=MAX_NAME_LENGTH,
        verbose_name=_("Group Name (Czech)"),
        unique=True
    )

    # Group name in the English language, used for internationalized representation
    group_name_eng: str = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name=_("Group Name (English)"),
        unique=True
    )

    # Returns the group name based on the active language (Czech or English)
    def __str__(self) -> str:
        lang: str = get_language()
        if lang == "cs":
            return self.group_name_cs
        return self.group_name_eng

    # Ensures that Czech and English group names are not identical
    def clean(self) -> None:
        super().clean()
        if self.group_name_cs == self.group_name_eng:
            raise ValidationError(_("The Czech and English group name must be different."))

    class Meta:
        # Human-readable names for admin interface
        verbose_name: str = _("Group")
        verbose_name_plural: str = _("Groups")

        # Ensures the combination of Czech and English group names is unique
        constraints = [
            models.UniqueConstraint(fields=["group_name_cs", "group_name_eng"], name="unique_group_names")
        ]

