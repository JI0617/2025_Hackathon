from django.urls import path
from . import views

urlpatterns = [
    # 리뷰 목록 및 상세
    path('', views.review_list, name='review_list'),
    path('<int:review_id>/', views.review_detail, name='review_detail'),
    
    # 리뷰 작성, 수정, 삭제
    path('create/<int:region_id>/', views.create_review, name='create_review'),
    path('edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('delete/<int:review_id>/', views.delete_review, name='delete_review'),
    
    # 지역별 리뷰
    path('region/<int:region_id>/', views.region_reviews, name='region_reviews'),
    
    # AJAX 기능
    path('like/<int:review_id>/', views.like_review, name='like_review'),
]