from django.db import models
from boost import settings
import datetime
from .tags import Study, Subject

# Create your models here.

User = settings.AUTH_USER_MODEL


class Doc (models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField(max_length=255, unique=True)
    path = models.CharField(max_length=127)
    description = models.CharField(max_length=511, blank=True)
    preview = models.ImageField(
        upload_to='media/',
        blank=False,
        default='media/default_images/default_document.png'
    )
    studies = models.ManyToManyField(Study)
    subjects = models.ManyToManyField(Subject)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return self.title
