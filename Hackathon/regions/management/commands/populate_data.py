from django.core.management.base import BaseCommand
from django.db.models import Min, Max, F, ExpressionWrapper, DecimalField
from regions.models import Region
from decimal import Decimal
import csv
import os

class Command(BaseCommand):
    help = 'Populate Region table from 통합_테이블.csv and calculate 0-100 scores.'

    def calculate_scores(self):
        """
        데이터베이스에 저장된 모든 Region 데이터를 기반으로
        50-100점 스케일 점수를 계산하여 일괄 업데이트합니다.
        """
        self.stdout.write(self.style.SUCCESS("--- 2. 전체 데이터 기반 50-100점 스케일 계산 시작 ---"))

        # 1. 전체 데이터셋의 최소/최대값 조회 (Aggregation)
        stats = Region.objects.aggregate(
            min_med=Min('medical_accessibility'), max_med=Max('medical_accessibility'),
            min_edu=Min('students_per_teacher'), max_edu=Max('students_per_teacher'),
            min_cost=Min('total_monthly_burden'), max_cost=Max('total_monthly_burden')
        )
        
        # 2. 정규화 공식 적용을 위한 범위 정의
        med_range = Decimal(stats['max_med'] - stats['min_med'])
        med_min = Decimal(stats['min_med'])
        edu_range = Decimal(stats['max_edu'] - stats['min_edu'])
        edu_min = Decimal(stats['min_edu'])
        cost_range = Decimal(stats['max_cost'] - stats['min_cost'])
        cost_min = Decimal(stats['min_cost'])

        # 3. Django ORM Expression을 사용하여 점수 계산 및 일괄 업데이트
        
        # (A) 의료 점수: medical_accessibility(접근성)은 높을수록 점수가 높음
        if med_range > 0:
            # Score = 50 + 50 * ((X - Min) / Range)
            med_score_expr = 50 + 50 * ((F('medical_accessibility') - med_min) / med_range)
            Region.objects.update(
                medical_score=ExpressionWrapper(med_score_expr, output_field=DecimalField(max_digits=5, decimal_places=2))
            )
            self.stdout.write(self.style.SUCCESS("  > 의료 점수 계산 완료 (높을수록 좋음)."))
        
        # (B) 교육 점수: students_per_teacher(학생수)는 높을수록 점수가 높음
        # (원래는 낮을수록 좋지만, 요청에 따라 높을수록 좋도록 수정)
        if edu_range > 0:
            # Score = 50 + 50 * ((X - Min) / Range)
            edu_score_expr = 50 + 50 * ((F('students_per_teacher') - edu_min) / edu_range)
            Region.objects.update(
                education_score=ExpressionWrapper(edu_score_expr, output_field=DecimalField(max_digits=5, decimal_places=2))
            )
            self.stdout.write(self.style.SUCCESS("  > 교육 점수 계산 완료 (높을수록 좋음)."))
            
        # (C) 생활비 점수: total_monthly_burden(부담)은 낮을수록 점수가 높음 (역방향 유지)
        if cost_range > 0:
            # Score = 50 + 50 * (1 - ((X - Min) / Range))
            cost_score_expr = 50 + 50 * (1 - (F('total_monthly_burden') - cost_min) / cost_range)
            Region.objects.update(
                cost_score=ExpressionWrapper(cost_score_expr, output_field=DecimalField(max_digits=5, decimal_places=2))
            )
            self.stdout.write(self.style.SUCCESS("  > 생활비 점수 계산 완료 (낮을수록 좋음)."))
        
        self.stdout.write(self.style.SUCCESS("--- 50-100점 스케일 DB 업데이트 최종 완료. ---"))


    def handle(self, *args, **kwargs):
        # 1. 데이터 로드 및 초기 저장 (경로는 이전 요청 그대로 유지)
        csv_file_path = 'c:/Users/minky/Documents/workspace/Hackathon/2025_Hackathon/Hackathon/통합_테이블.csv'
        
        if not os.path.exists(csv_file_path):
             self.stdout.write(self.style.ERROR(f"CSV 파일을 찾을 수 없습니다: {csv_file_path}"))
             return

        self.stdout.write(self.style.SUCCESS('--- 1. CSV 데이터 로드 및 Region 모델 초기 저장 시작 ---'))
        Region.objects.all().delete() # 기존 데이터 초기화

        try:
            with open(csv_file_path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # CSV 헤더 확인 및 매핑
                REGION_NAME_KEY = '\ufeff지역명' if '\ufeff지역명' in reader.fieldnames else '지역명'
                
                for i, row in enumerate(reader):
                    # 데이터 타입 변환 및 모델 필드명과 CSV 컬럼명 매핑
                    Region.objects.create(
                        name=row[REGION_NAME_KEY],
                        medical_accessibility=float(row['의료 평균접근성']),
                        student_count=int(row['학생수']),
                        teacher_count=int(row['교원수']),
                        students_per_teacher=float(row['교원 1인당 학생수']),
                        deposit_manwon=Decimal(row['보증금(만원)']),
                        monthly_rent_manwon=Decimal(row['월세금(만원)']),
                        total_monthly_burden=Decimal(row['종합월부담']),
                        total_burden_grade=row['종합부담등급'],
                        medical_grade=row['의료 등급'],
                        education_infra_grade=row['교육 인프라 등급'],
                        monthly_rent_grade=row['월세등급'],
                        summary=row['summary']
                    )
                    if (i + 1) % 100 == 0:
                         self.stdout.write(f"  > {i + 1}개 지역 로드 완료...")

                self.stdout.write(self.style.SUCCESS(f"  > 총 {Region.objects.count()}개 지역 초기 로드 완료."))
                
        except KeyError as e:
            self.stdout.write(self.style.ERROR(f'KeyError: {e} - CSV 컬럼명을 확인해 주세요.'))
            self.stdout.write(f'CSV 컬럼명: {reader.fieldnames}')
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"데이터 로드 중 오류 발생: {e}"))
            return
            
        # 4. 데이터 로드가 완료된 후, 점수 계산 함수 실행
        self.calculate_scores()

# from django.core.management.base import BaseCommand
# import csv
# from regions.models import Region

# class Command(BaseCommand):
#     help = 'Populate Region table from 통합_테이블.csv'

#     def handle(self, *args, **kwargs):
#         with open('c:/Users/user/Documents/2025_Hackathon/Data/통합_테이블.csv', encoding='utf-8') as f:
#             reader = csv.DictReader(f)
#             print('CSV 컬럼명:', reader.fieldnames)
#             for row in reader:
#                 try:
#                     Region.objects.create(
#                         지역명=row['\ufeff지역명'],
#                         의료_평균접근성=row['의료 평균접근성'],
#                         학생수=row['학생수'],
#                         교원수=row['교원수'],
#                         교원_1인당_학생수=row['교원 1인당 학생수'],
#                         보증금_만원=row['보증금(만원)'],
#                         월세금_만원=row['월세금(만원)'],
#                         종합월부담=row['종합월부담'],
#                         종합부담등급=row['종합부담등급'],
#                         의료_등급=row['의료 등급'],
#                         교육_인프라_등급=row['교육 인프라 등급'],
#                         월세등급=row['월세등급'],
#                         summary=row['summary']
#                     )
#                 except KeyError as e:
#                     print(f'KeyError: {e}. row keys: {list(row.keys())}')
#                     raise
