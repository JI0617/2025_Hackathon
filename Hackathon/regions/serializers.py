from rest_framework import serializers
from .models import Region

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'city', 'traffic_score', 'education_score', 
                 'medical_score', 'cost_level', 'population', 'area', 
                 'description', 'latitude', 'longitude']
