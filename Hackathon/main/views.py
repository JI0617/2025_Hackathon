from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
import json
from regions.models import Region, News
from users.models import UserPreference
from reviews.models import Review
from comparisons.models import Comparison
from .forms import UserRegistrationForm, UserPreferenceForm, ReviewForm, ComparisonForm, SearchForm, AdvancedSearchForm, SavedSearchForm
from .models import SavedSearch

def home(request):
    """메인 홈페이지 - 추천 지역 표시"""
    # 로그인한 사용자의 경우 개인화 추천, 그렇지 않으면 일반 추천
    if request.user.is_authenticated:
        try:
            preference = request.user.userpreference
            regions = Region.objects.all()
            
            # 선호도 기반 점수 계산
            scored_regions = []
            for region in regions:
                score = 0
                score += region.traffic_score * preference.traffic_importance
                score += region.education_score * preference.education_importance
                score += region.medical_score * preference.medical_importance
                
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
            recommended_regions = [region for region, score in scored_regions[:12]]
            
        except UserPreference.DoesNotExist:
            recommended_regions = Region.objects.all()[:12]
    else:
        recommended_regions = Region.objects.all()[:12]
    
    # 추천 정책 (최신 6개)
    from policies.models import Policy
    recommended_policies = Policy.objects.filter(
        is_active=True,
        is_featured=True
    ).order_by('-priority', '-created_at')[:6]
    
    # 통계 정보
    total_regions_count = Region.objects.count()
    total_reviews_count = Review.objects.count()
    
    context = {
        'regions': recommended_regions,
        'recommended_policies': recommended_policies,
        'total_regions_count': total_regions_count,
        'total_reviews_count': total_reviews_count,
    }
    return render(request, 'main/home.html', context)

def region_detail(request, name):
    """지역 상세 페이지 - 리뷰 포함"""
    region = get_object_or_404(Region, name=name)
    reviews = region.reviews.all()
    
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
            return redirect('home')
    else:
        form = UserPreferenceForm(instance=preference)
    
    return render(request, 'users/preferences.html', {'form': form})


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
    
    # 비교 데이터 준비 - 각 지역에 리뷰 정보 추가
    comparison_data = []
    for region in regions:
        region.review_count = region.reviews.count()
        comparison_data.append(region)
    
    return render(request, 'comparisons/comparison_detail.html', {
        'comparison': comparison,
        'comparison_data': comparison_data
    })

def policy(request):
    """정책 및 업데이트"""
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


