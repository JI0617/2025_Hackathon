from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ComparisonViewSet

router = DefaultRouter()
router.register(r'comparisons', ComparisonViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
