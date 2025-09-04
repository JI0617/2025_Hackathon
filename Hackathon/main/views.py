from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.core.paginator import Paginator
from regions.models import Region, News
from users.models import UserPreference
from reviews.models import Review
from comparisons.models import Comparison
from .forms import UserRegistrationForm, UserPreferenceForm, ReviewForm, ComparisonForm, SearchForm

def home(request):
    """메인 홈페이지 - 검색 및 필터링 기능 포함"""
    search_form = SearchForm(request.GET)
    regions = Region.objects.all()
    
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search_query')
        city = search_form.cleaned_data.get('city')
        min_traffic = search_form.cleaned_data.get('min_traffic')
        min_education = search_form.cleaned_data.get('min_education')
        min_medical = search_form.cleaned_data.get('min_medical')
        cost_level = search_form.cleaned_data.get('cost_level')
        
        if search_query:
            regions = regions.filter(name__icontains=search_query)
        if city:
            regions = regions.filter(city=city)
        if min_traffic is not None:
            regions = regions.filter(traffic_score__gte=min_traffic)
        if min_education is not None:
            regions = regions.filter(education_score__gte=min_education)
        if min_medical is not None:
            regions = regions.filter(medical_score__gte=min_medical)
        if cost_level:
            regions = regions.filter(cost_level=cost_level)
    
    # 페이지네이션
    paginator = Paginator(regions, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 통계 정보
    total_regions_count = Region.objects.count()
    total_reviews_count = Review.objects.count()
    
    context = {
        'regions': page_obj,
        'search_form': search_form,
        'total_regions': regions.count(),
        'total_regions_count': total_regions_count,
        'total_reviews_count': total_reviews_count,
    }
    return render(request, 'main/home.html', context)

def region_detail(request, name):
    """지역 상세 페이지 - 리뷰 및 평점 포함"""
    region = get_object_or_404(Region, name=name)
    reviews = region.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # 사용자 리뷰 작성 폼
    review_form = None
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        if not user_review:
            review_form = ReviewForm()
    
    context = {
        'region': region,
        'reviews': reviews[:5],  # 최근 5개 리뷰만 표시
        'avg_rating': round(avg_rating, 1),
        'review_count': reviews.count(),
        'review_form': review_form,
        'user_review': user_review,
    }
    return render(request, 'regions/detail.html', context)

@login_required
def add_review(request, region_name):
    """리뷰 추가"""
    region = get_object_or_404(Region, name=region_name)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.region = region
            review.save()
            messages.success(request, '리뷰가 성공적으로 등록되었습니다!')
            return redirect('region_detail', name=region_name)
    else:
        form = ReviewForm()
    
    return render(request, 'reviews/add_review.html', {'form': form, 'region': region})

def register(request):
    """사용자 등록"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '회원가입이 완료되었습니다!')
            return redirect('preferences')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    """사용자 로그인"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'{user.username}님 환영합니다!')
            return redirect('home')
        else:
            messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
    
    return render(request, 'users/login.html')

@login_required
def user_logout(request):
    """사용자 로그아웃"""
    logout(request)
    messages.success(request, '로그아웃되었습니다.')
    return redirect('home')

@login_required
def preferences(request):
    """사용자 선호도 설정"""
    preference, created = UserPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserPreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            messages.success(request, '선호도가 저장되었습니다!')
            return redirect('recommendations')
    else:
        form = UserPreferenceForm(instance=preference)
    
    return render(request, 'users/preferences.html', {'form': form})

@login_required
def recommendations(request):
    """개인화된 추천"""
    try:
        preference = request.user.userpreference
        regions = Region.objects.all()
        
        # 선호도 기반 점수 계산
        scored_regions = []
        for region in regions:
            score = 0
            score += region.traffic_score * preference.traffic_importance
            score += region.education_score * preference.education_importance
            
            # 비용 선호도 반영
            cost_score = 0
            if preference.preferred_cost_level == region.cost_level:
                cost_score = 100
            elif preference.preferred_cost_level == '낮음' and region.cost_level in ['매우낮음', '낮음']:
                cost_score = 80
            elif preference.preferred_cost_level == '보통' and region.cost_level == '보통':
                cost_score = 100
            elif preference.preferred_cost_level == '높음' and region.cost_level in ['높음', '매우높음']:
                cost_score = 80
            
            score += cost_score * preference.cost_importance
            scored_regions.append((region, score))
        
        # 점수순 정렬
        scored_regions.sort(key=lambda x: x[1], reverse=True)
        recommended_regions = [region for region, score in scored_regions[:5]]
        
    except UserPreference.DoesNotExist:
        recommended_regions = Region.objects.all()[:5]
        messages.warning(request, '선호도를 설정해주세요!')
    
    return render(request, 'users/recommendations.html', {
        'recommended_regions': recommended_regions
    })

@login_required
def comparison(request):
    """지역 비교 기능"""
    if request.method == 'POST':
        form = ComparisonForm(request.POST)
        if form.is_valid():
            comparison = form.save(commit=False)
            comparison.user = request.user
            comparison.save()
            form.save_m2m()
            return redirect('comparison_detail', pk=comparison.pk)
    else:
        form = ComparisonForm()
    
    user_comparisons = Comparison.objects.filter(user=request.user).order_by('-created_at')
    
    # 시/도별로 그룹화된 지역 데이터
    from django.db.models import Count
    regions_by_city = Region.objects.values('city').annotate(count=Count('id')).order_by('-count')
    grouped_regions = {}
    for city_info in regions_by_city:
        city = city_info['city']
        regions = Region.objects.filter(city=city).order_by('name')
        grouped_regions[city] = regions
    
    return render(request, 'comparisons/comparison.html', {
        'form': form,
        'user_comparisons': user_comparisons,
        'grouped_regions': grouped_regions
    })

def comparison_detail(request, pk):
    """비교 상세 페이지"""
    comparison = get_object_or_404(Comparison, pk=pk)
    regions = comparison.regions.all()
    
    # 비교 데이터 준비
    comparison_data = []
    for region in regions:
        avg_rating = region.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        comparison_data.append({
            'region': region,
            'avg_rating': round(avg_rating, 1),
            'review_count': region.reviews.count(),
        })
    
    return render(request, 'comparisons/comparison_detail.html', {
        'comparison': comparison,
        'comparison_data': comparison_data
    })

def news(request):
    """뉴스 및 업데이트"""
    featured_news = News.objects.filter(is_featured=True).order_by('-published_at')[:3]
    all_news = News.objects.all().order_by('-published_at')
    
    # 페이지네이션
    paginator = Paginator(all_news, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'regions/news.html', {
        'featured_news': featured_news,
        'news_list': page_obj
    })

def calculator(request):
    """생활비 계산기"""
    if request.method == 'POST':
        region_name = request.POST.get('region')
        monthly_income = int(request.POST.get('monthly_income', 0))
        family_size = int(request.POST.get('family_size', 1))
        
        try:
            region = Region.objects.get(name=region_name)
            
            # 간단한 생활비 계산 (예시)
            base_cost = {
                '매우낮음': 800000,
                '낮음': 1000000,
                '보통': 1200000,
                '높음': 1500000,
                '매우높음': 2000000,
            }
            
            monthly_cost = base_cost.get(region.cost_level, 1200000) * family_size
            remaining = monthly_income - monthly_cost
            
            calculation_result = {
                'region': region,
                'monthly_income': monthly_income,
                'family_size': family_size,
                'monthly_cost': monthly_cost,
                'remaining': remaining,
                'cost_level': region.cost_level,
            }
            
            return render(request, 'calculator/calculator.html', {'result': calculation_result})
            
        except Region.DoesNotExist:
            messages.error(request, '지역을 찾을 수 없습니다.')
    
    regions = Region.objects.all()
    return render(request, 'calculator/calculator.html', {'regions': regions})

def api_regions(request):
    """API: 지역 목록 (AJAX용)"""
    regions = Region.objects.all()
    data = []
    for region in regions:
        avg_rating = region.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        data.append({
            'id': region.id,
            'name': region.name,
            'traffic_score': region.traffic_score,
            'education_score': region.education_score,
            'cost_level': region.cost_level,
            'avg_rating': round(avg_rating, 1),
            'review_count': region.reviews.count(),
        })
    return JsonResponse({'regions': data})

def privacy_policy(request):
    """개인정보 처리 정책 페이지"""
    return render(request, 'main/privacy_policy.html')

def terms_of_service(request):
    """이용약관 페이지"""
    return render(request, 'main/terms_of_service.html')

@login_required
def my_page(request):
    """마이페이지 - 사용자 정보 및 선호도 관리"""
    user = request.user
    try:
        preferences = UserPreference.objects.get(user=user)
    except UserPreference.DoesNotExist:
        preferences = None
    
    # 사용자 리뷰 목록
    user_reviews = Review.objects.filter(user=user).order_by('-created_at')[:5]
    
    # 사용자 비교 목록
    user_comparisons = Comparison.objects.filter(user=user).order_by('-created_at')[:5]
    
    context = {
        'user': user,
        'preferences': preferences,
        'user_reviews': user_reviews,
        'user_comparisons': user_comparisons,
    }
    return render(request, 'main/my_page.html', context)

