from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Notification(models.Model):
    for_user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=False
    )
    text = models.CharField(max_length=1000)
    datetime = models.DateTimeField(auto_now_add=True)
