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
        # --- 필터링 전략 ---
        # 사용자 선호도를 바탕으로 등급(의료/교육/월세)을 매칭하여 후보군을 먼저 필터링합니다.
        # 등급은 '하' < '중' < '상' 순서로 가정합니다.
        def allowed_grades(preferred, importance):
            """preferred: '하'/'중'/'상', importance: 1(낮음)-3(높음)
            반환: 허용할 등급 집합. importance가 클수록 엄격(=작은 범위)
            """
            order = ['하', '중', '상']
            try:
                idx = order.index(preferred)
            except Exception:
                return set(order)
            # importance: 3 -> strict(only preferred), 2 -> preferred ±1, 1 -> all
            radius = 3 - int(preference.cost_importance) if False else (3 - int(importance))
            low = max(0, idx - radius)
            high = min(len(order) - 1, idx + radius)
            return set(order[low:high + 1])

        # cost preferred might be stored as '하'/'중'/'상' or '보통' etc. normalize
        pref_cost = preference.preferred_cost_level or ''
        # normalize possible synonyms
        if pref_cost == '보통':
            pref_cost = '중'

        med_allowed = allowed_grades(preferred=getattr(preference, 'medical_importance', 2) and '상', importance=preference.medical_importance)
        # Above is awkward because user doesn't pick a preferred_medical_grade; instead we interpret importance:
        # If importance==3 => require '상', importance==2 => allow '상','중', else allow all.
        if preference.medical_importance == 3:
            med_allowed = {'상'}
        elif preference.medical_importance == 2:
            med_allowed = {'상', '중'}
        else:
            med_allowed = {'상', '중', '하'}

        if preference.education_importance == 3:
            edu_allowed = {'상'}
        elif preference.education_importance == 2:
            edu_allowed = {'상', '중'}
        else:
            edu_allowed = {'상', '중', '하'}

        # monthly_rent_grade filtering based on preferred_cost_level and cost_importance
        grade_order = ['하', '중', '상']
        def allowed_cost_grades(pref, importance):
            if not pref or pref not in grade_order:
                return set(grade_order)
            idx = grade_order.index(pref)
            # importance 3 -> strict, 2 -> allow neighbor, 1 -> allow all
            radius = 3 - int(importance)
            low = max(0, idx - radius)
            high = min(len(grade_order) - 1, idx + radius)
            return set(grade_order[low:high+1])

        cost_allowed = allowed_cost_grades(pref_cost, preference.cost_importance)

        # 후보 필터링
        candidates = []
        for region in regions:
            r_med = getattr(region, 'medical_grade', None)
            r_edu = getattr(region, 'education_infra_grade', None)
            r_rent = getattr(region, 'monthly_rent_grade', None)

            # If grade fields are missing, keep the region (be permissive)
            if r_med and r_med not in med_allowed:
                continue
            if r_edu and r_edu not in edu_allowed:
                continue
            if r_rent and r_rent not in cost_allowed:
                continue
            candidates.append(region)

        # --- 점수 계산 ---
        scored_regions = []
        for region in candidates:
            # use numeric score fields (fall back to 0)
            try:
                edu_score = float(getattr(region, 'education_score') or 0)
            except Exception:
                edu_score = 0.0
            try:
                med_score = float(getattr(region, 'medical_score') or 0)
            except Exception:
                med_score = 0.0
            try:
                cost_score = float(getattr(region, 'cost_score') or 0)
            except Exception:
                cost_score = 0.0

            # weighted sum by importance (importance 1..3)
            score = (edu_score * preference.education_importance) + (med_score * preference.medical_importance) + (cost_score * preference.cost_importance)

            # small boost if exact grade matches preferred (optional)
            # education
            if getattr(region, 'education_infra_grade', None) == '상' and preference.education_importance == 3:
                score += 20
            if getattr(region, 'medical_grade', None) == '상' and preference.medical_importance == 3:
                score += 20

            scored_regions.append((region, score))

        # 정렬 및 상위 결과 선택
        scored_regions.sort(key=lambda x: x[1], reverse=True)
        recommended_regions = [region for region, score in scored_regions[:3]]
        
        return render(request, 'users/recommendations.html', {
            'recommended_regions': recommended_regions
        })
        
    except UserPreference.DoesNotExist:
        messages.warning(request, '먼저 선호도를 설정해주세요.')
        return redirect('preferences')
    except Exception as e:
        messages.error(request, f'추천 시스템 오류가 발생했습니다: {str(e)}')
        return redirect('home') 