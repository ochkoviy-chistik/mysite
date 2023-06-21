from django.db import models


class Subject (models.Model):
    objects = models.Manager()

    name = models.CharField(max_length=31, unique=True)
    color = models.CharField(max_length=7, unique=True)

    def __str__(self):
        return str(self.name)


class Study (models.Model):
    objects = models.Manager()

    level = models.CharField(max_length=15, unique=True)
    color = models.CharField(max_length=7, unique=True)

    def __str__(self):
        return str(self.level)
