from django.urls import path
from . import api_views

urlpatterns = [
    path('recommendations/', api_views.get_recommendations, name='api_recommendations'),
]
