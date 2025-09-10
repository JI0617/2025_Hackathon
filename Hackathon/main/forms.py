from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from regions.models import Region
from users.models import UserPreference
from reviews.models import Review
from comparisons.models import Comparison

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ['traffic_importance', 'education_importance', 'cost_importance', 'preferred_cost_level']
        widgets = {
            'traffic_importance': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'education_importance': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'cost_importance': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'preferred_cost_level': forms.Select(choices=Region.cost_level.field.choices),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f"{i}점") for i in range(1, 6)]),
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

class SearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '지역명을 검색하세요...'})
    )
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
    min_traffic = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'placeholder': '최소 교통점수'})
    )
    min_education = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'placeholder': '최소 교육점수'})
    )
    min_medical = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'placeholder': '최소 의료점수'})
    )
    cost_level = forms.ChoiceField(
        choices=[
            ('', '전체'),
            ('매우낮음', '매우낮음'),
            ('낮음', '낮음'),
            ('보통', '보통'),
            ('높음', '높음'),
            ('매우높음', '매우높음'),
        ],
        required=False
    )

class AdvancedSearchForm(SearchForm):
    """고급 검색 폼 - 기존 SearchForm을 확장"""
    
    # 점수 범위 필터
    traffic_range = forms.ChoiceField(
        choices=[
            ('', '교통점수 범위'),
            ('0-20', '0-20점'),
            ('21-40', '21-40점'),
            ('41-60', '41-60점'),
            ('61-80', '61-80점'),
            ('81-100', '81-100점'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    education_range = forms.ChoiceField(
        choices=[
            ('', '교육점수 범위'),
            ('0-20', '0-20점'),
            ('21-40', '21-40점'),
            ('41-60', '41-60점'),
            ('61-80', '61-80점'),
            ('81-100', '81-100점'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    medical_range = forms.ChoiceField(
        choices=[
            ('', '의료점수 범위'),
            ('0-20', '0-20점'),
            ('21-40', '21-40점'),
            ('41-60', '41-60점'),
            ('61-80', '61-80점'),
            ('81-100', '81-100점'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # 인구수 필터
    population_range = forms.ChoiceField(
        choices=[
            ('', '인구수 범위'),
            ('0-10000', '1만명 미만'),
            ('10000-50000', '1만-5만명'),
            ('50000-100000', '5만-10만명'),
            ('100000-500000', '10만-50만명'),
            ('500000-1000000', '50만-100만명'),
            ('1000000-9999999', '100만명 이상'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # 면적 필터
    area_range = forms.ChoiceField(
        choices=[
            ('', '면적 범위'),
            ('0-50', '50km² 미만'),
            ('50-100', '50-100km²'),
            ('100-200', '100-200km²'),
            ('200-500', '200-500km²'),
            ('500-1000', '500-1000km²'),
            ('1000-9999', '1000km² 이상'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # 정렬 옵션
    sort_by = forms.ChoiceField(
        choices=[
            ('name', '지역명 (가나다순)'),
            ('-name', '지역명 (역순)'),
            ('-traffic_score', '교통점수 (높은순)'),
            ('traffic_score', '교통점수 (낮은순)'),
            ('-education_score', '교육점수 (높은순)'),
            ('education_score', '교육점수 (낮은순)'),
            ('-medical_score', '의료점수 (높은순)'),
            ('medical_score', '의료점수 (낮은순)'),
            ('-population', '인구수 (많은순)'),
            ('population', '인구수 (적은순)'),
            ('-area', '면적 (큰순)'),
            ('area', '면적 (작은순)'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # 리뷰 필터
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
    
    # 저장된 검색 조건
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