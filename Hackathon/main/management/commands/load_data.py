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
}

class Command(BaseCommand):
    help = 'Loads region data from the 통합_테이블.csv file into the Region model.'

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
            # ⭐ 수정 1: 인코딩을 'utf-8-sig'로 변경하고 newline='' 옵션 유지 ⭐
            with open(csv_file_path, 'r', encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                
                # 딕셔너리를 사용하여 region_name을 키로 중복을 방지합니다.
                unique_regions_data = {}
                
                for row in reader:
                    data = {}
                    current_region_name = None # 현재 행의 region_name을 저장할 변수

                    for csv_header, model_field in header_map.items():
                        value = row.get(csv_header, '')

                        # 데이터 유형 변환
                        if model_field == 'name':
                            # ⭐ 수정 2 (핵심): region_name 값에서 양쪽의 모든 공백/제어 문자 제거 ⭐
                            # .strip()을 통해 보이지 않는 \r, \n, 공백 등을 제거하여 고유성을 보장합니다.
                            current_region_name = value.strip()
                            data[model_field] = current_region_name
                            
                        elif model_field in ['student_count', 'teacher_count']:
                            data[model_field] = int(float(value)) if value and value.replace('.', '', 1).isdigit() else 0
                        elif model_field in ['medical_accessibility', 'students_per_teacher']:
                            data[model_field] = float(value) if value and value.replace('.', '', 1).isdigit() else 0.0
                        elif model_field in ['deposit_manwon', 'monthly_rent_manwon', 'total_monthly_burden']:
                            try:
                                data[model_field] = Decimal(value) if value else Decimal('0.00')
                            except:
                                data[model_field] = Decimal('0.00')
                        else:
                            data[model_field] = value
                    
                    # region_name을 키로 사용하여 저장: 중복이 있으면 덮어쓰여 유일성 보장
                    if current_region_name:
                        unique_regions_data[current_region_name] = data

                # 딕셔너리의 값(데이터)을 Region 객체로 변환
                regions_to_create = [Region(**data) for data in unique_regions_data.values()]
                
                # Bulk Create 실행
                Region.objects.bulk_create(regions_to_create)
                
                total_rows_read = len(unique_regions_data) + (reader.line_num - 1 - len(unique_regions_data))
                duplicate_count = total_rows_read - len(unique_regions_data)
                
                self.stdout.write(self.style.WARNING(f'CSV에서 중복된 지역 {duplicate_count}개를 자동으로 제외했습니다. (총 {total_rows_read}개 중)'))
                self.stdout.write(self.style.SUCCESS(f"✅ {len(regions_to_create)}개의 지역 데이터가 성공적으로 저장되었습니다."))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"❌ 오류: 파일을 찾을 수 없습니다. 경로를 확인하세요: {csv_file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ 데이터 로딩 중 오류 발생: {e}"))