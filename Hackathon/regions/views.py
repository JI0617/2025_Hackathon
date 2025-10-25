from django.shortcuts import get_object_or_404, render
from .models import Region
from django.db.models import Avg
# import ReviewForm from main app to reuse the form
from main.forms import ReviewForm

# Create your views here.
# Future region-specific views can be added here 

def region_detail(request, name):
    """지역 상세 페이지"""
    region = get_object_or_404(Region, name=name)
    # 리뷰 및 통계 정보 준비 (main.views.region_detail과 동일한 컨텍스트 제공)
    reviews = region.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    # 사용자 리뷰 작성 폼
    review_form = None
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        if not user_review:
            review_form = ReviewForm()

    # 안전한 표시용 필드 추가
    try:
        pop = int(region.population) if getattr(region, 'population', None) not in (None, '') else None
    except Exception:
        pop = None
    try:
        area = float(getattr(region, 'area', None)) if getattr(region, 'area', None) not in (None, '') else None
    except Exception:
        area = None

    region.population_display = f"{pop:,}명" if pop else None
    region.area_display = f"{area:.2f} km²" if area else None
    if pop and area and area > 0:
        region.density_display = f"{pop/area:.1f}명/km²"
    else:
        region.density_display = None

    context = {
        'region': region,
        'reviews': reviews[:5],  # 최근 5개 리뷰만 표시
        'avg_rating': round(avg_rating, 1),
        'review_count': reviews.count(),
        'review_form': review_form,
        'user_review': user_review,
    }
    return render(request, 'regions/detail.html', context)

# def news(request):
#     """뉴스 페이지"""
#     news_list = News.objects.filter(is_featured=True).order_by('-published_at')[:10]
#     return render(request, 'regions/news.html', {'news_list': news_list})