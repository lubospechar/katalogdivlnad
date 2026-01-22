from django.http.response import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.http import http_date
from django.utils.timezone import now
from django.views.generic import ListView, DetailView
from django.views.generic.base import View

from .models import Group, Measure, Page, ContactPerson, BoxName
from django.utils import translation
from markdownx.utils import markdownify
from django.utils.safestring import mark_safe
from .forms import FilterForm

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

class MeasuresListByGroupView(ListView):
    model = Measure
    template_name = "measure_list.html"
    context_object_name = "measures"

    def get_queryset(self):
        lang = translation.get_language()
        qs = super().get_queryset().prefetch_related("groups")
        group_id = self.kwargs.get("pk")
        if group_id:
            qs = qs.filter(groups__id=group_id)
        return qs.order_by(f"measure_name_{lang}")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group_id = self.kwargs.get("pk")
        context["selected_group"] = None
        context["filter_form"] = FilterForm(self.request.GET or None)

        if group_id:
            context["selected_group"] = get_object_or_404(Group, pk=group_id)
        return context


class MeasuresListByGroupAjaxView(MeasuresListByGroupView):
    template_name = "measure_list_partial.html"

    def get_queryset(self):
        qs = super().get_queryset()
        form = FilterForm(self.request.GET or None)

        if not form.is_valid():
            return qs

        data = form.cleaned_data

        potential = data.get("potential_scale") or []
        size = data.get("size_scale") or []
        diff = data.get("difficulty_of_implementation") or []
        quant = data.get("quantification_scale") or []
        time = data.get("time_horizon") or []


        if potential:
            qs = qs.filter(potential_scale__in=potential)

        if size:
            qs = qs.filter(size_scale__in=size)

        if diff:
            qs = qs.filter(difficulty_of_implementation_scale__in=diff)

        if quant:
            qs = qs.filter(quantification_scale__in=quant)

        if time:
            qs = qs.filter(time_horizon_scale__in=time)

        return qs
class MeasureDetailView(DetailView):
    model = Measure
    template_name = "measure_detail.html"
    context_object_name = "measure"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["box_names"] = BoxName.objects.all().order_by("box_number")

        return context

class ContactPersonListView(ListView):
    model = ContactPerson
    template_name = "contacts.html"
    context_object_name = "peoples"
    ordering = ("last_name", "first_name")

class HeroCssView(DetailView):
    model = Measure
    template_name = "css/hero.css"
    content_type = "text/css; charset=utf-8"
    context_object_name = "measure"

    def render_to_response(self, context, **response_kwargs):
        response_kwargs.setdefault("content_type", self.content_type)
        response = super().render_to_response(context, **response_kwargs)
        response["Cache-Control"] = "public, max-age=86400"
        response["Last-Modified"] = http_date(now().timestamp())
        return response




class ContactPersonRevealEmailView(View):
    def get(self, request, pk: int):
        try:
            p = ContactPerson.objects.only("id", "email", "phone").get(pk=pk)
        except ContactPerson.DoesNotExist:
            raise Http404

        return JsonResponse({
            "email": p.email,
        })

class ContactPersonRevealPhoneView(View):
    def get(self, request, pk: int):
        try:
            p = ContactPerson.objects.only("id", "email", "phone").get(pk=pk)
        except ContactPerson.DoesNotExist:
            raise Http404

        return JsonResponse({
            "email": p.phone,
        })