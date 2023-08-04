"""
Модуль с моделями.
"""

import os
from io import BytesIO

from django.db import models
from django.conf import settings

from app.third_party.ImageManager import ImageManager
from app.third_party.disk_invoker import DiskInvoker, COMMANDS, unique_name_generator
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

    def __init__(self, *args, **kwargs):
        self.file = None
        super().__init__(*args, **kwargs)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None,
    ):
        if self.file is not None:
            path = settings.DISK_PATH + unique_name_generator()

            disk_invoker = DiskInvoker(token=settings.DISK_TOKEN)
            response_file = BytesIO(
                list(self.file)[0]
            )

            disk_invoker.run(COMMANDS.UPLOAD, path=path, file=response_file)
            disk_invoker.run(COMMANDS.PUBLISH, path=path)
            info = disk_invoker.run(COMMANDS.INFO, path=path)

            self.link = info['public_url']
            self.path = path

        super().save(force_insert, force_update, using, update_fields)

    def to_json(self):
        resp = {
            'title': self.title,
            'description': self.description,
            'link': self.link,
            'path': self.path,
            'preview': settings.API_DOMAIN + self.preview.url,
            'likes': self.likes,
            'dislikes': self.dislikes,
            'comments': self.comments,
            'tags': {
                'studies': [str(study) for study in self.studies.all()],
                'subjects': [str(subject) for subject in self.subjects.all()],
            },
            'author': self.author.username,
            'date': self.date
        }

        return resp

    def delete(self, using=None, keep_parents=False):
        disk_invoker = DiskInvoker(token=settings.DISK_TOKEN)
        disk_invoker.run(COMMANDS.DELETE, path=self.path)

        super().delete(using, keep_parents)

    def use_file(self, file):
        self.file = file

    def __str__(self):
        """
        Выводит название документа.
        """
        return str(self.title)
