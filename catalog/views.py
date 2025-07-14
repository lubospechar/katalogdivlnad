from django.views.generic import ListView, DetailView
from .models import Group, Measure

class Home(ListView):
    model = Group
    template_name = "home.html"
    context_object_name = "groups"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['measures'] = Measure.objects.all()
        return context


class GroupDetailView(DetailView):
    model = Group
    template_name = "group_detail.html"
    context_object_name = "group"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.all()
        context['measures'] = Measure.objects.filter(group=self.object)
        return context

class MeasureDetailView(DetailView):
    model = Measure
    template_name = "measure_detail.html"  # Šablona pro detail opatření
    context_object_name = "measure"