def api_regions(request):
    """API: 지역 목록 (AJAX용)"""
    regions = Region.objects.all()
    data = []
    for region in regions:
        data.append({
            'id': region.id,
            'name': region.name,
            'traffic_score': region.traffic_score,
            'education_score': region.education_score,
            'cost_level': region.cost_level,
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

def api_realtime_news(request):
    """실시간 뉴스 API"""
    # 최근 24시간 내의 실시간 뉴스
    since = timezone.now() - timedelta(hours=24)
    news = News.objects.filter(
        published_at__gte=since,
        is_realtime=True
    ).order_by('-priority', '-published_at')[:10]
    
    data = []
    for item in news:
        data.append({
            'id': item.id,
            'title': item.title,
            'content': item.content[:200] + '...' if len(item.content) > 200 else item.content,
            'region': item.region.name,
            'category': item.category,
            'published_at': item.published_at.isoformat(),
            'source_url': item.source_url,
            'priority': item.priority,
        })
    
    return JsonResponse({
        'news': data,
        'count': len(data),
        'last_updated': timezone.now().isoformat()
    })

def api_realtime_stats(request):
    """실시간 통계 API"""
    # 최근 24시간 내의 활동 통계
    since = timezone.now() - timedelta(hours=24)
    
    stats = {
        'new_reviews': Review.objects.filter(created_at__gte=since).count(),
        'new_comparisons': Comparison.objects.filter(created_at__gte=since).count(),
        'new_news': News.objects.filter(published_at__gte=since).count(),
        'total_regions': Region.objects.count(),
        'total_reviews': Review.objects.count(),
        'total_comparisons': Comparison.objects.count(),
        'last_updated': timezone.now().isoformat()
    }
    
    return JsonResponse(stats)

def api_region_updates(request, region_id):
    """특정 지역의 실시간 업데이트 API"""
    region = get_object_or_404(Region, id=region_id)
    
    # 최근 7일간의 업데이트
    since = timezone.now() - timedelta(days=7)
    
    updates = {
        'region': {
            'id': region.id,
            'name': region.name,
            'city': region.city,
        },
        'recent_news': [],
        'recent_reviews': [],
        'score_changes': {
            'traffic_score': region.traffic_score,
            'education_score': region.education_score,
            'medical_score': region.medical_score,
            'cost_level': region.cost_level,
        },
        'last_updated': timezone.now().isoformat()
    }
    
    # 최근 뉴스
    news = region.news.filter(published_at__gte=since).order_by('-published_at')[:5]
    for item in news:
        updates['recent_news'].append({
            'id': item.id,
            'title': item.title,
            'category': item.category,
            'published_at': item.published_at.isoformat(),
            'is_realtime': item.is_realtime,
        })
    
    # 최근 리뷰
    reviews = region.reviews.filter(created_at__gte=since).order_by('-created_at')[:5]
    for review in reviews:
        updates['recent_reviews'].append({
            'id': review.id,
            'comment': review.comment[:100] + '...' if len(review.comment) > 100 else review.comment,
            'created_at': review.created_at.isoformat(),
            'user': review.user.username if review.user else '익명',
        })
    
    return JsonResponse(updates)

def advanced_search(request):
    """고급 검색 페이지"""
    form = AdvancedSearchForm(request.GET)
    regions = Region.objects.all()
    
    if form.is_valid():
        # 기본 검색 조건
        search_query = form.cleaned_data.get('search_query')
        city = form.cleaned_data.get('city')
        cost_level = form.cleaned_data.get('cost_level')
        
        if search_query:
            regions = regions.filter(name__icontains=search_query)
        if city:
            regions = regions.filter(city=city)
        if cost_level:
            regions = regions.filter(cost_level=cost_level)
        
        # 점수 범위 필터
        traffic_range = form.cleaned_data.get('traffic_range')
        if traffic_range:
            min_traffic, max_traffic = map(int, traffic_range.split('-'))
            regions = regions.filter(traffic_score__gte=min_traffic, traffic_score__lte=max_traffic)
        
        education_range = form.cleaned_data.get('education_range')
        if education_range:
            min_education, max_education = map(int, education_range.split('-'))
            regions = regions.filter(education_score__gte=min_education, education_score__lte=max_education)
        
        medical_range = form.cleaned_data.get('medical_range')
        if medical_range:
            min_medical, max_medical = map(int, medical_range.split('-'))
            regions = regions.filter(medical_score__gte=min_medical, medical_score__lte=max_medical)
        
        # 인구수 범위 필터
        population_range = form.cleaned_data.get('population_range')
        if population_range:
            min_pop, max_pop = map(int, population_range.split('-'))
            regions = regions.filter(population__gte=min_pop, population__lte=max_pop)
        
        # 면적 범위 필터
        area_range = form.cleaned_data.get('area_range')
        if area_range:
            min_area, max_area = map(int, area_range.split('-'))
            regions = regions.filter(area__gte=min_area, area__lte=max_area)
        
        # 리뷰 필터
        has_reviews = form.cleaned_data.get('has_reviews')
        if has_reviews:
            regions = regions.filter(reviews__isnull=False).distinct()
        
        # 평점 필터 제거됨
        
        # 정렬
        sort_by = form.cleaned_data.get('sort_by')
        if sort_by:
            regions = regions.order_by(sort_by)
        else:
            regions = regions.order_by('name')
    
    # 페이지네이션
    paginator = Paginator(regions, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 저장된 검색 조건들
    saved_searches = []
    if request.user.is_authenticated:
        saved_searches = SavedSearch.objects.filter(user=request.user)[:5]
    
    context = {
        'form': form,
        'regions': page_obj,
        'saved_searches': saved_searches,
        'total_regions': regions.count(),
    }
    
    return render(request, 'main/advanced_search.html', context)

@login_required
def save_search(request):
    """검색 조건 저장"""
    if request.method == 'POST':
        form = SavedSearchForm(request.POST)
        if form.is_valid():
            saved_search = form.save(commit=False)
            saved_search.user = request.user
            saved_search.save_search_params(request.GET)
            saved_search.save()
            messages.success(request, '검색 조건이 저장되었습니다.')
            return redirect('advanced_search')
    return redirect('advanced_search')

@login_required
def load_saved_search(request, search_id):
    """저장된 검색 조건 로드"""
    try:
        saved_search = SavedSearch.objects.get(id=search_id, user=request.user)
        # 저장된 검색 조건을 URL 파라미터로 변환하여 리다이렉트
        search_url = saved_search.get_search_url()
        return redirect(f'/advanced-search/?{search_url}')
    except SavedSearch.DoesNotExist:
        messages.error(request, '저장된 검색 조건을 찾을 수 없습니다.')
        return redirect('advanced_search')

@login_required
def delete_saved_search(request, search_id):
    """저장된 검색 조건 삭제"""
    try:
        saved_search = SavedSearch.objects.get(id=search_id, user=request.user)
        saved_search.delete()
        messages.success(request, '검색 조건이 삭제되었습니다.')
    except SavedSearch.DoesNotExist:
        messages.error(request, '저장된 검색 조건을 찾을 수 없습니다.')
    return redirect('advanced_search')

