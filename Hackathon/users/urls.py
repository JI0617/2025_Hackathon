from django.urls import path
from main import views

urlpatterns = [
    # 인증 관련
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # 사용자 기능
    path('preferences/', views.preferences, name='preferences'),
    path('recommendations/', views.recommendations, name='recommendations'),
] 