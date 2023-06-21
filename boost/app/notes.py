"""
Этот модуль содержит модели оценок документов и комментариев к ним.
"""

from django.conf import settings
from django.db import models

from app.models import Doc


User = settings.AUTH_USER_MODEL


class Like (models.Model):
    """
    Класс модели лайка.
    """
    objects = models.Manager()

    doc = models.ForeignKey(Doc, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        """
        Возвращает фразу "<автор> оценил документ <документ>"
        """
        return f'{self.author} оценил документ "{self.doc}"'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        Сохраняет лайк и делает проверку на наличие дизлайка.
        """
        dislike = Dislike.objects.filter(
            doc=self.doc, author=self.author
        )

        if dislike.exists():
            dislike.delete()

        super().save(force_insert=False, force_update=False, using=None, update_fields=None)


class Dislike (models.Model):
    """
    Класс модели дизлайка.
    """
    objects = models.Manager()

    doc = models.ForeignKey(Doc, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        Сохраняет дизлайк и делает проверку на наличие лайка.
        """
        like = Like.objects.filter(
            doc=self.doc, author=self.author
        )

        if like.exists():
            like.delete()

        super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def __str__(self):
        """
        Возвращает фразу "<автор> оценил документ <документ>"
        """
        return f'{self.author} оценил документ "{self.doc}"'


class Comment (models.Model):
    """
    Класс модели комментария.
    """
    objects = models.Manager()

    text = models.CharField(max_length=511)
    doc = models.ForeignKey(Doc, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        """
        Возвращает текст комментария.
        """
        return str(self.text)
