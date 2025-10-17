from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
import json
from .models import Comparison
from regions.models import Region

@login_required
def comparison_list(request):
    """비교 목록 페이지"""
    comparisons = Comparison.objects.filter(user=request.user).order_by('-created_at')
    
    # 페이지네이션
    paginator = Paginator(comparisons, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj
    }
    
    return render(request, 'comparisons/comparison_list.html', context)

@login_required
def comparison_detail(request, comparison_id):
    """비교 상세 페이지"""
    comparison = get_object_or_404(Comparison, id=comparison_id, user=request.user)
    regions = comparison.regions.all()
    
    # 비교 데이터 준비
    comparison_data = []
    for region in regions:
        region_data = {
            'id': region.id,
            'name': region.name, 
            'city': region.city, # city 필드가 모델에 없다면 이 줄은 이후에 오류를 일으킬 수 있습니다.
            'education_score': region.education_score,
            'medical_score': region.medical_score,
            'cost_level': region.cost_level,
            'population': region.population,
            'area': region.area,
            'description': region.description,
            'latitude': region.latitude,
            'longitude': region.longitude
        }
        comparison_data.append(region_data)
    
    # 통계 계산
    if comparison_data:
        # 데이터베이스에 없는 필드(traffic_score, education_score, medical_score 등)는
        # 이전에 데이터를 로드한 CSV 파일에는 없었으므로, 이 부분을 사용하는 템플릿/뷰에서
        # 오류가 발생할 수 있습니다. 여기서는 코드를 그대로 유지합니다.
        # 모델 필드 목록: comparison, deposit_manwon, education_infra_grade, id, medical_accessibility, medical_grade, monthly_rent_grade, monthly_rent_manwon, region_name, reviews, student_count, students_per_teacher, summary, teacher_count, total_burden_grade, total_monthly_burden
        education_scores = [r.get('education_score', 0) for r in comparison_data]
        medical_scores = [r.get('medical_score', 0) for r in comparison_data]
        
        # 0이 아닌 유효한 점수를 가진 리스트로 재구성 (오류 방지)
        valid_education = [s for s in education_scores if s is not None and s != 0]
        valid_medical = [s for s in medical_scores if s is not None and s != 0]

        stats = {
            'education': {
                'min': min(valid_education) if valid_education else 0,
                'max': max(valid_education) if valid_education else 0,
                'avg': sum(valid_education) / len(valid_education) if valid_education else 0
            },
            'medical': {
                'min': min(valid_medical) if valid_medical else 0,
                'max': max(valid_medical) if valid_medical else 0,
                'avg': sum(valid_medical) / len(valid_medical) if valid_medical else 0
            }
        }
    else:
        stats = None
    
    context = {
        'comparison': comparison,
        'regions': regions,
        'comparison_data': comparison_data,
        'stats': stats
    }
    
    return render(request, 'comparisons/comparison_detail.html', context)

