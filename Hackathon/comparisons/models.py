from django.db import models
from django.contrib.auth.models import User

class Comparison(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="비교 이름")
    regions = models.ManyToManyField('regions.Region')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 대분류/소분류 찜 비교 기능
    CATEGORY_CHOICES = [
        ('traffic', '교통'),
        ('education', '교육'),
        ('medical', '의료'),
        ('cost', '비용'),
        ('environment', '환경'),
        ('culture', '문화'),
        ('safety', '안전'),
        ('convenience', '편의시설'),
    ]
    
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='general',
        help_text="비교 카테고리"
    )
    
    is_favorite = models.BooleanField(default=False, help_text="찜 목록 여부")

    def __str__(self):
        return f"{self.user.username}의 {self.name} 비교"
