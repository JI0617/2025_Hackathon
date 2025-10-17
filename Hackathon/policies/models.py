from django.db import models
from django.contrib.auth.models import User

class Policy(models.Model):
    """정책 모델"""
    title = models.CharField(max_length=200, help_text="정책 제목")
    content = models.TextField(help_text="정책 내용")
    summary = models.TextField(max_length=500, help_text="정책 요약")
    
    # 카테고리 분류
    CATEGORY_CHOICES = [
        ('youth', '청년'),
        ('housing', '주거'),
        ('education', '교육'),
        ('medical', '의료'),
        ('transportation', '교통'),
        ('business', '창업'),
        ('employment', '취업'),
        ('family', '가족'),
        ('elderly', '노인'),
        ('disability', '장애인'),
        ('environment', '환경'),
        ('culture', '문화'),
        ('tourism', '관광'),
        ('agriculture', '농업'),
        ('fishery', '수산업'),
        ('general', '일반'),
    ]
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general',
        help_text="정책 카테고리"
    )
    
    # 지역 관련
    region = models.ForeignKey(
        'regions.Region',
        on_delete=models.CASCADE,
        related_name='policies',
        null=True,
        blank=True,
        help_text="해당 지역 (전국 정책의 경우 None)"
    )
    
    # 정책 정보
    target_age_min = models.IntegerField(null=True, blank=True, help_text="대상 연령 최소")
    target_age_max = models.IntegerField(null=True, blank=True, help_text="대상 연령 최대")
    target_income_min = models.IntegerField(null=True, blank=True, help_text="대상 소득 최소")
    target_income_max = models.IntegerField(null=True, blank=True, help_text="대상 소득 최대")
    
    # 지원 내용
    support_amount = models.IntegerField(null=True, blank=True, help_text="지원 금액")
    support_period = models.CharField(max_length=100, blank=True, help_text="지원 기간")
    support_type = models.CharField(max_length=100, blank=True, help_text="지원 유형")
    
    # 신청 정보
    application_start = models.DateTimeField(null=True, blank=True, help_text="신청 시작일")
    application_end = models.DateTimeField(null=True, blank=True, help_text="신청 마감일")
    application_url = models.URLField(blank=True, help_text="신청 URL")
    contact_info = models.CharField(max_length=200, blank=True, help_text="문의처")
    
    # 상태 관리
    is_active = models.BooleanField(default=True, help_text="활성화 여부")
    is_featured = models.BooleanField(default=False, help_text="추천 정책 여부")
    priority = models.IntegerField(default=0, help_text="우선순위")
    
    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="등록자"
    )
    
    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = '정책'
        verbose_name_plural = '정책들'
    
    def __str__(self):
        return self.title
    
    def get_category_display_name(self):
        """카테고리 한글명 반환"""
        category_dict = dict(self.CATEGORY_CHOICES)
        return category_dict.get(self.category, self.category)
    
    def is_application_open(self):
        """신청 가능 여부 확인"""
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False
            
        if self.application_start and now < self.application_start:
            return False
            
        if self.application_end and now > self.application_end:
            return False
            
        return True
