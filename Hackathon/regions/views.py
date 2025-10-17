from django.shortcuts import render, get_object_or_404
from .models import Region, News

# Create your views here.
# Future region-specific views can be added here 

def region_detail(request, name):
    """지역 상세 페이지"""
    region = get_object_or_404(Region, name=name)
    return render(request, 'regions/detail.html', {'region': region})

def news(request):
    """뉴스 페이지"""
    news_list = News.objects.filter(is_featured=True).order_by('-published_at')[:10]
    return render(request, 'regions/news.html', {'news_list': news_list}) 