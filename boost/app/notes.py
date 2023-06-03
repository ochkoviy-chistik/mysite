from django.db import models
from boost.settings import AUTH_USER_MODEL
from app.models import Doc

User = AUTH_USER_MODEL


class Like (models.Model):
    doc = models.ForeignKey(Doc, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.author} оценил документ "{self.doc}"'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        dislike = Dislike.objects.filter(
            doc=self.doc, author=self.author
        )

        if dislike.exists():
            dislike.delete()

        super().save(force_insert=False, force_update=False, using=None, update_fields=None)


class Dislike (models.Model):
    doc = models.ForeignKey(Doc, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        like = Like.objects.filter(
            doc=self.doc, author=self.author
        )

        if like.exists():
            like.delete()

        super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def __str__(self):
        return f'{self.author} оценил документ "{self.doc}"'
