"""
lawdz URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health(request):
    return JsonResponse({"status": "ok", "service": "lawdz-django"})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("chat.urls")),
    path("api/health/", health, name="health"),
]
