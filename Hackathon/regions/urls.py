from django.urls import path
from . import views

urlpatterns = [
    # 지역 관련
    path('region/<str:name>/', views.region_detail, name='region_detail'),
    path('news/', views.news, name='news'),
] 