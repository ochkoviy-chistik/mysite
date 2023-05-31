from django.contrib import admin

from .models import Doc


# Register your models here.


@admin.register(Doc)
class DocAdmin (admin.ModelAdmin):
    list_display = ['title', 'link', 'author']
