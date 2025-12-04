from django import forms
from .models import Group, Measure
from django.utils.translation import gettext_lazy as _

class SizeMultiChoiceField(forms.MultipleChoiceField):
    def __init__(self, *args, **kwargs):
        defaults = {
            "choices": Measure.Size.choices,
            "widget": forms.CheckboxSelectMultiple,
            "required": False,
            "initial": [choice[0] for choice in Measure.Size.choices],
        }
        defaults.update(kwargs)
        super().__init__(*args, **defaults)

class FilterForm(forms.Form):
    potential_scale = SizeMultiChoiceField(label=_("Application potential"))
    size_scale = SizeMultiChoiceField(label=_("Scale / extent"))
    difficulty_of_implementation = SizeMultiChoiceField(label=_("Implementation complexity"))
    quantification_scale = SizeMultiChoiceField(label=_("Impact quantification"))
    time_horizon = SizeMultiChoiceField(label=_("Impact time horizon"))

