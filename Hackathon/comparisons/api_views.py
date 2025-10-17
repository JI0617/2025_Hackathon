from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Comparison
from .serializers import ComparisonSerializer

class ComparisonViewSet(viewsets.ModelViewSet):
    queryset = Comparison.objects.all()
    serializer_class = ComparisonSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Comparison.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_comparisons(self, request):
        """현재 사용자의 비교 목록 반환"""
        comparisons = Comparison.objects.filter(user=request.user)
        serializer = self.get_serializer(comparisons, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_region(self, request, pk=None):
        """비교에 지역 추가"""
        comparison = self.get_object()
        region_id = request.data.get('region_id')
        
        if not region_id:
            return Response({'error': 'region_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from regions.models import Region
            region = Region.objects.get(id=region_id)
            comparison.regions.add(region)
            return Response({'message': 'Region added successfully'})
        except Region.DoesNotExist:
            return Response({'error': 'Region not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def remove_region(self, request, pk=None):
        """비교에서 지역 제거"""
        comparison = self.get_object()
        region_id = request.data.get('region_id')
        
        if not region_id:
            return Response({'error': 'region_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from regions.models import Region
            region = Region.objects.get(id=region_id)
            comparison.regions.remove(region)
            return Response({'message': 'Region removed successfully'})
        except Region.DoesNotExist:
            return Response({'error': 'Region not found'}, status=status.HTTP_404_NOT_FOUND)
