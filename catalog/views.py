from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Group, Measure, Page
from django.utils import translation
from markdownx.utils import markdownify
from django.utils.safestring import mark_safe

class Home(ListView):
    model = Group
    template_name = "home.html"
    context_object_name = "groups"

    def get_queryset(self):
        lang = translation.get_language()
        field = f"group_name_{lang}"
        return Group.objects.all().order_by(field)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        lang = translation.get_language()

        page = get_object_or_404(Page, is_home=True)

        title = getattr(page, f"title_{lang}")
        content = getattr(page, f"content_{lang}")

        context["title"] = title
        context["content"]= mark_safe(markdownify(content))
        context["language"] = lang

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
