"""
Модуль с моделями.
"""


from django.db import models
from django.conf import settings
from app.third_party.tags import Study, Subject

# Create your models here.

User = settings.AUTH_USER_MODEL


class Doc (models.Model):
    """
    Класс модели документа.
    """
    objects = models.Manager()

    title = models.CharField(max_length=255)
    description = models.CharField(max_length=511, blank=True)

    link = models.URLField(max_length=255, unique=True)
    path = models.CharField(max_length=127)

    preview = models.ImageField(
        upload_to=settings.PREVIEWS_UPLOAD_PATH,
        blank=False,
        default=settings.DEFAULT_PREVIEW
    )

    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)

    studies = models.ManyToManyField(Study)
    subjects = models.ManyToManyField(Subject)

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        """
        Выводит название документа.
        """
        return str(self.title)
