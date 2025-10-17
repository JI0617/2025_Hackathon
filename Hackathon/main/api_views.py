from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from regions.models import Region
from users.models import UserPreference
import json

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_recommendations(request):
    """개인화 추천 API"""
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
        
        # JSON 응답 생성
        recommendations = []
        for region in recommended_regions:
            recommendations.append({
                'name': region.name,
                'city': region.city,
                'traffic_score': region.traffic_score,
                'education_score': region.education_score,
                'cost_level': region.cost_level,
                'population': region.population,
                'description': region.description,
                'image_url': region.image_url,
            })
        
        return JsonResponse({
            'success': True,
            'recommendations': recommendations
        })
        
    except UserPreference.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '선호도가 설정되지 않았습니다.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'추천 시스템 오류: {str(e)}'
        })
