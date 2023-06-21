from django.db import models
from django.conf import settings
from app.tags import Study, Subject

# Create your models here.

User = settings.AUTH_USER_MODEL


class Doc (models.Model):
    objects = models.Manager()

    title = models.CharField(max_length=255)
    description = models.CharField(max_length=511, blank=True)

    link = models.URLField(max_length=255, unique=True)
    path = models.CharField(max_length=127)

    preview = models.ImageField(
        upload_to='media/',
        blank=False,
        default='media/default_images/default_document.png'
    )

    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)

    studies = models.ManyToManyField(Study)
    subjects = models.ManyToManyField(Subject)

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return self.title
