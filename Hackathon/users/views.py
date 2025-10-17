from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from regions.models import Region
from .models import UserPreference

# Create your views here.

@login_required
def recommendations(request):
    """개인화 추천 페이지"""
    try:
        # 사용자 선호도 가져오기
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
        recommended_regions = [region for region, score in scored_regions[:6]]  # 상위 6개 추천
        
        return render(request, 'users/recommendations.html', {
            'recommended_regions': recommended_regions
        })
        
    except UserPreference.DoesNotExist:
        messages.warning(request, '먼저 선호도를 설정해주세요.')
        return redirect('preferences')
    except Exception as e:
        messages.error(request, f'추천 시스템 오류가 발생했습니다: {str(e)}')
        return redirect('home') 