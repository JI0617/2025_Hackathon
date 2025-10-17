from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from policies.models import Policy
from regions.models import Region

class Command(BaseCommand):
    help = 'Populate database with sample policy data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample policy data...')
        
        # Get admin user or create one
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            admin_user.set_password('admin')
            admin_user.save()
        
        # Get some regions
        regions = Region.objects.all()[:3]
        
        # Create sample policies
        policies_data = [
            {
                'title': '청년 주거 지원금',
                'content': '''청년층의 주거 안정을 위해 제공하는 지원금입니다.

지원 내용:
- 1인 가구: 월 20만원, 2년간 지원
- 2인 가구: 월 30만원, 2년간 지원
- 신혼부부: 월 40만원, 3년간 지원

신청 자격:
- 만 19세 이상 39세 이하 청년
- 월 소득 200만원 이하
- 해당 지역 거주 또는 이주 예정자

신청 방법:
온라인 신청 후 서류 제출 및 심사''',
                'summary': '청년층 주거비 지원을 위한 월 지원금 지급 정책',
                'category': 'youth',
                'region': regions[0] if regions else None,
                'target_age_min': 19,
                'target_age_max': 39,
                'target_income_max': 2000000,
                'support_amount': 200000,
                'support_period': '2년',
                'support_type': '월 지원금',
                'application_start': timezone.now(),
                'application_end': timezone.now() + timedelta(days=90),
                'application_url': 'https://example.com/youth-housing',
                'contact_info': '청년정책과 043-123-4567',
                'is_active': True,
                'is_featured': True,
                'priority': 10,
                'created_by': admin_user
            },
            {
                'title': '농촌 이주 지원금',
                'content': '''도시에서 농촌으로 이주하는 가구에 대한 지원금입니다.

지원 내용:
- 이주비: 300만원 (1회성)
- 정착 지원금: 월 50만원, 6개월간
- 주택 구입 지원: 최대 500만원

신청 자격:
- 농촌 이주 예정 가구
- 월 소득 400만원 이하
- 농업 관련 활동 계획서 제출

신청 방법:
온라인 신청 후 현장 방문 및 서류 제출''',
                'summary': '농촌 이주 가구를 위한 이주비 및 정착 지원금',
                'category': 'agriculture',
                'target_income_max': 4000000,
                'support_amount': 3000000,
                'support_period': '1회성 + 6개월',
                'support_type': '이주비 + 정착 지원금',
                'application_start': timezone.now(),
                'application_end': timezone.now() + timedelta(days=120),
                'application_url': 'https://example.com/rural-migration',
                'contact_info': '농업정책과 043-234-5678',
                'is_active': True,
                'is_featured': True,
                'priority': 9,
                'created_by': admin_user
            },
            {
                'title': '창업 지원금',
                'content': '''청년 창업자를 위한 창업 지원금입니다.

지원 내용:
- 창업 자금: 최대 1000만원
- 사업장 임대료 지원: 월 30만원, 1년간
- 멘토링 및 컨설팅 지원

신청 자격:
- 만 18세 이상 45세 이하
- 창업 6개월 이내 또는 창업 예정자
- 사업계획서 제출

신청 방법:
온라인 신청 후 발표 및 심사''',
                'summary': '청년 창업자를 위한 창업 자금 및 사업 지원',
                'category': 'business',
                'region': regions[1] if len(regions) > 1 else None,
                'target_age_min': 18,
                'target_age_max': 45,
                'support_amount': 10000000,
                'support_period': '1년',
                'support_type': '창업 자금 + 임대료 지원',
                'application_start': timezone.now(),
                'application_end': timezone.now() + timedelta(days=60),
                'application_url': 'https://example.com/startup-support',
                'contact_info': '창업정책과 043-345-6789',
                'is_active': True,
                'is_featured': True,
                'priority': 8,
                'created_by': admin_user
            },
            {
                'title': '교육비 지원',
                'content': '''저소득 가구 자녀의 교육비를 지원합니다.

지원 내용:
- 초등학생: 월 10만원
- 중학생: 월 15만원
- 고등학생: 월 20만원
- 대학생: 등록금 전액 지원

신청 자격:
- 기준중위소득 60% 이하 가구
- 해당 지역 거주자
- 재학 증명서 제출

신청 방법:
온라인 신청 후 소득 증명 서류 제출''',
                'summary': '저소득 가구 자녀의 교육비 지원 정책',
                'category': 'education',
                'region': regions[2] if len(regions) > 2 else None,
                'target_income_max': 2000000,
                'support_amount': 100000,
                'support_period': '학기별',
                'support_type': '교육비 지원',
                'application_start': timezone.now(),
                'application_end': timezone.now() + timedelta(days=30),
                'application_url': 'https://example.com/education-support',
                'contact_info': '교육정책과 043-456-7890',
                'is_active': True,
                'is_featured': False,
                'priority': 7,
                'created_by': admin_user
            },
            {
                'title': '의료비 지원',
                'content': '''중증질환자 및 저소득층의 의료비를 지원합니다.

지원 내용:
- 입원비: 본인부담금의 80% 지원
- 외래비: 본인부담금의 70% 지원
- 약값: 본인부담금의 50% 지원

신청 자격:
- 기준중위소득 80% 이하 가구
- 중증질환자 또는 만성질환자
- 의료비 부담이 큰 경우

신청 방법:
온라인 신청 후 의료비 영수증 제출''',
                'summary': '저소득층 및 중증질환자의 의료비 지원',
                'category': 'medical',
                'target_income_max': 3000000,
                'support_amount': 500000,
                'support_period': '연간',
                'support_type': '의료비 지원',
                'application_start': timezone.now(),
                'application_end': timezone.now() + timedelta(days=180),
                'application_url': 'https://example.com/medical-support',
                'contact_info': '의료정책과 043-567-8901',
                'is_active': True,
                'is_featured': False,
                'priority': 6,
                'created_by': admin_user
            },
            {
                'title': '교통비 지원',
                'content': '''대중교통 이용자에 대한 교통비 지원 정책입니다.

지원 내용:
- 버스 할인: 20% 할인
- 지하철 할인: 30% 할인
- 택시 할인: 10% 할인 (장애인, 노인)

신청 자격:
- 해당 지역 거주자
- 교통카드 발급 및 등록
- 연령 제한 없음

신청 방법:
교통카드 발급소 방문 신청''',
                'summary': '대중교통 이용자 교통비 할인 지원',
                'category': 'transportation',
                'support_amount': 50000,
                'support_period': '월간',
                'support_type': '교통비 할인',
                'application_start': timezone.now(),
                'application_end': timezone.now() + timedelta(days=365),
                'application_url': 'https://example.com/transport-support',
                'contact_info': '교통정책과 043-678-9012',
                'is_active': True,
                'is_featured': False,
                'priority': 5,
                'created_by': admin_user
            }
        ]
        
        for policy_data in policies_data:
            policy, created = Policy.objects.get_or_create(
                title=policy_data['title'],
                defaults=policy_data
            )
            if created:
                self.stdout.write(f'Created policy: {policy.title}')
            else:
                self.stdout.write(f'Policy already exists: {policy.title}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample policy data')
        )
