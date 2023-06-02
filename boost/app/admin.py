from django.contrib import admin

from .models import Doc
from .tags import Study, Subject


# Register your models here.


@admin.register(Doc)
class DocAdmin (admin.ModelAdmin):
    list_display = ['title', 'link', 'author']
    filter_horizontal = ['subjects', 'studies',]


@admin.register(Subject)
class SubjectAdmin (admin.ModelAdmin):
    list_display = ['name', 'color']


@admin.register(Study)
class StudyAdmin (admin.ModelAdmin):
    list_display = ['level', 'color']
