from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)
    city = models.CharField(max_length=50, default='충청북도', help_text='소속 시/도')
    traffic_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    education_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    medical_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=70, help_text='의료시설 점수')
    cost_level = models.CharField(max_length=20, choices=[
        ('매우낮음', '매우낮음'),
        ('낮음', '낮음'),
        ('보통', '보통'),
        ('높음', '높음'),
        ('매우높음', '매우높음'),
    ])
    population = models.IntegerField(default=0)
    area = models.FloatField(default=0.0)  # km²
    latitude = models.FloatField(default=36.5, help_text='위도')
    longitude = models.FloatField(default=127.5, help_text='경도')
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='news')
    published_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title
