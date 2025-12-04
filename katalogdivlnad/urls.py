from django.contrib import admin
from django.urls import path, include
from django.views.i18n import set_language
from catalog.views import Home, MeasuresListByGroupView, MeasureDetailView, HeroCssView, ContactPersonDetailView, \
    MeasuresListByGroupAjaxView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', Home.as_view(), name='home'),
    path('groups/', MeasuresListByGroupView.as_view(), name='groups-all'),
    path('groups/group-<int:pk>/', MeasuresListByGroupView.as_view(), name='group-filter'),
    path('measure/<int:pk>/', MeasureDetailView.as_view(), name='measure-detail'),
    path('contact/<int:pk>/', ContactPersonDetailView.as_view(), name='contact-detail'),
    path("markdownx/", include("markdownx.urls")),
    #path("<slug:slug>/", views.page_detail, name="page_detail"),
    path("css/hero/images-<int:pk>.css", HeroCssView.as_view(), name="hero_css"),

    path("groups/ajax/", MeasuresListByGroupAjaxView.as_view(), name="groups-all-ajax"),
    path(
        "measures/group/<int:pk>/ajax/",
        MeasuresListByGroupAjaxView.as_view(),
        name="measures_by_group_ajax",
    ),
]

urlpatterns += [
    path('i18n/set_language/', set_language, name='set_language'),
]

if settings.DEBUG and settings.ENVIRONMENT == 'local':
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
