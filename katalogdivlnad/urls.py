"""
URL configuration for katalogdivlnad project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.views.i18n import set_language
from catalog.views import Home, MeasuresListByGroupView, MeasureDetailView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', Home.as_view(), name='home'),
    path('groups/', MeasuresListByGroupView.as_view(), name='groups-all'),
    path('groups/group-<int:pk>/', MeasuresListByGroupView.as_view(), name='group-filter'),
    path('measure/<int:pk>/', MeasureDetailView.as_view(), name='measure-detail'),
    path("markdownx/", include("markdownx.urls")),
    #path("<slug:slug>/", views.page_detail, name="page_detail"),
]

urlpatterns += [
    path('i18n/set_language/', set_language, name='set_language'),
]

if settings.DEBUG and settings.ENVIRONMENT == 'local':
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

