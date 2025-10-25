from django.db import models
from decimal import Decimal

class Region(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="지역명")
    
    # 숫자형 데이터 (CSV 기반)
    medical_accessibility = models.FloatField(verbose_name="의료 평균접근성") # 낮을수록 좋음
    student_count = models.IntegerField(verbose_name="학생수")
    teacher_count = models.IntegerField(verbose_name="교원수")
    students_per_teacher = models.FloatField(verbose_name="교원 1인당 학생수") # 낮을수록 좋음
    deposit_manwon = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="보증금(만원)")
    monthly_rent_manwon = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="월세금(만원)")
    total_monthly_burden = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="종합월부담") # 낮을수록 좋음
    
    # 등급 데이터 (CSV 기반)
    total_burden_grade = models.CharField(max_length=5, verbose_name="종합부담등급")
    medical_grade = models.CharField(max_length=5, verbose_name="의료 등급")
    education_infra_grade = models.CharField(max_length=5, verbose_name="교육 인프라 등급")
    monthly_rent_grade = models.CharField(max_length=5, verbose_name="월세등급")
    summary = models.TextField(verbose_name="summary")
    
    # 템플릿/지도 사용을 위해 추가된 필드 (교통 필드 삭제)
    latitude = models.FloatField(default=0.0, verbose_name="위도")
    longitude = models.FloatField(default=0.0, verbose_name="경도")
    population = models.IntegerField(default=0, verbose_name="인구수")
    area = models.FloatField(default=0.0, verbose_name="면적")
    
    # 계산된 0-100점 점수를 저장할 필드 (DB 필드로만 사용)
    medical_score = models.DecimalField(max_digits=5, decimal_places=2, default=50.0, verbose_name="의료 점수")
    education_score = models.DecimalField(max_digits=5, decimal_places=2, default=50.0, verbose_name="교육 점수")
    cost_score = models.DecimalField(max_digits=5, decimal_places=2, default=50.0, verbose_name="생활비 점수")
    
    class Meta:
        verbose_name = "지역 정보"
        verbose_name_plural = "지역 정보 목록"

    def __str__(self):
        return self.name

    # --- 템플릿에서 사용하는 속성 ---

    @property
    def city(self):
        """지역명에서 시/군/구만 추출"""
        parts = self.name.split()
        return parts[-1] if parts else ""
        
    @property
    def description(self):
        """템플릿 호환성을 위해 summary를 description으로 연결"""
        return self.summary
        
    # medical_score, education_score @property 제거 완료

    @property
    def cost_level(self):
        """생활비 점수(cost_score)를 기반으로 등급 문자열 반환"""
        score = self.cost_score
        # 점수가 높을수록 (부담이 낮을수록) 좋은 등급을 부여
        if score >= Decimal('80.0'):
            return '매우낮음'
        elif score >= Decimal('60.0'):
            return '낮음'
        elif score >= Decimal('40.0'):
            return '보통'
        elif score >= Decimal('20.0'):
            return '높음'
        else:
            return '매우높음'