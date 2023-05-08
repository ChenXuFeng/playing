from django.urls import path

from .views import Stats

urlpatterns = [
    path('9e59390013fba5ec4605/stats/<str:types>', Stats.as_view()),
]