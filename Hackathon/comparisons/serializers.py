from rest_framework import serializers
from .models import Comparison
from regions.serializers import RegionSerializer

class ComparisonSerializer(serializers.ModelSerializer):
    regions = RegionSerializer(many=True, read_only=True)
    region_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        help_text="비교할 지역 ID 목록"
    )
    
    class Meta:
        model = Comparison
        fields = ['id', 'name', 'regions', 'region_ids', 'created_at']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        region_ids = validated_data.pop('region_ids', [])
        comparison = Comparison.objects.create(**validated_data)
        comparison.regions.set(region_ids)
        return comparison

    def update(self, instance, validated_data):
        region_ids = validated_data.pop('region_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if region_ids is not None:
            instance.regions.set(region_ids)
        
        return instance
