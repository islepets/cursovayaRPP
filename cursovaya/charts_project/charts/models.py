from django.contrib.auth.models import User
from django.db import models

class Graph(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    x_value = models.FloatField()
    image = models.ImageField(upload_to='graphs/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Graph by {self.user.username} at {self.created_at}"

    class Meta:
        verbose_name = 'Граф'
        verbose_name_plural = 'Графы'

        