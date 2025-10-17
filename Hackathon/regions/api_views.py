from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Region
from .serializers import RegionSerializer

class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'cost_level']
    search_fields = ['name', 'city', 'description']
    ordering_fields = ['education_score', 'medical_score', 'population']
    ordering = ['-education_score']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """지역 통계 정보 반환"""
        total_regions = Region.objects.count()
        cities = Region.objects.values_list('city', flat=True).distinct()
        city_counts = {}
        
        for city in cities:
            city_counts[city] = Region.objects.filter(city=city).count()
        
        return Response({
            'total_regions': total_regions,
            'city_counts': city_counts,
            'cost_levels': {
                '매우낮음': Region.objects.filter(cost_level='매우낮음').count(),
                '낮음': Region.objects.filter(cost_level='낮음').count(),
                '보통': Region.objects.filter(cost_level='보통').count(),
                '높음': Region.objects.filter(cost_level='높음').count(),
                '매우높음': Region.objects.filter(cost_level='매우높음').count(),
            }
        })

    @action(detail=False, methods=['get'])
    def top_regions(self, request):
        """상위 지역들 반환"""
        limit = request.query_params.get('limit', 10)
        try:
            limit = int(limit)
        except ValueError:
            limit = 10
            
        regions = Region.objects.all().order_by('-education_score')[:limit]
        serializer = self.get_serializer(regions, many=True)
        return Response(serializer.data)
