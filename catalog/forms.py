from django import forms
from .models import Group, Measure
from django.utils.translation import gettext_lazy as _

class FilterForm(forms.Form):
    group = forms.ModelChoiceField(
        label=_("Group"),
        queryset=Group.objects.all(),
        required=False,
        empty_label=_("All"),
    )

    potential_scale = forms.ChoiceField(
        label=_("Potential"),
        choices=Measure.Size.choices,
        widget=forms.RadioSelect,
        required=False,
    )

