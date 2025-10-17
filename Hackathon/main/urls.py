from django.urls import path
from . import views

urlpatterns = [
    # 기본 페이지
    path('', views.home, name='home'),
    
    # --- 지역 상세 및 리뷰 ---
    # 지역 상세 페이지
    path('region/<str:name>/', views.region_detail, name='region_detail'), 
    # 리뷰 추가
    path('region/<str:name>/review/', views.add_review, name='add_review'),
    
    # --- 비교 기능 ---
    path('comparison/', views.comparison, name='comparison'),
    path('comparison/<int:pk>/', views.comparison_detail, name='comparison_detail'),
    
    # --- 고급 검색 및 저장 ---
    path('advanced-search/', views.advanced_search, name='advanced_search'),
    path('save-search/', views.save_search, name='save_search'),
    path('load-search/<int:search_id>/', views.load_saved_search, name='load_saved_search'),
    path('delete-search/<int:search_id>/', views.delete_saved_search, name='delete_saved_search'),
    
    # --- API ---
    path('api/regions/', views.api_regions, name='api_regions'),
    # 'api_realtime_news' 'api_realtime_stats'
    path('api/region/<int:region_id>/updates/', views.api_region_updates, name='api_region_updates'),
    
    # --- 정책 및 마이페이지 ---
    # 'policy/' 경로는 제거했습니다.
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('my-page/', views.my_page, name='my_page'),
    path('calculator/', views.calculator, name='calculator'),
]