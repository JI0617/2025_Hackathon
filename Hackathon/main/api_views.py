from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from regions.models import Region
from users.models import UserPreference
import json

@csrf_exempt
@require_http_methods(["GET"])
def get_recommendations(request):
    """개인화 추천 API"""
    try:
        # Regions queryset
        regions = Region.objects.all()

        # Read optional query params (from modal) and fall back to saved preferences
        q = request.GET
        education_weight = int(q.get('education_weight')) if q.get('education_weight') else None
        medical_weight = int(q.get('medical_weight')) if q.get('medical_weight') else None
        cost_pref = q.get('cost_preference') or None
        city_pref = q.get('city_preference') or None
        min_score = int(q.get('min_score')) if q.get('min_score') else None

        try:
            saved_pref = request.user.userpreference if request.user.is_authenticated else None
        except Exception:
            saved_pref = None

        # 선호도 기반 점수 계산
        scored_regions = []
        for region in regions:
            score = 0
            ew = education_weight if education_weight is not None else (saved_pref.education_importance if saved_pref else 2)
            mw = medical_weight if medical_weight is not None else (saved_pref.medical_importance if saved_pref else 2)

            # assume region.education_score/medical_score are numeric
            score += (region.education_score or 0) * ew
            score += (region.medical_score or 0) * mw

            # 비용 선호도 반영 (map cost_pref to cost_score)
            pref_cost = cost_pref or (saved_pref.preferred_cost_level if saved_pref else None)
            cost_score = 0
            if pref_cost and region.cost_level:
                if pref_cost == region.cost_level:
                    cost_score = 100
                elif pref_cost == 'low' or pref_cost == '낮음':
                    if region.cost_level in ['매우낮음', '낮음']:
                        cost_score = 80
                elif pref_cost == 'medium' or pref_cost == '보통':
                    if region.cost_level == '보통':
                        cost_score = 100
                elif pref_cost == 'high' or pref_cost == '높음':
                    if region.cost_level in ['높음', '매우높음']:
                        cost_score = 80

            cost_importance = saved_pref.cost_importance if saved_pref else 2
            score += cost_score * cost_importance

            # City filter: if provided, deprioritize others (simple boost)
            if city_pref:
                if region.city == city_pref:
                    score += 50

            # Min score filter: skip regions below threshold
            if min_score:
                # compute a simple avg score approximate
                avg = 0
                cnt = 0
                if region.education_score:
                    avg += region.education_score; cnt += 1
                if region.medical_score:
                    avg += region.medical_score; cnt += 1
                if cnt > 0 and (avg / cnt) < min_score:
                    continue

            scored_regions.append((region, score))
        
        # 점수순 정렬
        scored_regions.sort(key=lambda x: x[1], reverse=True)
        recommended_regions = [region for region, score in scored_regions[:3]]  # 상위 6개 추천
        
        # JSON 응답 생성
        recommendations = []
        for region in recommended_regions:
            recommendations.append({
                'name': region.name,
                'city': region.city,
                'education_score': region.education_score,
                'medical_score': region.medical_score,
                'cost_level': region.cost_level,
                'population': region.population,
                'description': region.description,
                'image_url': getattr(region, 'image_url', ''),
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
