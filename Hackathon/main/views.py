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

# --- NameError를 해결할 필수 모델 임포트 ---
from regions.models import Region
from users.models import UserPreference
from reviews.models import Review
from comparisons.models import Comparison

# News 모델은 policy/api 함수에서 사용되지만, 일단 NameError가 난 함수들을 위해 주석 처리합니다.
# 만약 News 관련 API 함수(api_realtime_news 등)를 다시 사용하려면 아래 import를 추가해야 합니다.
# from news.models import News # News 모델이 news 앱에 있다고 가정

from .forms import UserRegistrationForm, UserPreferenceForm, ReviewForm, ComparisonForm, SearchForm, AdvancedSearchForm, SavedSearchForm
from .models import SavedSearch
# ----------------------------------------

# --- 등급을 점수로 변환하는 헬퍼 함수 ---
def get_grade_score(grade):
    """등급('상', '중', '하')을 점수(100, 50, 0)로 변환"""
    if grade == '상':
        return 100
    elif grade == '중':
        return 50
    elif grade == '하':
        return 0
    return 0

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
                
                # 1. 교육 점수 계산: education_score 대신 education_infra_grade 사용
                education_score = get_grade_score(region.education_infra_grade)
                score += education_score * preference.education_importance
                
                # 2. 의료 점수 계산: medical_score 대신 medical_grade 사용
                medical_score = get_grade_score(region.medical_grade)
                score += medical_score * preference.medical_importance
                
                # 3. 비용 선호도 반영 (cost_level 대신 total_burden_grade 사용)
                # '상'이 부담 높음, '하'가 부담 낮음
                region_cost_grade = region.total_burden_grade 
                preferred_level = preference.preferred_cost_level # 가정: '낮음', '보통', '높음' 중 하나

                cost_score = 0
                
                # 비용 선호도 매칭 로직 (선호도에 따라 부담 등급을 매칭하여 점수 부여)
                if preferred_level == '낮음':
                    if region_cost_grade == '하': cost_score = 100
                    elif region_cost_grade == '중': cost_score = 70
                    elif region_cost_grade == '상': cost_score = 30
                elif preferred_level == '보통':
                    if region_cost_grade == '중': cost_score = 100
                    elif region_cost_grade in ['하', '상']: cost_score = 50
                elif preferred_level == '높음':
                    if region_cost_grade == '상': cost_score = 100
                    elif region_cost_grade == '중': cost_score = 70
                    elif region_cost_grade == '하': cost_score = 30
                
                score += cost_score * preference.cost_importance
                scored_regions.append((region, score))
            
            # 점수순 정렬
            scored_regions.sort(key=lambda x: x[1], reverse=True)
            recommended_regions = [region for region, score in scored_regions[:12]]
            
        except UserPreference.DoesNotExist:
            # 선호도 설정이 없으면 전체 지역 중 상위 12개
            recommended_regions = Region.objects.all()[:12]
    else:
        # 비로그인 사용자는 전체 지역 중 상위 12개
        recommended_regions = Region.objects.all()[:12]
    
    # 통계 정보
    total_regions_count = Region.objects.count()
    total_reviews_count = Review.objects.count()
    
    context = {
        'regions': recommended_regions,
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
def add_review(request, name):
    """리뷰 추가"""
    region = get_object_or_404(Region, name=name) 
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # 기존 리뷰가 있으면 업데이트, 없으면 새로 생성
            from reviews.models import Review as ReviewModel
            existing = ReviewModel.objects.filter(user=request.user, region=region).first()
            if existing:
                existing.rating = form.cleaned_data.get('rating')
                existing.comment = form.cleaned_data.get('comment')
                existing.save()
                messages.success(request, '기존 리뷰가 업데이트되었습니다.')
                return redirect('review_detail', review_id=existing.id)
            else:
                review = form.save(commit=False)
                review.user = request.user
                review.region = region
                review.save()
                messages.success(request, '리뷰가 성공적으로 등록되었습니다!')
                return redirect('review_detail', review_id=review.id)
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
    
    # 시/도(시도)별로 그룹화된 지역 데이터
    # Region.name typically contains the full name like '강원특별자치도 춘천시 ...'
    # We'll take the first token as the 시도 (province) and group by that.
    all_regions = Region.objects.all().order_by('name')
    grouped_regions = {}
    for region in all_regions:
        # split name and take first token as province; fallback to '기타'
        parts = str(region.name).split()
        province = parts[0] if parts else '기타'
        grouped_regions.setdefault(province, []).append(region)
    # convert to list of tuples (province, count) sorted by group size desc for template convenience
    regions_by_city = sorted([(province, len(regs)) for province, regs in grouped_regions.items()], key=lambda x: x[1], reverse=True)
    
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
        avg_rating = region.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        region.avg_rating = round(avg_rating, 1)
        region.review_count = region.reviews.count()
        comparison_data.append(region)
    
    return render(request, 'comparisons/comparison_detail.html', {
        'comparison': comparison,
        'comparison_data': comparison_data
    })

# def policy(request):
#     """정책 및 업데이트"""
#     featured_news = News.objects.filter(is_featured=True).order_by('-published_at')[:3]
#     all_news = News.objects.all().order_by('-published_at')
    
#     # 페이지네이션
#     paginator = Paginator(all_news, 10)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
    
#     return render(request, 'regions/news.html', {
#         'featured_news': featured_news,
#         'news_list': page_obj
#     })


def api_regions(request):
    """API: 지역 목록 (AJAX용)"""
    regions = Region.objects.all()
    data = []
    for region in regions:
        avg_rating = region.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        data.append({
            'id': region.id,
            'name': region.name,
            'education_grade': region.education_infra_grade, # score 대신 grade 사용
            'medical_grade': region.medical_grade,
            'cost_grade': region.total_burden_grade, # cost_level 대신 grade 사용
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


def calculator(request):
    """간단한 생활비 계산기 페이지(템플릿 렌더링용)"""
    # 기본적으로 모델 데이터는 사용하지 않는 간단한 페이지입니다.
    return render(request, 'main/calculator.html')

# def api_realtime_news(request):
#     """실시간 뉴스 API"""
#     # 최근 24시간 내의 실시간 뉴스
#     since = timezone.now() - timedelta(hours=24)
#     news = News.objects.filter(
#         published_at__gte=since,
#         is_realtime=True
#     ).order_by('-priority', '-published_at')[:10]
    
#     data = []
#     for item in news:
#         data.append({
#             'id': item.id,
#             'title': item.title,
#             'content': item.content[:200] + '...' if len(item.content) > 200 else item.content,
#             'region': item.region.name,
#             'category': item.category,
#             'published_at': item.published_at.isoformat(),
#             'source_url': item.source_url,
#             'priority': item.priority,
#         })
    
#     return JsonResponse({
#         'news': data,
#         'count': len(data),
#         'last_updated': timezone.now().isoformat()
#     })

# def api_realtime_stats(request):
#     """실시간 통계 API"""
#     # 최근 24시간 내의 활동 통계
#     since = timezone.now() - timedelta(hours=24)
    
#     stats = {
#         'new_reviews': Review.objects.filter(created_at__gte=since).count(),
#         'new_comparisons': Comparison.objects.filter(created_at__gte=since).count(),
#         'new_news': News.objects.filter(published_at__gte=since).count(),
#         'total_regions': Region.objects.count(),
#         'total_reviews': Review.objects.count(),
#         'total_comparisons': Comparison.objects.count(),
#         'last_updated': timezone.now().isoformat()
#     }
    
#     return JsonResponse(stats)

def api_region_updates(request, region_id):
    """특정 지역의 실시간 업데이트 API"""
    region = get_object_or_404(Region, id=region_id)
    
    # 최근 7일간의 업데이트
    since = timezone.now() - timedelta(days=7)
    
    updates = {
        'region': {
            'id': region.id,
            'name': region.name,
        },
        'recent_news': [],
        'recent_reviews': [],
        'score_changes': {
            'education_grade': region.education_infra_grade,
            'medical_grade': region.medical_grade,
            'cost_grade': region.total_burden_grade,
        },
        'last_updated': timezone.now().isoformat()
    }
    
    # # 최근 뉴스
    # news = region.news.filter(published_at__gte=since).order_by('-published_at')[:5]
    # for item in news:
    #     updates['recent_news'].append({
    #         'id': item.id,
    #         'title': item.title,
    #         'category': item.category,
    #         'published_at': item.published_at.isoformat(),
    #         'is_realtime': item.is_realtime,
    #     })
    
    # 최근 리뷰
    reviews = region.reviews.filter(created_at__gte=since).order_by('-created_at')[:5]
    for review in reviews:
        updates['recent_reviews'].append({
            'id': review.id,
            'rating': review.rating,
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
        # city = form.cleaned_data.get('city') # CSV에 city 필드는 없으므로 주석 처리
        cost_level = form.cleaned_data.get('cost_level') # UserPreference의 preferred_cost_level과 매칭되는 '낮음/보통/높음'일 경우
        
        if search_query:
            regions = regions.filter(name__icontains=search_query)
        # if city:
        #     regions = regions.filter(city=city)
            
        if cost_level:
            # preferred_cost_level이 '낮음', '보통', '높음'일 경우, 이를 종합부담등급 '하', '중', '상'에 매핑하여 필터링
            cost_grade_map = {'낮음': '하', '보통': '중', '높음': '상'}
            target_grade = cost_grade_map.get(cost_level)
            if target_grade:
                 regions = regions.filter(total_burden_grade=target_grade)
        
        # # 점수 범위 필터
        # traffic_range = form.cleaned_data.get('traffic_range')
        # if traffic_range:
        #     min_traffic, max_traffic = map(int, traffic_range.split('-'))
        #     regions = regions.filter(traffic_score__gte=min_traffic, traffic_score__lte=max_traffic)
        
        # education_range = form.cleaned_data.get('education_range')
        # if education_range:
        #     min_education, max_education = map(int, education_range.split('-'))
        #     regions = regions.filter(education_score__gte=min_education, education_score__lte=max_education)
        
        # medical_range = form.cleaned_data.get('medical_range')
        # if medical_range:
        #     min_medical, max_medical = map(int, medical_range.split('-'))
        #     regions = regions.filter(medical_score__gte=min_medical, medical_score__lte=max_medical)
        
        # # 인구수 범위 필터
        # population_range = form.cleaned_data.get('population_range')
        # if population_range:
        #     min_pop, max_pop = map(int, population_range.split('-'))
        #     regions = regions.filter(population__gte=min_pop, population__lte=max_pop)
        
        # # 면적 범위 필터
        # area_range = form.cleaned_data.get('area_range')
        # if area_range:
        #     min_area, max_area = map(int, area_range.split('-'))
        #     regions = regions.filter(area__gte=min_area, area__lte=max_area)
        
        # 리뷰 필터
        has_reviews = form.cleaned_data.get('has_reviews')
        if has_reviews:
            regions = regions.filter(reviews__isnull=False).distinct()
        
        min_rating = form.cleaned_data.get('min_rating')
        if min_rating:
            regions = regions.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__gte=float(min_rating))
        
        # 정렬
        sort_by = form.cleaned_data.get('sort_by')
        if sort_by:
            if sort_by == 'name':
                sort_by = 'name'
            # 없는 필드에 대한 정렬을 피하기 위해 필드 이름을 확인해야 합니다.
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

