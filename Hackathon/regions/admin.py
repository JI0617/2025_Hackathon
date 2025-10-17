# regions/admin.py (수정 필요)

from django.contrib import admin
from .models import Region # Region 모델이 regions 앱에 있다고 가정합니다.

# RegionAdmin 정의
class RegionAdmin(admin.ModelAdmin):
    
    # 1. list_display 수정 (관리자 목록에 표시할 필드)
    list_display = (
        'name',          # 지역명
        'medical_accessibility',  # 의료 평균접근성
        'student_count',        # 학생수
        'teacher_count',        # 교원수
        'deposit_manwon',       # 보증금(만원)
        'monthly_rent_manwon',  # 월세금(만원)
        'total_burden_grade',   # 종합부담등급
        'medical_grade',        # 의료 등급
        'education_infra_grade',# 교육 인프라 등급
    )
    
    # 2. ordering 수정 (기본 정렬 순서)
    ordering = ('name',)

    # 3. list_filter 수정 (측면 필터)
    list_filter = (
        'total_burden_grade',   # 종합부담등급
        'medical_grade',        # 의료 등급
        'education_infra_grade',# 교육 인프라 등급
        'monthly_rent_grade',   # 월세등급
    )
    
    # 검색 필드
    search_fields = ('name', 'summary')

# RegionAdmin을 Admin 사이트에 등록
admin.site.register(Region, RegionAdmin)