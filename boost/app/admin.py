from django.contrib import admin

from app.models import Doc
from app.tags import Study, Subject
from app.notes import Like, Dislike, Comment


# Register your models here.


@admin.register(Doc)
class DocAdmin (admin.ModelAdmin):
    list_display = ['title', 'link', 'author']
    filter_horizontal = ['subjects', 'studies', ]


@admin.register(Subject)
class SubjectAdmin (admin.ModelAdmin):
    list_display = ['name', 'color']


@admin.register(Study)
class StudyAdmin (admin.ModelAdmin):
    list_display = ['level', 'color']


@admin.register(Like)
class LikeAdmin (admin.ModelAdmin):
    list_display = ['doc', 'author', ]


@admin.register(Dislike)
class DislikeAdmin (admin.ModelAdmin):
    list_display = ['doc', 'author', ]


@admin.register(Comment)
class CommentAdmin (admin.ModelAdmin):
    list_display = ['text', 'doc', 'author', ]
