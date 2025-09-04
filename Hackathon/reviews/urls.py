from django.urls import path
from main import views

urlpatterns = [
    # 리뷰 기능
    path('region/<str:region_name>/review/', views.add_review, name='add_review'),
] 