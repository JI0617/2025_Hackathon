from django.urls import path
from . import views

urlpatterns = [
    # 비교 목록 및 상세
    path('', views.comparison_list, name='comparison_list'),
    path('quick/', views.quick_compare, name='quick_compare'),
    path('<int:comparison_id>/', views.comparison_detail, name='comparison_detail'),
    
    # 비교 생성, 수정, 삭제
    path('create/', views.create_comparison, name='create_comparison'),
    path('edit/<int:comparison_id>/', views.edit_comparison, name='edit_comparison'),
    path('delete/<int:comparison_id>/', views.delete_comparison, name='delete_comparison'),
    
    # AJAX 기능
    path('add-region/<int:comparison_id>/', views.add_region_to_comparison, name='add_region_to_comparison'),
    path('remove-region/<int:comparison_id>/', views.remove_region_from_comparison, name='remove_region_from_comparison'),
]