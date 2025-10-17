from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Policy
from regions.models import Region

def policy_list(request):
    """정책 목록 페이지"""
    # 필터링 옵션
    category_filter = request.GET.get('category', '')
    region_filter = request.GET.get('region', '')
    search_query = request.GET.get('search', '')
    application_open = request.GET.get('application_open', '')
    
    # 기본 쿼리셋 (활성화된 정책만)
    policies = Policy.objects.filter(is_active=True)
    
    # 필터링 적용
    if category_filter:
        policies = policies.filter(category=category_filter)
    
    if region_filter:
        policies = policies.filter(region_id=region_filter)
    
    if search_query:
        policies = policies.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(summary__icontains=search_query)
        )
    
    if application_open == 'true':
        # 신청 가능한 정책만 필터링
        from django.utils import timezone
        now = timezone.now()
        policies = policies.filter(
            application_start__lte=now,
            application_end__gte=now
        )
    
    # 정렬
    sort_by = request.GET.get('sort', '-priority')
    policies = policies.order_by(sort_by, '-created_at')
    
    # 페이지네이션
    paginator = Paginator(policies, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 카테고리별 통계
    category_stats = {}
    for category_code, category_name in Policy.CATEGORY_CHOICES:
        count = Policy.objects.filter(category=category_code, is_active=True).count()
        if count > 0:
            category_stats[category_code] = {
                'name': category_name,
                'count': count
            }
    
    context = {
        'page_obj': page_obj,
        'categories': Policy.CATEGORY_CHOICES,
        'regions': Region.objects.all().order_by('city', 'name'),
        'category_stats': category_stats,
        'current_filters': {
            'category': category_filter,
            'region': region_filter,
            'search': search_query,
            'application_open': application_open,
            'sort': sort_by
        }
    }
    
    return render(request, 'policies/policy_list.html', context)

def policy_detail(request, policy_id):
    """정책 상세 페이지"""
    policy = get_object_or_404(Policy, id=policy_id, is_active=True)
    
    # 관련 정책 (같은 카테고리)
    related_policies = Policy.objects.filter(
        category=policy.category,
        is_active=True
    ).exclude(id=policy_id).order_by('-priority', '-created_at')[:5]
    
    context = {
        'policy': policy,
        'related_policies': related_policies,
        'is_application_open': policy.is_application_open()
    }
    
    return render(request, 'policies/policy_detail.html', context)

def policy_category(request, category):
    """카테고리별 정책 목록"""
    if category not in dict(Policy.CATEGORY_CHOICES):
        messages.error(request, '존재하지 않는 카테고리입니다.')
        return redirect('policy_list')
    
    policies = Policy.objects.filter(
        category=category,
        is_active=True
    ).order_by('-priority', '-created_at')
    
    # 페이지네이션
    paginator = Paginator(policies, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    category_name = dict(Policy.CATEGORY_CHOICES)[category]
    
    context = {
        'page_obj': page_obj,
        'category': category,
        'category_name': category_name,
        'total_count': policies.count()
    }
    
    return render(request, 'policies/policy_category.html', context)

def policy_recommendations(request):
    """추천 정책 페이지"""
    # 추천 정책 (is_featured=True)
    featured_policies = Policy.objects.filter(
        is_featured=True,
        is_active=True
    ).order_by('-priority', '-created_at')[:10]
    
    # 카테고리별 최신 정책
    category_policies = {}
    for category_code, category_name in Policy.CATEGORY_CHOICES:
        policies = Policy.objects.filter(
            category=category_code,
            is_active=True
        ).order_by('-created_at')[:3]
        
        if policies.exists():
            category_policies[category_code] = {
                'name': category_name,
                'policies': policies
            }
    
    # 신청 마감 임박 정책
    from django.utils import timezone
    from datetime import timedelta
    
    deadline_soon = timezone.now() + timedelta(days=7)
    urgent_policies = Policy.objects.filter(
        is_active=True,
        application_end__lte=deadline_soon,
        application_end__gte=timezone.now()
    ).order_by('application_end')[:5]
    
    context = {
        'featured_policies': featured_policies,
        'category_policies': category_policies,
        'urgent_policies': urgent_policies
    }
    
    return render(request, 'policies/policy_recommendations.html', context)
