from django.urls import path
from main import views

urlpatterns = [
    # 비교 기능
    path('', views.comparison, name='comparison'),
    path('<int:pk>/', views.comparison_detail, name='comparison_detail'),
] 