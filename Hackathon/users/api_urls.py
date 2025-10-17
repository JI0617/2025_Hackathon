from django.urls import path
from .api_views import register, login_view, logout_view, profile, update_profile

urlpatterns = [
    path('register/', register, name='api_register'),
    path('login/', login_view, name='api_login'),
    path('logout/', logout_view, name='api_logout'),
    path('profile/', profile, name='api_profile'),
    path('profile/update/', update_profile, name='api_update_profile'),
]
