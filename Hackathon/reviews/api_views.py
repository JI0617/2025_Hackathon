from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db import models
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['region', 'rating', 'user']
    search_fields = ['comment', 'user__username']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def by_region(self, request):
        """특정 지역의 리뷰들 반환"""
        region_id = request.query_params.get('region_id')
        if not region_id:
            return Response({'error': 'region_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        reviews = Review.objects.filter(region_id=region_id)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """리뷰 통계 정보 반환"""
        total_reviews = Review.objects.count()
        avg_rating = Review.objects.aggregate(avg_rating=models.Avg('rating'))['avg_rating'] or 0
        
        rating_counts = {}
        for i in range(1, 6):
            rating_counts[str(i)] = Review.objects.filter(rating=i).count()
        
        return Response({
            'total_reviews': total_reviews,
            'average_rating': round(avg_rating, 2),
            'rating_distribution': rating_counts
        })

    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """현재 사용자의 리뷰들 반환"""
        reviews = Review.objects.filter(user=request.user)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
