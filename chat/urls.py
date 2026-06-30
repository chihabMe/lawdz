from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.chat, name="chat"),
    path("sources/", views.sources, name="sources"),
    # Ingestion will be a management command primarily
]
