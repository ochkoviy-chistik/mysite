from django.db import models
from boost import settings
import datetime

# Create your models here.

User = settings.AUTH_USER_MODEL


class Doc (models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField(max_length=255, unique=True)
    description = models.CharField(max_length=511, blank=True)
    preview = models.ImageField(
        upload_to='media/',
        blank=False,
        default='media/default_images/default_document.png'
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
