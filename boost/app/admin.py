from django.contrib import admin
from .profile import Profile

# Register your models here.


@admin.register(Profile)
class ProfileAdmin (admin.ModelAdmin):
    list_display = ('user', 'avatar', )

