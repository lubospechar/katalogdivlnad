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
        label=_("Application potential"),
        choices=Measure.Size.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    size_scale = forms.ChoiceField(
        label=_("Scale / extent"),
        choices=Measure.Size.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    difficulty_of_implementation = forms.ChoiceField(
        label=_("Implementation complexity"),
        choices=Measure.Size.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    quantification_scale = forms.ChoiceField(
        label=_("Impact quantification"),
        choices=Measure.Size.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    time_horizon = forms.ChoiceField(
        label=_("Impact time horizon"),
        choices=Measure.Size.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

