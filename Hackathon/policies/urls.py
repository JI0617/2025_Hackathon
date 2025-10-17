from django.urls import path
from . import views

urlpatterns = [
    # 정책 목록 및 상세
    path('', views.policy_list, name='policy_list'),
    path('recommendations/', views.policy_recommendations, name='policy_recommendations'),
    path('<int:policy_id>/', views.policy_detail, name='policy_detail'),
    path('category/<str:category>/', views.policy_category, name='policy_category'),
]
