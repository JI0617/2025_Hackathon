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