@login_required
def create_comparison(request):
    """비교 생성 페이지"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        region_ids = request.POST.getlist('regions')
        
        if not name:
            messages.error(request, '비교 이름을 입력해주세요.')
        elif len(region_ids) < 2:
            messages.error(request, '최소 2개 이상의 지역을 선택해주세요.')
        elif len(region_ids) > 5:
            messages.error(request, '최대 5개까지만 비교할 수 있습니다.')
        else:
            try:
                comparison = Comparison.objects.create(
                    user=request.user,
                    name=name
                )
                comparison.regions.set(region_ids)
                messages.success(request, '비교가 성공적으로 생성되었습니다.')
                return redirect('comparison_detail', comparison_id=comparison.id)
            except Exception as e:
                messages.error(request, f'비교 생성 중 오류가 발생했습니다: {str(e)}')
    
    # 모든 지역 목록
    regions = Region.objects.all().order_by('name')
    
    context = {
        'regions': regions
    }
    
    return render(request, 'comparisons/create_comparison.html', context)

@login_required
def edit_comparison(request, comparison_id):
    """비교 수정 페이지"""
    comparison = get_object_or_404(Comparison, id=comparison_id, user=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        region_ids = request.POST.getlist('regions')
        
        if not name:
            messages.error(request, '비교 이름을 입력해주세요.')
        elif len(region_ids) < 2:
            messages.error(request, '최소 2개 이상의 지역을 선택해주세요.')
        elif len(region_ids) > 5:
            messages.error(request, '최대 5개까지만 비교할 수 있습니다.')
        else:
            try:
                comparison.name = name
                comparison.save()
                comparison.regions.set(region_ids)
                messages.success(request, '비교가 성공적으로 수정되었습니다.')
                return redirect('comparison_detail', comparison_id=comparison.id)
            except Exception as e:
                messages.error(request, f'비교 수정 중 오류가 발생했습니다: {str(e)}')
    
    # 모든 지역 목록
    regions = Region.objects.all().order_by('name')
    selected_regions = comparison.regions.all()
    
    context = {
        'comparison': comparison,
        'regions': regions,
        'selected_regions': selected_regions
    }
    
    return render(request, 'comparisons/edit_comparison.html', context)

@login_required
def delete_comparison(request, comparison_id):
    """비교 삭제"""
    comparison = get_object_or_404(Comparison, id=comparison_id, user=request.user)
    
    if request.method == 'POST':
        comparison.delete()
        messages.success(request, '비교가 삭제되었습니다.')
        return redirect('comparison_list')
    
    context = {
        'comparison': comparison
    }
    
    return render(request, 'comparisons/delete_comparison.html', context)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def add_region_to_comparison(request, comparison_id):
    """비교에 지역 추가 (AJAX)"""
    try:
        comparison = get_object_or_404(Comparison, id=comparison_id, user=request.user)
        data = json.loads(request.body)
        region_id = data.get('region_id')
        
        if not region_id:
            return JsonResponse({'error': '지역 ID가 필요합니다.'}, status=400)
        
        if comparison.regions.count() >= 5:
            return JsonResponse({'error': '최대 5개까지만 비교할 수 있습니다.'}, status=400)
        
        region = get_object_or_404(Region, id=region_id)
        comparison.regions.add(region)
        
        return JsonResponse({
            'message': '지역이 추가되었습니다.',
            'region': {
                'id': region.id,
                'name': region.name, 
                'city': region.city # city 필드가 모델에 없다면 이 줄은 이후에 오류를 일으킬 수 있습니다.
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def remove_region_from_comparison(request, comparison_id):
    """비교에서 지역 제거 (AJAX)"""
    try:
        comparison = get_object_or_404(Comparison, id=comparison_id, user=request.user)
        data = json.loads(request.body)
        region_id = data.get('region_id')
        
        if not region_id:
            return JsonResponse({'error': '지역 ID가 필요합니다.'}, status=400)
        
        if comparison.regions.count() <= 2:
            return JsonResponse({'error': '최소 2개 이상의 지역이 필요합니다.'}, status=400)
        
        region = get_object_or_404(Region, id=region_id)
        comparison.regions.remove(region)
        
        return JsonResponse({
            'message': '지역이 제거되었습니다.',
            'region_id': region_id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def quick_compare(request):
    """빠른 비교 페이지"""
    if request.method == 'POST':
        region_ids = request.POST.getlist('regions')
        
        if len(region_ids) < 2:
            messages.error(request, '최소 2개 이상의 지역을 선택해주세요.')
        elif len(region_ids) > 5:
            messages.error(request, '최대 5개까지만 비교할 수 있습니다.')
        else:
            # 임시 비교 데이터 생성
            comparison_data = []
            for region in regions:
                region_data = {
                    'id': region.id,
                    'name': region.name, # 템플릿이 region.name을 사용하도록 매핑
                    
                    # ⭐ 추가/수정된 실제 필드 (템플릿에서 사용될 키) ⭐
                    'medical_accessibility': region.medical_accessibility, # 의료 접근성
                    'students_per_teacher': region.students_per_teacher,   # 교원당 학생수
                    'total_monthly_burden': region.total_monthly_burden,   # 종합 월부담
                    'monthly_rent_grade': region.monthly_rent_grade,       # 월세 등급
                    'student_count': region.student_count,                 # 학생수
                    'deposit_manwon': region.deposit_manwon,               # 보증금
                }
                comparison_data.append(region_data)
            
            context = {
                'regions': regions,
                'comparison_data': comparison_data,
                'is_quick_compare': True
            }
            
            return render(request, 'comparisons/quick_compare.html', context)
    
    # 모든 지역 목록
    regions = Region.objects.all().order_by('name')
    
    context = {
        'regions': regions
    }
    
    return render(request, 'comparisons/quick_compare.html', context)