from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from regions.models import Region

def calculator_view(request):
    """계산기 뷰"""
    # 모든 지역 데이터를 가져와서 템플릿에 전달
    regions = Region.objects.all().order_by('city', 'name')
    cities = Region.objects.values_list('city', flat=True).distinct().order_by('city')
    
    context = {
        'regions': regions,
        'cities': cities,
    }
    return render(request, 'calculator/calculator.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def calculate_cost(request):
    """생활비 계산 API"""
    try:
        data = json.loads(request.body)
        region_id = data.get('region_id')
        monthly_income = float(data.get('monthly_income', 0))
        family_size = int(data.get('family_size', 1))
        
        if not region_id:
            return JsonResponse({'error': '지역을 선택해주세요.'}, status=400)
        
        try:
            region = Region.objects.get(id=region_id)
        except Region.DoesNotExist:
            return JsonResponse({'error': '선택한 지역을 찾을 수 없습니다.'}, status=404)
        
        # 기본 생활비 계산 (지역별 비용 수준 기반)
        cost_multipliers = {
            '매우낮음': 0.7,
            '낮음': 0.85,
            '보통': 1.0,
            '높음': 1.2,
            '매우높음': 1.4
        }
        
        base_cost = 2000000  # 기본 월 생활비 (200만원)
        multiplier = cost_multipliers.get(region.cost_level, 1.0)
        family_multiplier = 1 + (family_size - 1) * 0.6  # 가족 수에 따른 배수
        
        estimated_monthly_cost = base_cost * multiplier * family_multiplier
        
        # 세부 항목별 비용 계산
        rent_cost = estimated_monthly_cost * 0.4  # 주거비 40%
        food_cost = estimated_monthly_cost * 0.25  # 식비 25%
        transport_cost = estimated_monthly_cost * 0.15  # 교통비 15%
        utility_cost = estimated_monthly_cost * 0.1  # 공과금 10%
        other_cost = estimated_monthly_cost * 0.1  # 기타 10%
        
        # 수입 대비 비용 비율
        cost_ratio = (estimated_monthly_cost / monthly_income * 100) if monthly_income > 0 else 0
        
        # 추천 여부
        recommendation = "적정" if cost_ratio <= 50 else "부담" if cost_ratio <= 70 else "부담스러움"
        
        result = {
            'region_name': region.name,
            'city': region.city,
            'cost_level': region.cost_level,
            'monthly_income': monthly_income,
            'family_size': family_size,
            'estimated_monthly_cost': round(estimated_monthly_cost),
            'breakdown': {
                'rent': round(rent_cost),
                'food': round(food_cost),
                'transport': round(transport_cost),
                'utility': round(utility_cost),
                'other': round(other_cost)
            },
            'cost_ratio': round(cost_ratio, 1),
            'recommendation': recommendation,
            'traffic_score': region.traffic_score,
            'education_score': region.education_score,
            'medical_score': region.medical_score
        }
        
        return JsonResponse(result)
        
    except (ValueError, KeyError) as e:
        return JsonResponse({'error': '잘못된 입력 데이터입니다.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': '계산 중 오류가 발생했습니다.'}, status=500) 