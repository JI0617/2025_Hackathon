"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('regions.api_urls')),  # 지역 API
    path('api/v1/', include('reviews.api_urls')),  # 리뷰 API
    path('api/v1/', include('comparisons.api_urls')),  # 비교 API
    path('api/v1/', include('users.api_urls')),  # 사용자 API
    path('api/', include('main.api_urls')),  # 메인 API (추천 등)
    path('', include('main.urls')),  # 메인 페이지 (루트)
    path('regions/', include('regions.urls')),  # 지역 관련
    path('users/', include('users.urls')),  # 사용자 관련
    path('reviews/', include('reviews.urls')),  # 리뷰 관련
    path('comparisons/', include('comparisons.urls')),  # 비교 관련
    path('chatbot/', include('chatbot.urls')),  # 챗봇 관련
    path('policies/', include('policies.urls')),  # 정책 관련
]


