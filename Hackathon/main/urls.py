from django.urls import path
from . import views

urlpatterns = [
    # 기본 페이지
    path('', views.home, name='home'),
    
    # API
    path('api/regions/', views.api_regions, name='api_regions'),
    
    # 정책 및 마이페이지
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('my-page/', views.my_page, name='my_page'),
]