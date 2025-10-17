from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from regions.models import Region
# UserProfile 모델이 UserRegistrationForm에서 참조되므로, 아래에 choices를 임의로 정의합니다.
# 실제 UserProfile 모델에 정의된 GENDER_CHOICES, JOB_CHOICES와 일치시켜야 합니다.
from users.models import UserPreference, UserProfile 
from reviews.models import Review
from comparisons.models import Comparison

# UserProfile이 정의되지 않은 경우를 대비해 임시 choices를 정의하거나,
# 실제 UserProfile에 정의된 choices를 사용해야 합니다.
# 여기서는 UserProfile 모델에 GENDER_CHOICES와 JOB_CHOICES가 정의되어 있다고 가정합니다.

# UserPreferenceForm에서 사용할 비용 레벨 Choices를 정의합니다.
# 뷰에서 이 값('낮음', '보통', '높음')을 모델의 '하', '중', '상'으로 매핑했으므로 동일하게 사용합니다.
COST_LEVEL_CHOICES = [
    ('낮음', '낮음 (부담 적음)'),
    ('보통', '보통 (적당함)'),
    ('높음', '높음 (부담 많음)'),
]

# --- 사용자 관련 폼 (변경 없음) ---

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    age = forms.IntegerField(
        min_value=1, max_value=120,
        widget=forms.NumberInput(attrs={'placeholder': '나이를 입력하세요'})
    )
    # UserProfile 모델에 GENDER_CHOICES와 JOB_CHOICES가 정의되어 있어야 합니다.
    gender = forms.ChoiceField(
        choices=UserProfile.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    job = forms.ChoiceField(
        choices=UserProfile.JOB_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'age', 'gender', 'job')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # UserProfile 생성
            UserProfile.objects.create(
                user=user,
                age=self.cleaned_data['age'],
                gender=self.cleaned_data['gender'],
                job=self.cleaned_data['job']
            )
        return user

# --- 선호도 폼 (수정 필요) ---

class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        # preferred_cost_level의 choices를 수정합니다.
        fields = ['education_importance', 'medical_importance', 'cost_importance', 'preferred_cost_level', 'monthly_rent_budget', 'deposit_budget']
        # Use 3-step importance choices: 상 (3), 중 (2), 하 (1)
        IMPORTANCE_CHOICES = [
            (3, '상'),
            (2, '중'),
            (1, '하'),
        ]
        widgets = {
            'education_importance': forms.Select(choices=IMPORTANCE_CHOICES),
            'medical_importance': forms.Select(choices=IMPORTANCE_CHOICES),
            'cost_importance': forms.Select(choices=IMPORTANCE_CHOICES),
            # Region 모델에 접근하는 대신, 정의된 COST_LEVEL_CHOICES 사용
            'preferred_cost_level': forms.Select(choices=COST_LEVEL_CHOICES), 
            'monthly_rent_budget': forms.NumberInput(attrs={'placeholder': '월세 예산 (만원)', 'min': '0'}),
            'deposit_budget': forms.NumberInput(attrs={'placeholder': '보증금 예산 (만원)', 'min': '0'}),
        }

# --- 리뷰 및 비교 폼 (변경 없음) ---

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': '이 지역에 대한 경험을 공유해주세요...'}),
        }

class ComparisonForm(forms.ModelForm):
    regions = forms.ModelMultipleChoiceField(
        queryset=Region.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        help_text="비교할 지역들을 선택하세요 (최대 5개)"
    )
    
    class Meta:
        model = Comparison
        fields = ['name', 'regions']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '비교 이름을 입력하세요'}),
        }

    def clean_regions(self):
        regions = self.cleaned_data.get('regions')
        if len(regions) > 5:
            raise forms.ValidationError("최대 5개 지역까지만 비교할 수 있습니다.")
        if len(regions) < 2:
            raise forms.ValidationError("최소 2개 지역을 선택해야 합니다.")
        return regions

# --- 검색 폼 (대폭 수정 필요) ---

class SearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '지역명을 검색하세요...'})
    )
    # Region 모델에 'city' 필드가 없으므로, 이 필드를 사용하려면 '지역명'에서 시/도를 파싱하는 로직이 필요합니다.
    # 현재 모델에 없으므로 유지하되, 뷰에서 필터링이 안 될 수 있음을 염두에 두어야 합니다.
    city = forms.ChoiceField(
        choices=[
             ('', '전체 시/도'),
             ('서울특별시', '서울특별시'),
             ('부산광역시', '부산광역시'),
             ('대구광역시', '대구광역시'),
             ('인천광역시', '인천광역시'),
             ('광주광역시', '광주광역시'),
             ('대전광역시', '대전광역시'),
             ('울산광역시', '울산광역시'),
             ('세종특별자치시', '세종특별자치시'),
             ('경기도', '경기도'),
             ('강원특별자치도', '강원특별자치도'),
             ('충청북도', '충청북도'),
             ('충청남도', '충청남도'),
             ('전북특별자치도', '전북특별자치도'),
             ('전라남도', '전라남도'),
             ('경상북도', '경상북도'),
             ('경상남도', '경상남도'),
             ('제주특별자치도', '제주특별자치도'),
        ],
        required=False
    )
    
    # 점수 필드 제거 (min_traffic, min_education, min_medical은 점수 데이터가 없어 제거)
    
    cost_level = forms.ChoiceField(
        # 기존 cost_level 대신, 사용자 친화적인 COST_LEVEL_CHOICES를 사용하여 뷰의 로직과 일치시킵니다.
        choices=[('', '전체')] + COST_LEVEL_CHOICES,
        required=False
    )

class AdvancedSearchForm(SearchForm):
    """고급 검색 폼 - 기존 SearchForm을 확장"""
    
    # --- 점수 범위 필터 제거 ---
    # traffic_range, education_range, medical_range는 점수 데이터가 없어 제거합니다.
    
    # --- 인구/면적 필터 제거 ---
    # population_range, area_range는 CSV 데이터에 해당 필드가 없어 제거합니다.
    
    # --- 정렬 옵션 수정 ---
    sort_by = forms.ChoiceField(
        choices=[
            ('name', '지역명 (가나다순)'),
            ('-name', '지역명 (역순)'),
            
            # 기존 점수 대신 등급별 정렬 추가 (필드 이름은 모델의 'education_infra_grade', 'medical_grade', 'total_burden_grade')
            ('education_infra_grade', '교육 등급 (낮은순)'),
            ('-education_infra_grade', '교육 등급 (높은순)'),
            ('medical_grade', '의료 등급 (낮은순)'),
            ('-medical_grade', '의료 등급 (높은순)'),
            ('total_burden_grade', '종합부담 등급 (낮은순)'), # '하' -> '상'
            ('-total_burden_grade', '종합부담 등급 (높은순)'), # '상' -> '하'
            
            ('-students_per_teacher', '교원당 학생수 (적은순)'), # CSV 데이터에 있는 필드 추가
            ('students_per_teacher', '교원당 학생수 (많은순)'),
            ('-monthly_rent_manwon', '월세 (높은순)'),
            ('monthly_rent_manwon', '월세 (낮은순)'),
            
            # 리뷰 관련 정렬은 regions.models.Review 모델을 Aggregation하여 사용해야 하므로 주석 처리
            ('-avg_rating', '평점 (높은순)'),
            ('avg_rating', '평점 (낮은순)'),
            
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # --- 리뷰 필터 (유지) ---
    has_reviews = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='리뷰가 있는 지역만'
    )
    
    min_rating = forms.ChoiceField(
        choices=[
            ('', '최소 평점'),
            ('1', '1점 이상'),
            ('2', '2점 이상'),
            ('3', '3점 이상'),
            ('4', '4점 이상'),
            ('5', '5점만'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # --- 저장된 검색 조건 (유지) ---
    saved_search_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '검색 조건 저장 이름'})
    )

class SavedSearchForm(forms.Form):
    """저장된 검색 조건 폼"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': '검색 조건 이름'})
    )
    description = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': '설명 (선택사항)'})
    )