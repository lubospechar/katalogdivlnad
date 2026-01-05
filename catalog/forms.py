from django import forms
from .models import Measure
from django.utils.translation import gettext_lazy as _

class SizeMultiChoiceField(forms.MultipleChoiceField):
    def __init__(self, *args, **kwargs):
        self.label_title = kwargs.pop("label_title", "")

        defaults = {
            "choices": Measure.Size.choices,
            "widget": forms.CheckboxSelectMultiple,
            "required": False,
            "initial": [choice[0] for choice in Measure.Size.choices],
        }
        defaults.update(kwargs)
        super().__init__(*args, **defaults)

class FilterForm(forms.Form):
    potential_scale = SizeMultiChoiceField(
        label=_("Application potential"),
        label_title=_("Indicates how easily and widely the measure can be applied.&#10;S = limited, specific conditions&#10;M = commonly applicable&#10;L = highly universal and widely usable"),
    )
    size_scale = SizeMultiChoiceField(
        label=_("Scale / extent"),
        label_title=_("Describes the typical spatial scale of implementation.&#10;S = local, small-scale&#10;M = medium-scale&#10;L = large-scale, landscape level")
    )
    difficulty_of_implementation = SizeMultiChoiceField(
        label=_("Implementation complexity"),
        label_title = _("Indicates technical, organisational and administrative complexity.&#10;S = simple, low effort&#10;M = moderate complexity&#10;L = complex, high implementation effort")
    )

    quantification_scale = SizeMultiChoiceField(
        label=_("Impact quantification"),
        label_title = _("Information on the extent of the measure’s impact.&#10;S = low impact&#10;M = medium impact&#10;L = very high impact")
    )

    time_horizon = SizeMultiChoiceField(
        label=_("Impact time horizon"),
        label_title=_("Indicates when the main benefits become visible.&#10;S = short-term, rapid effect&#10;M = medium-term impact&#10;L = long-term impact")
    )

