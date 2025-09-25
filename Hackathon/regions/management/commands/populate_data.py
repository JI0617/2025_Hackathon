from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from regions.models import Region, News

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create sample regions
        regions_data = [
            {
                'name': '청주시',
                'traffic_score': 85,
                'education_score': 90,
                'cost_level': '보통',
                'population': 850000,
                'area': 940.0,
                'description': '충청북도의 도청 소재지로, 교통과 교육이 발달한 도시입니다. 중부권의 중심지로서 다양한 편의시설을 갖추고 있습니다.'
            },
            {
                'name': '충주시',
                'traffic_score': 70,
                'education_score': 80,
                'cost_level': '낮음',
                'population': 210000,
                'area': 983.0,
                'description': '자연환경이 우수하고 생활비가 저렴한 도시입니다. 교육환경도 양호하며, 주거하기 좋은 환경을 제공합니다.'
            },
            {
                'name': '제천시',
                'traffic_score': 65,
                'education_score': 75,
                'cost_level': '낮음',
                'population': 140000,
                'area': 882.0,
                'description': '자연과 도시가 조화를 이룬 도시로, 관광지로도 유명합니다. 생활비가 저렴하고 교육환경도 양호합니다.'
            },
            {
                'name': '보은군',
                'traffic_score': 50,
                'education_score': 60,
                'cost_level': '매우낮음',
                'population': 35000,
                'area': 584.0,
                'description': '자연환경이 우수하고 생활비가 매우 저렴한 지역입니다. 조용하고 평화로운 생활을 원하는 분들에게 적합합니다.'
            },
            {
                'name': '옥천군',
                'traffic_score': 60,
                'education_score': 70,
                'cost_level': '낮음',
                'population': 55000,
                'area': 537.0,
                'description': '충청북도 중부에 위치한 군으로, 교통이 비교적 편리하고 생활비가 저렴합니다.'
            },
            {
                'name': '영동군',
                'traffic_score': 55,
                'education_score': 65,
                'cost_level': '낮음',
                'population': 45000,
                'area': 845.0,
                'description': '자연환경이 우수하고 생활비가 저렴한 지역입니다. 조용한 생활을 원하는 분들에게 적합합니다.'
            },
            {
                'name': '증평군',
                'traffic_score': 75,
                'education_score': 85,
                'cost_level': '보통',
                'population': 35000,
                'area': 81.0,
                'description': '면적이 작지만 교통이 편리하고 교육환경이 우수한 지역입니다. 청주시와 인접해 있어 편의시설 이용이 용이합니다.'
            },
            {
                'name': '진천군',
                'traffic_score': 70,
                'education_score': 80,
                'cost_level': '낮음',
                'population': 65000,
                'area': 407.0,
                'description': '교통이 편리하고 교육환경이 양호한 지역입니다. 생활비도 저렴하여 주거하기 좋은 환경을 제공합니다.'
            },
            {
                'name': '괴산군',
                'traffic_score': 45,
                'education_score': 55,
                'cost_level': '매우낮음',
                'population': 35000,
                'area': 842.0,
                'description': '자연환경이 우수하고 생활비가 매우 저렴한 지역입니다. 조용하고 평화로운 생활을 원하는 분들에게 적합합니다.'
            },
            {
                'name': '음성군',
                'traffic_score': 65,
                'education_score': 75,
                'cost_level': '낮음',
                'population': 95000,
                'area': 520.0,
                'description': '교통이 비교적 편리하고 생활비가 저렴한 지역입니다. 교육환경도 양호하여 주거하기 좋은 환경을 제공합니다.'
            }
        ]
        
        for region_data in regions_data:
            region, created = Region.objects.get_or_create(
                name=region_data['name'],
                defaults=region_data
            )
            if created:
                self.stdout.write(f'Created region: {region.name}')
            else:
                self.stdout.write(f'Region already exists: {region.name}')
        
        # Create sample news
        news_data = [
            {
                'title': '청주시 교통 인프라 대폭 개선',
                'content': '청주시에서 교통 인프라 개선 사업이 본격적으로 시작되었습니다. 주요 도로 확장과 대중교통 시스템 개선으로 교통 편의성이 크게 향상될 것으로 예상됩니다.',
                'region': Region.objects.get(name='청주시'),
                'is_featured': True
            },
            {
                'title': '충주시 교육 시설 현대화 완료',
                'content': '충주시의 주요 교육 시설 현대화 사업이 완료되었습니다. 최신 교육 장비와 시설이 도입되어 교육 환경이 크게 개선되었습니다.',
                'region': Region.objects.get(name='충주시'),
                'is_featured': True
            },
            {
                'title': '제천시 관광 인프라 확충',
                'content': '제천시에서 관광 인프라 확충 사업이 진행 중입니다. 새로운 관광지 개발과 기존 시설 개선으로 관광객 유치가 증가할 것으로 예상됩니다.',
                'region': Region.objects.get(name='제천시'),
                'is_featured': True
            },
            {
                'title': '보은군 생활 환경 개선 사업',
                'content': '보은군에서 주민 생활 환경 개선 사업이 시작되었습니다. 도로 정비와 공원 조성 등으로 주민들의 삶의 질이 향상될 것으로 기대됩니다.',
                'region': Region.objects.get(name='보은군'),
                'is_featured': False
            },
            {
                'title': '옥천군 교통 편의성 향상',
                'content': '옥천군의 교통 편의성이 크게 향상되었습니다. 새로운 버스 노선 개설과 도로 정비로 주민들의 이동이 더욱 편리해졌습니다.',
                'region': Region.objects.get(name='옥천군'),
                'is_featured': False
            },
            {
                'title': '영동군 교육 환경 개선',
                'content': '영동군의 교육 환경이 개선되었습니다. 학교 시설 현대화와 교육 프로그램 확충으로 학생들의 학습 환경이 향상되었습니다.',
                'region': Region.objects.get(name='영동군'),
                'is_featured': False
            },
            {
                'title': '증평군 교통망 확충',
                'content': '증평군의 교통망이 확충되었습니다. 새로운 도로 개설과 대중교통 시스템 개선으로 교통 편의성이 크게 향상되었습니다.',
                'region': Region.objects.get(name='증평군'),
                'is_featured': False
            },
            {
                'title': '진천군 생활 편의시설 확충',
                'content': '진천군에 새로운 생활 편의시설들이 들어서고 있습니다. 상업시설과 문화시설 확충으로 주민들의 생활이 더욱 편리해졌습니다.',
                'region': Region.objects.get(name='진천군'),
                'is_featured': False
            },
            {
                'title': '괴산군 자연환경 보호 사업',
                'content': '괴산군에서 자연환경 보호 사업이 진행 중입니다. 생태계 보호와 자연 경관 개선으로 지역의 자연환경이 더욱 아름다워졌습니다.',
                'region': Region.objects.get(name='괴산군'),
                'is_featured': False
            },
            {
                'title': '음성군 주거 환경 개선',
                'content': '음성군의 주거 환경이 개선되었습니다. 주택 시설 현대화와 주거지 정비로 주민들의 삶의 질이 향상되었습니다.',
                'region': Region.objects.get(name='음성군'),
                'is_featured': False
            }
        ]
        
        for news_data_item in news_data:
            news, created = News.objects.get_or_create(
                title=news_data_item['title'],
                defaults=news_data_item
            )
            if created:
                self.stdout.write(f'Created news: {news.title}')
            else:
                self.stdout.write(f'News already exists: {news.title}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data')
        ) 