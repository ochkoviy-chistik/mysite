from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='media/', default='/static/edmond.jpeg')

    def __str__(self):
        return str(self.user)


@receiver(post_save, sender=User)
def profile_create_handler(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def profile_save_handler(sender, instance, **kwargs):
    instance.profile.save()
