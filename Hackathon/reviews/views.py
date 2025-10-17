from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
import json
from .models import Review
from regions.models import Region

def review_list(request):
    """리뷰 목록 페이지"""
    # 필터링 옵션
    region_filter = request.GET.get('region', '')
    search_query = request.GET.get('search', '')
    
    # 기본 쿼리셋
    reviews = Review.objects.select_related('user', 'region').all()
    
    # 필터링 적용
    if region_filter:
        reviews = reviews.filter(region__name__icontains=region_filter)
    
    if search_query:
        reviews = reviews.filter(
            Q(comment__icontains=search_query) | 
            Q(region__name__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    # 정렬
    sort_by = request.GET.get('sort', '-created_at')
    reviews = reviews.order_by(sort_by)
    
    # 페이지네이션
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 통계 정보
    stats = {
        'total_reviews': Review.objects.count(),
    }
    
    # 인기 지역 (리뷰 수 기준)
    popular_regions = Region.objects.annotate(
        review_count=Count('reviews')
    ).filter(review_count__gt=0).order_by('-review_count')[:5]
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'popular_regions': popular_regions,
        'regions': Region.objects.all().order_by('name'),
        'current_filters': {
            'region': region_filter,
            'search': search_query,
            'sort': sort_by
        }
    }
    
    return render(request, 'reviews/review_list.html', context)

def review_detail(request, review_id):
    """리뷰 상세 페이지"""
    review = get_object_or_404(Review, id=review_id)
    
    # 관련 리뷰 (같은 지역)
    related_reviews = Review.objects.filter(
        region=review.region
    ).exclude(id=review_id).order_by('-created_at')[:5]
    
    context = {
        'review': review,
        'related_reviews': related_reviews
    }
    
    return render(request, 'reviews/review_detail.html', context)

@login_required
def create_review(request, region_id):
    """리뷰 작성 페이지"""
    region = get_object_or_404(Region, id=region_id)
    
    # 이미 리뷰를 작성했는지 확인
    existing_review = Review.objects.filter(user=request.user, region=region).first()
    if existing_review:
        messages.warning(request, '이미 이 지역에 대한 리뷰를 작성하셨습니다.')
        return redirect('review_detail', review_id=existing_review.id)
    
    if request.method == 'POST':
        comment = request.POST.get('comment', '').strip()
        
        if not comment:
            messages.error(request, '댓글을 입력해주세요.')
        else:
            try:
                review = Review.objects.create(
                    user=request.user,
                    region=region,
                    comment=comment
                )
                messages.success(request, '리뷰가 성공적으로 작성되었습니다.')
                return redirect('review_detail', review_id=review.id)
            except Exception as e:
                messages.error(request, f'리뷰 작성 중 오류가 발생했습니다: {str(e)}')
    
    context = {
        'region': region
    }
    
    return render(request, 'reviews/create_review.html', context)

@login_required
def edit_review(request, review_id):
    """리뷰 수정 페이지"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        comment = request.POST.get('comment', '').strip()
        
        if not comment:
            messages.error(request, '댓글을 입력해주세요.')
        else:
            try:
                review.comment = comment
                review.save()
                messages.success(request, '리뷰가 성공적으로 수정되었습니다.')
                return redirect('review_detail', review_id=review.id)
            except Exception as e:
                messages.error(request, f'리뷰 수정 중 오류가 발생했습니다: {str(e)}')
    
    context = {
        'review': review
    }
    
    return render(request, 'reviews/edit_review.html', context)

@login_required
def delete_review(request, review_id):
    """리뷰 삭제"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, '리뷰가 삭제되었습니다.')
        return redirect('review_list')
    
    context = {
        'review': review
    }
    
    return render(request, 'reviews/delete_review.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def like_review(request, review_id):
    """리뷰 좋아요 (AJAX)"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': '로그인이 필요합니다.'}, status=401)
    
    try:
        review = get_object_or_404(Review, id=review_id)
        # 좋아요 기능은 추후 구현
        return JsonResponse({'message': '좋아요 기능은 준비 중입니다.'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def region_reviews(request, region_id):
    """특정 지역의 리뷰 목록"""
    region = get_object_or_404(Region, id=region_id)
    reviews = Review.objects.filter(region=region).order_by('-created_at')
    
    # 페이지네이션
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 지역 통계
    region_stats = {
        'total_reviews': reviews.count(),
    }
    
    context = {
        'region': region,
        'page_obj': page_obj,
        'region_stats': region_stats
    }
    
    return render(request, 'reviews/region_reviews.html', context)