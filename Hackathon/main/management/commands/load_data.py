import csv
import os
from django.core.management.base import BaseCommand
from regions.models import Region
from decimal import Decimal
from django.conf import settings

# CSV 파일 경로 설정: settings.BASE_DIR는 프로젝트 루트를 가리킵니다.
csv_file_path = os.path.join(settings.BASE_DIR, '통합_테이블.csv')

# 헤더 매핑 (CSV 헤더 이름: 모델 필드 이름)
header_map = {
    '지역명': 'name',
    '의료 평균접근성': 'medical_accessibility',
    '학생수': 'student_count',
    '교원수': 'teacher_count',
    '교원 1인당 학생수': 'students_per_teacher',
    '보증금(만원)': 'deposit_manwon',
    '월세금(만원)': 'monthly_rent_manwon',
    '종합월부담': 'total_monthly_burden',
    '종합부담등급': 'total_burden_grade',
    '의료 등급': 'medical_grade',
    '교육 인프라 등급': 'education_infra_grade',
    '월세등급': 'monthly_rent_grade',
    'summary': 'summary',
    '인구수': 'population',
    '면적': 'area',
}

class Command(BaseCommand):
    help = 'Loads region data from the final integrated CSV file into the Region model.'

    def handle(self, *args, **options):
        self.stdout.write("데이터 로딩 시작...")

        # 1. 기존 데이터 삭제
        try:
            count, _ = Region.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'기존 Region 데이터 {count}개 모두 삭제 완료.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"기존 데이터 삭제 중 오류 발생: {e}"))
            return

        # 2. 새로운 데이터 로딩 (CSV 중복 처리 및 인코딩/공백 제거 강화)
        try:
            with open(csv_file_path, 'r', encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                
                unique_regions_data = {}
                
                for row in reader:
                    data = {}
                    current_region_name = None

                    for csv_header, model_field in header_map.items():
                        value = row.get(csv_header, '')
                        if isinstance(value, str) and (value.lower() == 'nan' or value.strip() == ''):
                            value = ''

                        if model_field == 'name':
                            current_region_name = value.strip()
                            data[model_field] = current_region_name or None

                        elif model_field in ['student_count', 'teacher_count', 'population']:
                            # 빈값 -> None, 숫자 문자열 -> int
                            try:
                                data[model_field] = int(float(value)) if value != '' else None
                            except Exception:
                                data[model_field] = None
                                
                        elif model_field in ['medical_accessibility', 'students_per_teacher']:
                            try:
                                data[model_field] = float(value) if value != '' else None
                            except Exception:
                                data[model_field] = None
                                
                        elif model_field == 'area':
                            # 면적: 빈값 -> None. 값이 크면 m^2로 추정하여 km^2로 변환
                            try:
                                if value != '':
                                    area_val = float(value)
                                    # 만약 값이 매우 크면 m^2 단위로 들어왔을 가능성 -> km^2로 변환
                                    if area_val > 1_000_000:  # 임계값: 1,000,000 m^2 = 1 km^2
                                        area_val = area_val / 1_000_000.0
                                    data[model_field] = area_val
                                else:
                                    data[model_field] = None
                            except Exception:
                                data[model_field] = None
                                
                        elif model_field in ['deposit_manwon', 'monthly_rent_manwon', 'total_monthly_burden']:
                            try:
                                clean_value = str(value).replace(',', '').strip()
                                data[model_field] = Decimal(clean_value) if clean_value != '' else None
                            except Exception:
                                data[model_field] = None
                        
                        else:
                            data[model_field] = value.strip() if isinstance(value, str) and value.strip() != '' else None
                    
                    if current_region_name:
                        unique_regions_data[current_region_name] = data

                # 변환된 dict에서 Region 객체 생성 (필드에 None 허용)
                regions_to_create = [Region(**data) for data in unique_regions_data.values()]
                
                Region.objects.bulk_create(regions_to_create)
                
                total_rows_read = len(unique_regions_data) + (reader.line_num - 1 - len(unique_regions_data))
                duplicate_count = total_rows_read - len(unique_regions_data)
                
                self.stdout.write(self.style.WARNING(f'CSV에서 중복된 지역 {duplicate_count}개를 자동으로 제외했습니다. (총 {total_rows_read}개 중)'))
                self.stdout.write(self.style.SUCCESS(f"✅ {len(regions_to_create)}개의 지역 데이터가 성공적으로 저장되었습니다."))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"❌ 오류: 파일을 찾을 수 없습니다. 경로를 확인하세요: {csv_file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ 데이터 로딩 중 오류 발생: {e}"))
            # self.stdout.write(self.style.ERROR(f"마지막 처리된 데이터: {data}"))