from django.db import models
from django.contrib.auth.models import User

class Comparison(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="비교 이름")
    regions = models.ManyToManyField('regions.Region')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}의 {self.name} 비교"
