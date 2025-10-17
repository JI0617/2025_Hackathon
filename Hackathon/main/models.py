from django.db import models
from django.contrib.auth.models import User
import json

# Models have been moved to their respective apps:
# - Region, News -> regions app
# - UserPreference -> users app  
# - Review -> reviews app
# - Comparison -> comparisons app

class SavedSearch(models.Model):
    """저장된 검색 조건 모델"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    name = models.CharField(max_length=100, help_text='검색 조건 이름')
    description = models.TextField(blank=True, help_text='검색 조건 설명')
    search_params = models.JSONField(help_text='검색 파라미터 (JSON)')
    is_public = models.BooleanField(default=False, help_text='공개 여부')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    def get_search_url(self):
        """검색 조건을 URL 파라미터로 변환"""
        params = []
        for key, value in self.search_params.items():
            if value:  # 빈 값이 아닌 경우만
                params.append(f"{key}={value}")
        return "&".join(params)
    
    def save_search_params(self, form_data):
        """폼 데이터를 JSON으로 저장"""
        self.search_params = {k: v for k, v in form_data.items() if v}
    
    def load_search_params(self):
        """저장된 검색 조건을 폼에 로드"""
        return self.search_params
