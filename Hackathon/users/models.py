from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    traffic_importance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=3,
        help_text="교통 중요도 (1-5)"
    )
    education_importance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=3,
        help_text="교육 중요도 (1-5)"
    )
    cost_importance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=3,
        help_text="비용 중요도 (1-5)"
    )
    preferred_cost_level = models.CharField(
        max_length=20,
        choices=[
            ('매우낮음', '매우낮음'),
            ('낮음', '낮음'),
            ('보통', '보통'),
            ('높음', '높음'),
            ('매우높음', '매우높음'),
        ],
        default='보통'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}의 선호도"
