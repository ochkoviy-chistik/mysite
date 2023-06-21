"""
Этот модуль содержит классы моделей,
при помощи которых можно администрировать сайт.
"""


from django.contrib import admin

from app.models import Doc
from app.third_party.tags import Study, Subject
from app.third_party.notes import Like, Dislike, Comment


# Register your models here.


@admin.register(Doc)
class DocAdmin (admin.ModelAdmin):
    """
    Класс для администрирования документов сайта.
    """
    list_display = ['title', 'link', 'author']
    filter_horizontal = ['subjects', 'studies', ]


@admin.register(Subject)
class SubjectAdmin (admin.ModelAdmin):
    """
    Класс для администрирования тегов предметов сайта.
    """
    list_display = ['name', 'color']


@admin.register(Study)
class StudyAdmin (admin.ModelAdmin):
    """
    Класс для администрирования тегов классов сайта.
    """
    list_display = ['level', 'color']


@admin.register(Like)
class LikeAdmin (admin.ModelAdmin):
    """
    Класс для администрирования лайков сайта.
    """
    list_display = ['doc', 'author', ]


@admin.register(Dislike)
class DislikeAdmin (admin.ModelAdmin):
    """
    Класс для администрирования дизлайков сайта.
    """
    list_display = ['doc', 'author', ]


@admin.register(Comment)
class CommentAdmin (admin.ModelAdmin):
    """
    Класс для администрирования комментариев сайта.
    """
    list_display = ['text', 'doc', 'author', ]
