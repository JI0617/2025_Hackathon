from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class UserProfile(models.Model):
    """사용자 프로필 확장 모델"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(120)],
        help_text="나이"
    )
    GENDER_CHOICES = [
        ('M', '남성'),
        ('F', '여성'),
        ('O', '기타'),
    ]
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        help_text="성별"
    )
    JOB_CHOICES = [
        ('student', '학생'),
        ('office_worker', '직장인'),
        ('freelancer', '프리랜서'),
        ('business_owner', '사업자'),
        ('public_servant', '공무원'),
        ('teacher', '교사'),
        ('healthcare', '의료진'),
        ('engineer', '엔지니어'),
        ('designer', '디자이너'),
        ('other', '기타'),
    ]
    job = models.CharField(
        max_length=20,
        choices=JOB_CHOICES,
        help_text="직무"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}의 프로필"

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    education_importance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        default=2,
        help_text="교육 중요도 (1-3)"
    )
    medical_importance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        default=2,
        help_text="의료 중요도 (1-3)"
    )
    cost_importance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        default=2,
        help_text="비용 중요도 (1-3)"
    )
    preferred_cost_level = models.CharField(
        max_length=20,
        choices=[
            ('하', '하'),
            ('중', '중'),
            ('상', '상'),
        ],
        default='보통'
    )
    # 월세 관련 선호도
    monthly_rent_budget = models.IntegerField(
        null=True, blank=True,
        help_text="월세 예산 (만원 단위)"
    )
    deposit_budget = models.IntegerField(
        null=True, blank=True,
        help_text="보증금 예산 (만원 단위)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}의 선호도"
